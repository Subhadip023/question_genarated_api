# 🔍 QMaster Performance Audit

> **Audited by:** Senior Developer Review  
> **Date:** 2026-10-05  
> **Scope:** Full-stack — FastAPI backend (`question_genarated_api`) + Next.js 16 frontend (`question_genartor_fontend`)

---

## 🚦 Summary

| Area | Severity | Impact |
|---|---|---|
| Auth middleware hits DB on **every request** | 🔴 Critical | All routes slowed by 1 extra DB round-trip |
| N+1 query in `history()` method | 🔴 Critical | 1 query per attempt → explodes with more users |
| `getAllQuestionsList` fetches everything in sequential loops | 🔴 Critical | Unbounded memory + network usage |
| Missing DB indexes on foreign keys | 🔴 Critical | Table scans on every join |
| Topics fetched with `staleTime: 60s` but never cached across pages | 🟠 High | Repeated API calls for static data |
| `list_public()` runs `joinedload` on full question tree just for topics | 🟠 High | Massive over-fetch on the student tests page |
| `_serialize_attempt()` does DB writes inside a GET handler | 🟠 High | Every read of a submitted attempt triggers a commit |
| Duplicate columns in `TestSeries` model | 🟡 Medium | Silent ORM mapping bugs |
| `next.config.ts` is empty — no image optimization or caching headers | 🟡 Medium | Images served without caching, no WebP |
| `react-quill-new` CSS imported in root layout | 🟡 Medium | Blocks initial render for all users on all pages |
| Frontend `staleTime` is global 60s — too aggressive for stable data | 🟡 Medium | Wasted network on topics, org lists |
| `debug: true` and full traceback exposed in production error handler | 🟡 Medium | Security risk + verbose logs in prod |
| Redis configured but never used | 🟡 Medium | Idle infrastructure that could eliminate DB hits |
| `list_public()` uses correlated `NOT EXISTS` subquery | 🟡 Medium | Runs once per row in test_series table |
| `attempt-runner.tsx` is a 1,243-line God component | 🟢 Low | Excessive re-renders, untestable, huge bundle chunk |

---

## 🔴 Critical Issues

### 1. Auth Middleware Queries the Database on Every Request

**File:** `app/middleware/auth_middleware.py` — Lines 38–47

```python
# CURRENT — opens a DB session and queries on EVERY authenticated request
db = SessionLocal()
try:
    user = db.query(User).filter(User.id == user_id).first()
```

**Why it is slow:** Every API call that carries a Bearer token opens a DB session, runs `SELECT * FROM users WHERE id = ?`, and closes the session — even though the JWT is already self-contained and verifiable without hitting the database.

**Fix — Option A (fastest): Embed the role in the JWT at login time and trust the claims:**

```python
# In auth_service.py — add role to token payload at login
def create_access_token(user_id: int, user_role: int) -> str:
    payload = {"sub": str(user_id), "role": str(user_role), ...}

# In auth_middleware.py — no DB query needed
claims = decode_access_token(token)
request.state.user_id = int(claims["sub"])
request.state.user_role = int(claims["role"])
```

**Fix — Option B: Cache the DB lookup in Redis (for real-time role revocation):**

```python
import redis
r = redis.from_url(settings.redis_url)

cache_key = f"user_role:{user_id}"
cached_role = r.get(cache_key)

if cached_role:
    request.state.user_role = int(cached_role)
else:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            r.setex(cache_key, 300, str(user.role))  # cache 5 minutes
            request.state.user_role = user.role
    finally:
        db.close()
```

---

### 2. N+1 Query in `history()` Method

**File:** `app/controllers/student_test_controller.py` — Lines 538–567

```python
# CURRENT — 1 extra DB query per attempt in the loop
for attempt in attempts:
    series = db.query(TestSeries).filter(TestSeries.id == attempt.series_id).first()  # N+1!
```

If a student has 20 attempts, this fires **21 SQL queries**. With 100 concurrent students viewing history, that is 2,100 queries for one endpoint.

**Fix — eager-load the series in a single query:**

```python
# Step 1: Add relationship to TestAttempt model
class TestAttempt(Base):
    series: Mapped["TestSeries"] = relationship("TestSeries", foreign_keys=[series_id])

# Step 2: Use joinedload in history()
attempts = (
    db.query(TestAttempt)
    .options(joinedload(TestAttempt.series))  # single JOIN — no loop queries
    .filter(TestAttempt.user_id == user_id)
    .order_by(TestAttempt.started_at.desc())
    .all()
)
for attempt in attempts:
    series = attempt.series  # already loaded, no extra query
```

**Result: 21 queries → 1 query.**

---

### 3. `getAllQuestionsList` — Unbounded Sequential API Loop

**File:** `app/services/questions.ts` — Lines 67–80

```typescript
// CURRENT — awaits each page one at a time, new array every iteration
do {
    const res = await getAllQuestions(page, 100);
    allItems = [...allItems, ...res.items];  // new array each loop
    page++;
} while (page <= totalPages);
```

Problems: sequential awaits, array copy on every iteration, no upper bound, nothing renders until all pages are downloaded.

**Fix — fetch all pages in parallel:**

```typescript
export async function getAllQuestionsList(): Promise<Question[]> {
    const client = await createApiClient();
    const first = await client.get<PaginatedQuestionResponse>(`questions/?page=1&page_size=100`);
    if (first.total_pages <= 1) return first.items;

    const rest = await Promise.all(
        Array.from({ length: first.total_pages - 1 }, (_, i) =>
            client.get<PaginatedQuestionResponse>(`questions/?page=${i + 2}&page_size=100`)
        )
    );
    return [first.items, ...rest.map(r => r.items)].flat();
}
```

**Better long-term:** Add a `GET /questions/simple-list` endpoint returning only `[{id, title}]` — tiny payload for dropdowns.

---

### 4. Missing Database Indexes on Foreign Keys

**Files:** All models in `app/models/`

MySQL does **not** auto-index foreign key columns. The following are queried constantly with no index:

| Table | Column | Used In |
|---|---|---|
| `questions` | `organization_id` | Every question visibility filter |
| `questions` | `user_id` | Teacher-scoped query filter |
| `questions` | `topic_id` | Topic filter on questions page |
| `test_attempts` | `series_id` | History, serialization |
| `test_attempts` | `user_id` | History, owned-attempt check |
| `test_attempts` | `status` | Filtering in-progress attempts |
| `attempt_questions` | `attempt_id` | Loaded on every attempt GET |
| `series_questions` | `series_id` | Loaded on every test detail |
| `test_access` | `test_series_id` | Student test discovery |
| `batch_student` | `student_id` | Access check for private tests |

**Fix:**

```python
# question.py
organization_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
user_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

# test_attempt.py
series_id: Mapped[int] = mapped_column(Integer, ForeignKey(...), nullable=False, index=True)
user_id: Mapped[int] = mapped_column(Integer, ForeignKey(...), nullable=False, index=True)
status: Mapped[str] = mapped_column(Integer, nullable=False, index=True)
```

Then run an Alembic migration:
```bash
alembic revision --autogenerate -m "add_missing_indexes"
alembic upgrade head
```

---

## 🟠 High Issues

### 5. `list_public()` Over-fetches the Entire Question Tree for Topic Names

**File:** `app/controllers/student_test_controller.py` — Lines 111–128

```python
# Loads full question Text content just to get topic names for the card
.options(
    joinedload(TestSeries.series_questions)
    .joinedload(SeriesQuestion.question)    # loads full question Text
    .joinedload(Question.topic)
)
```

Loads the full HTML `TEXT` of every question in every test series just to display topic tags on the listing card.

**Fix:** Use a targeted subquery that fetches only topic names:

```python
topic_subq = (
    db.query(SeriesQuestion.series_id, Topic.name.label("topic_name"))
    .join(Question, SeriesQuestion.question_id == Question.id)
    .join(Topic, Question.topic_id == Topic.id)
    .subquery()
)
```

Or denormalize: store `topic_ids` as a JSON column on `test_series` and update it on create/update.

---

### 6. `_serialize_attempt()` Writes to the Database Inside a GET Handler

**File:** `app/controllers/student_test_controller.py` — Lines 723–747

```python
# A GET endpoint commits score corrections on every call
if attempt.score != recalc_score or need_commit:
    attempt.score = recalc_score
    db.commit()   # DB write inside a read handler!
```

Adds a `COMMIT` to every GET of a submitted attempt. Causes lock contention, breaks read-replica patterns, errors swallowed silently.

**Fix:** Move all score recalculation into `submit()` and `_mark_expired()` only. `get_attempt()` should be a pure read.

---

### 7. Topics Use `staleTime: 60s` — Too Short for Static Data

Topics are reference data. A user navigating 10 pages over 15 minutes triggers 15 `GET /topics/` calls.

**Fix:**

```typescript
// lib/query/topics/use-topics.ts
export function useTopics(initialData?: Topic[]) {
    return useQuery({
        queryKey: topicKeys.all,
        queryFn: getAllTopics,
        initialData,
        staleTime: 10 * 60 * 1000,  // 10 minutes
        gcTime:    30 * 60 * 1000,
    });
}
```

---

## 🟡 Medium Issues

### 8. Duplicate Columns in `TestSeries` Model

**File:** `app/models/test_series.py`

`is_result_show` and `is_score_show` are declared **twice** (lines 35–36 and again lines 54–64). SQLAlchemy silently overwrites the first with the second.

**Fix:** Delete the second (duplicate) block at lines 54–64.

---

### 9. `react-quill-new` CSS in Root Layout Loaded on Every Page

**File:** `app/layout.tsx` — Line 18

```typescript
import "react-quill-new/dist/quill.snow.css";  // parsed on login, student tests, history...
```

**Fix:** Delete from `layout.tsx`. Import it only in the component or page that uses the editor.

---

### 10. `next.config.ts` Is Completely Empty

Add critical performance options:

```typescript
const nextConfig: NextConfig = {
  compress: true,
  images: {
    remotePatterns: [{ protocol: "https", hostname: "your-api-domain.com" }],
    formats: ["image/avif", "image/webp"],
  },
  async headers() {
    return [{
      source: "/api/backend/uploads/:path*",
      headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
    }];
  },
};
```

Without `Cache-Control`, diagram images re-download on every page visit.

---

### 11. Full Stack Traceback Exposed in API Responses

**File:** `main.py` — Line 71 and `app/config.py` — Line 19

```python
debug: bool = True          # hardcoded in config
content={"detail": str(exc), "traceback": tb}  # sent to client in prod!
```

Reveals file paths, SQL queries, and library versions.

**Fix:**

```python
return JSONResponse(
    status_code=500,
    content={
        "detail": str(exc) if settings.debug else "An internal error occurred.",
        **({"traceback": tb} if settings.debug else {}),
    },
)
```

Set `DEBUG=false` in the production `.env` file.

---

### 12. Redis Is Configured but Never Used

**File:** `app/config.py`

```python
redis_url: str = "redis://127.0.0.1:6379/0"  # exists but zero code uses it
```

**Quick wins with Redis (ordered by impact):**

| Cache Key | TTL | Eliminates |
|---|---|---|
| `user_role:{user_id}` | 5 min | DB query per API request (auth middleware) |
| `topics:{org_id}` | 10 min | Repeated `GET /topics/` calls |
| `test_list:{user_id}:{page}` | 30 sec | Expensive `list_public()` query |

---

### 13. `list_public()` Uses a Correlated `NOT EXISTS` Subquery

```python
# Runs once per row in test_series — 500 series = 500 sub-selects
~db.query(TestAttempt).filter(
    TestAttempt.series_id == TestSeries.id,
    TestAttempt.user_id == user_id,
).exists(),
```

**Fix — LEFT JOIN + IS NULL (index-friendly):**

```python
attempted_subq = (
    db.query(TestAttempt.series_id)
    .filter(TestAttempt.user_id == user_id)
    .subquery()
)
query = (
    query
    .outerjoin(attempted_subq, TestSeries.id == attempted_subq.c.series_id)
    .filter(attempted_subq.c.series_id.is_(None))
)
```

---

## 🟢 Low Issues

### 14. Array Spread Inside a Loop

```typescript
allItems = [...allItems, ...res.items];  // new array every iteration
```

**Fix:** `allItems.push(...res.items);`

---

### 15. `attempt-runner.tsx` Is a 1,243-Line God Component

Every 1-second timer tick (`setNow`) re-renders the entire component including all question cards. Split into:

```
<AttemptRunner>
  ├── <ExamProctoring />      (fullscreen, tab-switch, devtools)
  ├── <ExamTimer />           (timer, auto-submit)
  ├── <InstructionsModal />
  ├── <SubmitModal />
  └── <QuestionCard />        (React.memo — skips re-render on timer tick)
```

Memoizing `<QuestionCard>` with `React.memo` prevents 50+ question cards from re-rendering every second.

---

## ✅ Quick Wins — Do These First

| Fix | Time | Impact |
|---|---|---|
| Add `index=True` to 10 missing columns + migrate | 30 min | Eliminates table scans |
| Fix N+1 in `history()` with `joinedload` | 15 min | 21 queries → 1 |
| Set `staleTime: 10 * 60 * 1000` in `useTopics()` | 5 min | Stops repeated topic fetches |
| Move quill CSS import out of root layout | 5 min | Faster load on all non-editor pages |
| Remove duplicate columns in `test_series.py` | 5 min | Fixes silent ORM bug |
| Remove traceback from prod error responses | 10 min | Security fix |

---

## 📊 Estimated Improvement After All Fixes

| Metric | Before | After |
|---|---|---|
| DB queries per authenticated API request | Route + 1 auth DB lookup | Route only |
| DB queries for student history (10 attempts) | 12 | 2 |
| `list_public()` subquery executions | 1 per row in test_series | 0 (single join) |
| Topics API calls per 15-min session | 1 per page navigation | 1 total |
| CSS parsed on non-editor pages | Full Quill stylesheet | Zero |
| Question list download time (1,000 questions) | Sequential × N pages | Parallel (N× faster) |

---

## 🗺️ Recommended Fix Order

```
Week 1 — Critical (do now)
  ├── #4  Add missing DB indexes                (~30 min)
  ├── #2  Fix N+1 query in history()           (~15 min)
  └── #1  Cache user role in auth middleware    (~1 hr)

Week 2 — High
  ├── #3  Fix getAllQuestionsList parallel      (~30 min)
  ├── #7  Increase useTopics staleTime         (~10 min)
  └── #6  Remove DB write from GET handler     (~1 hr)

Week 3 — Medium
  ├── #8  Remove duplicate TestSeries columns  (~10 min)
  ├── #9  Move quill CSS out of root layout    (~5 min)
  ├── #10 Configure next.config.ts             (~30 min)
  ├── #11 Fix debug/traceback in prod          (~10 min)
  ├── #12 Wire up Redis caching                (~3-4 hrs)
  └── #13 Replace correlated subquery          (~1 hr)

Backlog
  └── #15 Refactor attempt-runner.tsx          (~1-2 days)
```

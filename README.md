# Question Generated API

A FastAPI REST API for generating, storing, and managing questions and answers.

## 🚀 Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- MySQL
- Pydantic
- JWT Authentication
- Uvicorn
- uv (Python package manager)

---

# Requirements

- Python 3.12+
- uv
- MySQL

Install uv if you don't have it:

```bash
pip install uv
```

or

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

# Clone Project

```bash
git clone https://github.com/Subhadip023/question_genarated_api.git

cd question_genarated_api
```

---

# Create Virtual Environment

```bash
uv venv
```

Activate

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

# Install Dependencies

```bash
uv sync
```

---

# Environment Variables

Create a `.env`

Example

```env
DATABASE_URL=mysql+pymysql://user:password@localhost/question_api

JWT_SECRET_KEY=your-secret-key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

# Database Migration

Generate a migration

```bash
uv run alembic revision --autogenerate -m "create users table"
```

Apply migrations

```bash
uv run alembic upgrade head
```

Rollback one migration

```bash
uv run alembic downgrade -1
```

Show current version

```bash
uv run alembic current
```

Migration history

```bash
uv run alembic history
```

---

# Run Development Server

```bash
uv run uvicorn main:app --reload
```

or

```bash
uv run fastapi dev main.py
```

---

# API Documentation

Swagger

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Running Tests

```bash
uv run pytest
```

Coverage

```bash
uv run pytest --cov=app
```

---

# Project Structure

```
question_genarated_api/

├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   └── config.py
├── main.py
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Development Workflow

Create a feature branch

```bash
git checkout -b feature/new-feature
```

Commit

```bash
git commit -m "feat: add user authentication"
```

Push

```bash
git push origin feature/new-feature
```

Open a Pull Request.

---

# Maintainer

**Subhadip Chakraborty** 
GitHub: https://github.com/Subhadip023

**Aniket Bera**
GitHub: https://github.com/Aniket-cyber69

**Nilrudra Dutta**
GitHub: https://github.com/nilrudradutta

---

# License

MIT License

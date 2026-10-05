# Test Series Access Control & Role Rules

This document outlines the business rules, role definitions, and access permissions for managing and viewing test series, questions, answer keys, and results.

---

## 1. Role Definitions

In relation to a Test Series, an authenticated user falls into one of the following roles:

| Role | Definition in System |
| :--- | :--- |
| **Super Admin / Org Admin** (`role = 0` or `1`) | System-level administrator or administrator of the organization owning the test series. |
| **Creator** (`role = 2`, `created_by == user_id`) | The teacher who originally created the test series. |
| **Supervisor** (`role = 2`) | A teacher who is either:<br>1. Assigned as the direct supervisor (`test_series.supervisor_id == user_id`), **OR**<br>2. The designated supervisor of the teacher group assigned to the test (`teacher_group.supervisor == user_id`). |
| **Group Teacher** (`role = 2`) | A teacher who is a member of the teacher group assigned to the test (`group_teachers.teacher_id == user_id` where `group_teachers.group_id == test_series.teacher_group_id` and `is_deleted = False`). |
| **Student** (`role = 3`) | A student enrolled in an assigned batch or explicitly assigned to take the test. |

---

## 2. Permissions Matrix

| Capability / Action | Admin | Creator | Supervisor | Group Teacher | Student |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **See Test** *(list & view details)* | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ *(Portal only)* |
| **Edit Test Settings** *(title, duration, time windows, batches, access type)* | ✅ Yes | ✅ Yes | ✅ Yes | ❌ **No** | ❌ No |
| **Add / Remove / Reorder Questions** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ **Yes** | ❌ No |
| **Edit Question Marks & Negative Marks** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ **Yes** | ❌ No |
| **Add / Upload Answer Key PDF** *(result sheet)* | ✅ Yes | ✅ Yes | ✅ Yes | ✅ **Yes** | ❌ No |
| **Publish Results / Scores** *(`is_result_show`, `is_score_show`)* | ✅ Yes | ✅ Yes | ✅ **Yes** | ❌ **No** | ❌ No |
| **View Test Results & Student Attempts** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ *(Masked until published)* |
| **Delete Test Series** | ✅ Yes | ✅ Yes *(if no attempts)* | ❌ No | ❌ No | ❌ No |

---

## 3. Specific Role Rules

### A. Supervisor
A supervisor oversees the execution and grading of the test series.
- **Can See:** Appears in their test series dashboard list and can open test details.
- **Can Edit:** Can update all test series settings (duration, dates, pass marks, assigned batches/students, instructions).
- **Can Manage Questions:** Can add questions, remove questions, reorder questions, and modify question marks and negative marks.
- **Can Add Answer Key:** Can upload or replace the answer key PDF / result sheet.
- **Can Publish Results:** Can toggle `is_result_show` and `is_score_show` to release scores and answer keys to students.
- **Cannot Delete:** Only the original creator (or admin) can delete a test series.

### B. Group Teacher
A group teacher collaborates on the content of the test series.
- **Can See:** Appears in their test series dashboard list and can open test details.
- **Can Add Questions:** Can select and add questions from the question bank into the test series.
- **Can Edit Question Marks:** Can customize marks and negative marks for questions in the test series.
- **Can Add Answer Key:** Can upload or replace the answer key PDF / result sheet.
- **Cannot Edit Settings:** Cannot change test metadata (test title, start/end dates, duration, total marks, assigned batches, supervisor assignment, or access type).
- **Cannot Publish Results:** Cannot publish results or alter student result/score visibility (`is_result_show`, `is_score_show`). Only supervisors and admins possess this privilege.
- **Cannot Delete:** Cannot delete the test series.

---

## 4. API Enforcement Reference

| API Endpoint | HTTP Method | Permitted Roles | Notes |
| :--- | :--- | :--- | :--- |
| `/api/test-series/` | `GET` | Admin, Creator, Supervisor, Group Teacher | Query filter includes `created_by`, `supervisor_id`, `teacher_group_id` (supervisor or member). |
| `/api/test-series/{id}` | `GET` | Admin, Creator, Supervisor, Group Teacher | Enforces `_apply_visibility`. |
| `/api/test-series/{id}` | `PUT` | Admin, Creator, Supervisor, Group Teacher | **Group Teacher:** restricted to updating `questions` (IDs, marks, negative marks). Attempting to edit metadata or result flags returns `403 Forbidden`. |
| `/api/test-series/{id}/result-sheet` | `POST` | Admin, Creator, Supervisor, Group Teacher | Allows uploading Answer Key PDF. |
| `/api/test-series/{id}/results` | `GET` | Admin, Creator, Supervisor, Group Teacher | Access results and submission records. |
| `/api/test-series/{id}` | `DELETE` | Admin, Creator | Only creator or admin can delete (blocked if attempts exist). |

---

## 5. Student Batches Access Control & Role Rules

This section defines the access control rules for Student Batches (`/student-batches`).

### A. Batch Ownership & Visibility
- **Admin (`role = 0` or `1`)**: Can view, manage, and CRUD **all batches** in the organization.
- **Teacher (`role = 2`)**: Can view and CRUD **only their own batches** (`batch.supervisor == user_id`).
  - A batch is considered the teacher's own if:
    1. The teacher created the batch (they are automatically set as the supervisor).
    2. An admin created the batch and assigned the teacher as the supervisor.
  - Teachers **cannot** see or manipulate batches belonging to other supervisors.

### B. Batch CRUD Permissions Matrix

| Capability / Action | Admin (`0, 1`) | Batch Supervisor Teacher (`2`) | Other Teachers (`2`) |
| :--- | :---: | :---: | :---: |
| **List Batches** (`GET /student-batches`) | ✅ All org batches | ✅ Own batches only | ❌ Excluded |
| **View Batch Details** (`GET /student-batches/{id}`) | ✅ Yes | ✅ Yes | ❌ 403 Forbidden |
| **Create Batch** (`POST /student-batches`) | ✅ Can select any supervisor | ✅ Auto-set to self as supervisor | — |
| **Edit Batch Details** (`PUT /student-batches/{id}`) | ✅ Yes (including supervisor) | ✅ Yes (**cannot** change supervisor) | ❌ 403 Forbidden |
| **Delete Batch** (`DELETE /student-batches/{id}`) | ✅ Yes | ✅ Yes | ❌ 403 Forbidden |
| **Manage Batch Students** (`POST/DELETE .../students`) | ✅ Yes | ✅ Yes | ❌ 403 Forbidden |

### C. Supervisor Assignment Rules
1. **Batch Creation**:
   - When an **admin** creates a batch, they can select any active teacher or admin in the organization as the supervisor.
   - When a **teacher** creates a batch, they **cannot select another supervisor**. The creating teacher is automatically set as the supervisor (`batch.supervisor = user_id`).
2. **Batch Editing**:
   - An **admin** can reassign the supervisor of a batch.
   - A **teacher cannot change the supervisor** of a batch. Attempting to modify the supervisor field returns `403 Forbidden` ("Teachers cannot change the batch supervisor").


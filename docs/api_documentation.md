# API reference — current foundation

All endpoints are prefixed `/api`. Authenticated endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API and database health |
| POST | `/auth/register` | Create user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/auth/me` | Current user |
| GET | `/tasks` | List own tasks |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get own task |
| DELETE | `/tasks/{id}` | Delete own task |
| POST | `/integrations/tavily/test` | Execute a real Tavily search test |

Task creation JSON: `{ "title": "...", "description": "...", "category": "research" }`. Supported categories: general, research, document, planning, data_analysis, exam_solver.


## Planner workflow (Milestone 2)

### `POST /api/tasks/<task_id>/plan`
Authenticated. Sends the task goal to Gemini, validates the returned structured plan, and persists subtasks with `waiting_for_approval` status. Returns the task, subtasks, and plan summary. Requires `GEMINI_API_KEY`.

### `POST /api/tasks/<task_id>/approve-plan`
Authenticated. Marks the plan approved and moves its subtasks to `queued`. This endpoint does not execute agents yet.

### `GET /api/tasks/<task_id>`
Now includes `plan_approved`, `plan_summary`, and the ordered `subtasks` collection.

## Exam Solver (Milestone 6)
All endpoints require `Authorization: Bearer <token>`.

- `POST /api/exams/upload` — multipart form field `file`; accepts PDF and common image formats; returns extracted question segments and an exam run ID.
- `GET /api/exams/runs` — current user's recent exam runs.
- `GET /api/exams/runs/{id}` — retrieve one of the current user's runs.
- `POST /api/exams/runs/{id}/solve` — Gemini worked answers followed by an independent Gemini review pass.
- `GET /api/exams/runs/{id}/download?format=pdf|docx` — export a solved run.

Uploads are limited to 15 MB, PDFs to 40 pages, and solving to 30 detected questions. Scanned documents need the Tesseract OCR system executable in addition to the Python package. AI review is advisory, not a correctness guarantee.

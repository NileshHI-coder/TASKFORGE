# TaskForge

Autonomous multi-agent task execution platform. The current repository includes JWT authentication, MySQL/XAMPP persistence, Gemini planning, specialist-agent execution and verification, Tavily-backed research, PDF/DOCX document generation, and the Milestone 5 Data Analysis Studio. Exam Solver, durable background workers, and production deployment hardening remain future work.

## Requirements
- Windows 10/11, VS Code
- Python 3.11+
- Node.js 20+ and npm
- XAMPP with MySQL running
- Gemini and Tavily API keys for AI workflows

## 1. Database
1. Start **MySQL** in XAMPP (Apache is not required for Flask).
2. Open `http://localhost/phpmyadmin`.
3. Import `database/schema.sql`.
4. Copy `.env.example` to `.env` in the project root and set DB credentials and API keys. The default XAMPP MySQL root password is often blank on local installations; use your actual setting.

## 2. Backend
```powershell
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
API: `http://localhost:5000/api/health`

## 3. Frontend
Open a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. If PowerShell blocks `npm.ps1`, run `npm.cmd install` and `npm.cmd run dev`, or use Command Prompt.

## API keys
- Gemini: create an API key in Google AI Studio and set `GEMINI_API_KEY`.
- Tavily: create an API key in the Tavily dashboard and set `TAVILY_API_KEY`.
Keys stay on the Flask backend; never add them to Vite variables.

## Current API
- `GET /api/health` — service/database status
- `POST /api/auth/register` — `{name,email,password}`
- `POST /api/auth/login` — `{email,password}`; returns bearer token
- `GET /api/auth/me` — authenticated profile
- `POST /api/tasks` — `{title,description,category}`; authenticated
- `GET /api/tasks` — authenticated user's tasks
- `GET /api/tasks/<id>` — authenticated task detail
- `DELETE /api/tasks/<id>` — delete own task
- `POST /api/integrations/tavily/test` — authenticated live Tavily test

## Project status
Milestones 1–4 are implemented in the codebase: authentication, MySQL task persistence, Gemini planning, specialist-agent request-driven execution, Tavily research, and PDF/DOCX generation. External Gemini/Tavily calls and MySQL connectivity still require the user's own credentials and local environment; they have not been live-tested here. Exam Solver, durable background workers, and production deployment hardening remain in progress. Milestone 5 adds a persisted Data Analysis Studio.

## Security notes
Use a unique secret in `.env`; do not deploy XAMPP/phpMyAdmin publicly. Local file storage is for development only. Add HTTPS, rate limits, CSRF strategy, malware scanning, and managed storage before production.

## Milestone 2 — Planner workflow
- `POST /api/tasks/<id>/plan` — calls Gemini to create a structured plan and persists ordered subtasks for review.
- `POST /api/tasks/<id>/approve-plan` — approves the saved plan and queues its subtasks; it does **not** launch agents yet.
- `GET /api/tasks/<id>` — now includes the task's subtasks and approval state.
- Open a task from the dashboard or task list to review, regenerate, and approve its plan.

If you already imported the Milestone 1 database schema, run `database/migrations/002_planner_workflow.sql` in phpMyAdmin before starting this version. For a fresh installation, import the updated `database/schema.sql` instead; do not run both the migration and the fresh schema changes.

The Planner Agent requires a valid `GEMINI_API_KEY`. A missing key or provider failure is shown as an API error; no sample plan is substituted.


## Milestone 3 — Specialist execution

After approving a generated plan, open its task detail page and choose **Execute next subtask**. TaskForge dispatches the next dependency-ready subtask to its assigned specialist agent, stores the execution record and output in MySQL, and updates the task status. Execute one subtask per request so progress remains inspectable and requests do not silently claim that an entire plan has completed. Failed subtasks can be retried from the task page. Once all subtasks complete, run the independent Verification Agent and review its report.

Execution API routes (JWT required):
- `POST /api/tasks/<id>/execute-next` — execute the next queued subtask.
- `POST /api/tasks/<id>/subtasks/<subtask_id>/retry` — requeue a failed subtask.
- `POST /api/tasks/<id>/verify` — independently review all completed outputs.
- `GET /api/tasks/<id>/executions` — inspect execution records and activity history.

The current runner is request-driven, not a durable background worker. Keep the Flask development server available while an agent request is running. For long tasks and production deployment, a worker queue and live progress transport are still required.


## Milestone 4 — Research & Document Studio

- `POST /api/research/<task_id>/run` — runs Tavily search and Gemini synthesis for an owned research/general/planning task. Optional JSON: `query`, `max_results` (1–10), `search_depth` (`basic`/`advanced`), `topic` (`general`/`news`/`finance`), `include_domains`, `exclude_domains`.
- `POST /api/research/<task_id>/export` — exports the saved research report as `pdf` or `docx`.
- `POST /api/documents/generate` — JSON fields: `task_id`, `title`, `instructions`, `content`, `format` (`pdf`/`docx`). Gemini drafts from supplied/task content; it is not instructed to invent missing facts.
- `GET /api/documents/files` — list generated files owned through the user's tasks.
- `GET /api/documents/files/<file_id>/download` — authenticated download.

Generated files are stored under `backend/app/storage/generated` for local development. Tavily retries transient provider failures up to three attempts; sources without URLs are excluded, and missing publication dates are labelled as not supplied. This is not a claim that the providers are reachable until valid API keys are configured and tested.

## Milestone 5 — Data Analysis Studio

For an existing database, run `database/migrations/005_data_analysis.sql` in phpMyAdmin. For a fresh installation, import the updated `database/schema.sql` instead.

- `POST /api/data/upload` — authenticated multipart upload (`file`) for CSV/XLS/XLSX, maximum 10 MB; computes dataset profile, preview, missing values, duplicate rows, numeric statistics, categorical distributions and pairwise correlations.
- `GET /api/data/runs` — list the signed-in user's analysis history.
- `GET /api/data/runs/<run_id>` — retrieve an owned analysis.
- `POST /api/data/runs/<run_id>/insights` — ask Gemini to interpret the computed summary, including limitations.
- Files are stored under `backend/app/storage/datasets`; metadata and computed results are stored in MySQL. The frontend `/data` route now contains the Data Analysis Studio with history, preview, tables, chart and AI insight action.

Limits: 10 MB upload, 100,000 rows and 150 columns. This milestone performs read-only profiling; it does not overwrite or modify the uploaded source dataset. Statistical outputs are computed with Pandas/NumPy. AI commentary is an interpretation, not a substitute for validating the source data.

## Milestone 6 — Exam Solver

The Exam Solver accepts PDF and image question papers, extracts text with PyMuPDF and optional Tesseract OCR, segments up to 30 detected questions, classifies question types, generates worked answers with Gemini, and runs a separate Gemini verification pass. Solutions can be exported as PDF or DOCX. Exam runs and results are scoped to the authenticated MySQL user.

### Database migration
Run `database/migrations/006_exam_solver.sql` against the existing `taskforge` MySQL database after applying earlier migrations.

### OCR setup
Install Python packages with `pip install -r backend/requirements.txt`. For scanned PDFs and image uploads, install the **Tesseract OCR system executable** separately and ensure it is on PATH. Text-based PDFs work with PyMuPDF without Tesseract. If Tesseract is unavailable, scanned pages may yield no readable text and the API will report that limitation.

### Exam Solver API
- `POST /api/exams/upload` — authenticated multipart upload (`file`); extracts and segments questions.
- `GET /api/exams/runs` — list the current user's uploads.
- `GET /api/exams/runs/<id>` — retrieve one owned upload and its results.
- `POST /api/exams/runs/<id>/solve` — generate answers and run an independent review pass.
- `GET /api/exams/runs/<id>/download?format=pdf|docx` — download a solved paper.

Limits: 15 MB per upload, 40 PDF pages, 30 detected questions, and 5,000 characters per question. OCR output and AI-generated answers must be reviewed; the verification pass is not a guarantee of correctness. Gemini credentials are required for solving. Existing Gemini, Tavily, MySQL and authentication configuration is retained.

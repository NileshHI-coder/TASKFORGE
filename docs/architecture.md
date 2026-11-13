# TaskForge architecture (foundation)

React/Vite is the browser client. It calls a Flask REST API. Flask uses SQLAlchemy with the PyMySQL driver to persist data in the MySQL service started by XAMPP. API secrets are held only in the root `.env` and read by backend service adapters.

Planned execution path: user goal → Planner Agent → approval gate → orchestrator/state machine → specialist agent(s) → Verifier → result/artifact storage. Tavily retrieves web evidence; Gemini reasons over supplied task context and retrieved evidence. Uploaded file text is untrusted input and must never override system instructions or tool permissions.

The first milestone implements authentication, task CRUD, health checks, and integration adapters. Background execution and plan approval are next.

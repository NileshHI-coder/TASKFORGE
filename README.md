# TaskForge – Autonomous Multi-Agent AI Platform

**TaskForge** is an AI-powered productivity platform designed to simplify complex tasks through intelligent planning, multi-agent workflows, research automation, document processing, and data analysis.

It combines a modern React frontend with a Python Flask backend to provide an integrated workspace where users can organize tasks, generate AI-powered plans, execute workflows, and manage their productivity efficiently.

---

## Overview

TaskForge aims to transform how users approach complex work by combining AI assistance with specialized agents.

Instead of manually handling every step, users can leverage AI-powered planning, research, execution, and analysis capabilities through a unified platform.

## Key Features

- **AI Task Planning:** Convert complex tasks into structured plans and actionable steps.
- **Multi-Agent Architecture:** Specialized agents for planning, research, and task execution.
- **AI Research Assistant:** Conduct research and organize relevant information.
- **Task Management:** Create, manage, and track tasks and their execution.
- **Document Processing:** Upload, process, and generate documents.
- **AI Data Analysis:** Analyze datasets and generate meaningful insights.
- **AI Exam Solver:** Support exam-related problem solving.
- **Authentication:** Secure user registration and login with JWT-based authentication.
- **Modern Dashboard:** User-friendly interface built with React and Tailwind CSS.

## Technology Stack

### Frontend
- React.js
- Vite
- JavaScript
- Tailwind CSS
- Axios

### Backend
- Python
- Flask
- Flask REST API
- SQLAlchemy
- JWT Authentication

### Artificial Intelligence
- Groq API
- Groq-hosted LLMs
- Tavily API
- Multi-Agent Architecture

### Database
- MySQL
- SQL
- Database Migrations

### Development & Deployment
- Git & GitHub
- Visual Studio Code
- Render

## Project Architecture

```text
TASKFORGE/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── storage/
│   │   └── utils/
│   │
│   ├── config.py
│   ├── requirements.txt
│   ├── run.py
│   └── test_gemini.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── context/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
│
├── database/
│   ├── migrations/
│   └── schema.sql
│
├── docs/
│   ├── api_documentation.md
│   ├── architecture.md
│   └── TaskForge_Product_Requirements_Document_PRD.pdf
│
├── tests/
│
├── .gitignore
├── CHANGELOG.md
└── README.md
```

## Getting Started

Follow these instructions to run TaskForge locally.

### Prerequisites

Install the following:

- Python 3.10+
- Node.js and npm
- MySQL or XAMPP
- Git
- Google Gemini API Key
- Tavily API Key (if using research functionality)

### 1. Clone the Repository

```bash
git clone https://github.com/NileshHI-coder/TASKFORGE.git
cd TASKFORGE
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file inside the `backend/` directory.

```env
FLASK_SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Add your database configuration using the variable names expected by the backend.

**Important:** Never upload your `.env` file or expose API keys publicly.

### 4. Database Setup

1. Start MySQL using XAMPP or your installed MySQL server.
2. Create the TaskForge database.
3. Configure database credentials in your backend environment.
4. Execute the SQL schema from:

```text
database/schema.sql
```

5. Apply any required migrations from:

```text
database/migrations/
```

### 5. Start the Backend

From the `backend/` directory:

```bash
python run.py
```

The Flask server will start using the host and port configured in the application.

### 6. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a frontend `.env` file if required:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Use the actual backend port configured in your application.

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser.

---

## API Modules

TaskForge organizes its backend functionality into dedicated route modules.

| Module | Responsibility |
|---|---|
| Authentication | Registration and login |
| Tasks | Task creation and planning |
| Research | AI-powered research |
| Documents | Document management |
| Data Analysis | Dataset analysis |
| Exam Solver | Exam-related problem solving |
| Integrations | External service integrations |

Refer to `docs/api_documentation.md` for additional API details.

## AI Architecture

TaskForge uses a specialized multi-agent architecture to organize AI-powered operations.

The backend includes:

- **Planner Agent:** Analyzes tasks and creates structured plans.
- **Research Agent:** Supports information gathering and research.
- **Execution Agents:** Handle specialized execution workflows.
- **Execution Service:** Coordinates execution operations.

The architecture is designed to make complex workflows easier to manage and extend.

## Testing

Run backend tests from the project root:

```bash
python -m pytest tests/
```

Individual tests are also available in the `tests/` directory.

## Deployment

TaskForge is designed for separate frontend and backend deployment.

| Component | Deployment |
|---|---|
| Frontend | Render Static Site |
| Backend | Render Web Service |
| Database | Hosted MySQL-compatible database |
| AI Services | Gemini API and Tavily API |

Production deployment requires configuring environment variables, database connectivity, CORS, and the appropriate frontend API URL.

## Security

- Keep API keys and credentials in environment variables.
- Never commit `.env` files.
- Use strong production secrets.
- Enable appropriate CORS restrictions.
- Protect authenticated endpoints.
- Use HTTPS in production.

## Future Enhancements

- Advanced autonomous agent collaboration.
- Improved real-time agent execution monitoring.
- Enhanced workflow automation.
- Advanced task analytics and reporting.
- Additional AI model integrations.
- Improved document generation and management.
- Scalable cloud deployment.

## Author

**Nilesh Prajapati**

B.Tech Computer Engineering Student

- GitHub: [@NileshHI-coder](https://github.com/NileshHI-coder)
- LinkedIn: [Nilesh Prajapati](https://www.linkedin.com/in/nilesh-prajapati-4a9593345/)

## Repository

[GitHub – TaskForge](https://github.com/NileshHI-coder/TASKFORGE)

---

*TaskForge – Plan Smarter. Execute Faster. Achieve More.*

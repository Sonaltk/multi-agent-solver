# 🤖 Multi-Agent GitHub Issue Solver

An AI-powered multi-agent system that autonomously analyzes GitHub issues and generates code patches, unit tests, and pull request descriptions — powered by LangGraph and Groq LLM.

🔗 **Live API:** https://multi-agent-solver.onrender.com/docs

---

## 🧠 How It Works

Paste any public GitHub issue URL and the system runs it through a pipeline of 5 specialized AI agents:

```
GitHub Issue URL
       ↓
 Agent 01 — Code Reader      → Identifies relevant files and root cause
       ↓
 Agent 02 — Planner          → Creates a step-by-step implementation plan
       ↓
 Agent 03 — Code Writer      → Writes the actual code patch
       ↓
 Agent 04 — Test Writer      → Generates unit tests for the patch
       ↓
 Agent 05 — PR Opener        → Produces a professional PR description
       ↓
  JSON Response
```

Each agent receives the full shared state and builds on the previous agent's output — just like a real engineering team.

---

## 🏗️ Architecture

```
multi-agent-system/
├── api.py                  # FastAPI REST API
├── Dockerfile              # Docker container config
├── requirements.txt        # Python dependencies
├── graph/
│   ├── state.py            # Shared AgentState (TypedDict)
│   └── orchestrator.py     # LangGraph StateGraph pipeline
└── agents/
    ├── code_reader.py      # Agent 01
    ├── planner.py          # Agent 02
    ├── code_writer.py      # Agent 03
    ├── test_writer.py      # Agent 04
    └── pr_opener.py        # Agent 05
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph (StateGraph) |
| LLM | Groq — Llama 3.3 70B |
| API Framework | FastAPI |
| Containerization | Docker |
| Cloud Deployment | Render |
| GitHub Integration | PyGithub |
| Language | Python 3.13 |

---

## 🚀 API Usage

### Health Check
```bash
curl https://multi-agent-solver.onrender.com/
```

### Solve a GitHub Issue
```bash
curl -X POST https://multi-agent-solver.onrender.com/solve \
  -H "Content-Type: application/json" \
  -d '{"github_issue_url": "https://github.com/owner/repo/issues/42"}'
```

### Response Structure
```json
{
  "repo": "owner/repo",
  "issue_number": 42,
  "issue_title": "Bug: something is broken",
  "issue_url": "https://github.com/owner/repo/issues/42",
  "code_context": "Analysis of relevant files...",
  "plan": "Step-by-step implementation plan...",
  "patch": "Generated code fix...",
  "tests": "Unit tests for the fix...",
  "pr_description": "Professional PR description..."
}
```

---

## 🖥️ Run Locally

### Prerequisites
- Python 3.11+
- Docker
- Groq API key (free at console.groq.com)
- GitHub Personal Access Token

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/multi-agent-solver.git
cd multi-agent-solver

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key" > .env
echo "GITHUB_TOKEN=your_github_token" >> .env

# Run the API
uvicorn api:app --reload
```

Visit `http://localhost:8000/docs` to use the interactive API UI.

### Run with Docker

```bash
docker build -t multi-agent-solver .

docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_groq_key \
  -e GITHUB_TOKEN=your_github_token \
  multi-agent-solver
```

---

## 💡 Key Concepts

**AgentState** — A shared TypedDict that flows through all agents. Each agent reads from it and writes back to it, building up the solution incrementally.

**StateGraph** — LangGraph's orchestration primitive. Defines nodes (agents) and edges (flow), compiles them into an executable pipeline.

**Conditional Edges** — The graph can route to different agents based on state, enabling dynamic decision-making (extendable feature).

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

*Built with LangGraph · Groq · FastAPI · Docker · Render*
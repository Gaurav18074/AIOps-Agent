# AIOps Agent - Autonomous Incident Response System

An agentic AI system that autonomously monitors infrastructure, detects failures, performs LLM-based root cause analysis, and generates incident reports.

## Architecture

```
                    ┌─────────────────┐
                    │   FastAPI App   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌─────▼─────┐       ┌─────▼──────┐
   │ Postgres │        │   Redis   │       │  LangGraph │
   │  (state) │        │ (dedup,   │       │  (agents)  │
   └──────────┘        │  cache)   │       └─────┬──────┘
                       └───────────┘             │
                                                 │
              ┌──────────────────────────────────┼──────────────────────────────────┐
              │                  │               │                 │                │
        ┌─────▼─────┐    ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼───────┐  ┌─────▼──────┐
        │Monitoring │ →  │ Log Analysis│→ │ Root Cause │→ │   Incident   │→ │Notification│
        │  Agent    │    │    Agent    │  │   Agent    │  │ Report Agent │  │   Agent    │
        └───────────┘    └─────────────┘  └────────────┘  └──────────────┘  └────────────┘
```

## Features

- **Multi-agent orchestration** via LangGraph
- **Autonomous monitoring** of HTTP endpoints with APScheduler
- **LLM root cause analysis** over collected logs
- **Incident deduplication** via Redis (avoid alert storms)
- **Incident reports** stored in Postgres with full audit trail
- **REST API** for managing monitored services and viewing incidents
- **Slack notifications** (optional)
- **Dockerized** end-to-end with docker-compose
- **CI/CD** via GitHub Actions
- **AWS-ready** with ECS task definitions included

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Agents**: LangGraph + LangChain
- **LLM**: OpenAI (swappable with Anthropic/Bedrock)
- **Scheduling**: APScheduler
- **Deployment**: Docker, docker-compose, AWS ECS

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- An OpenAI API key (or Anthropic — see `.env.example`)

### 2. Setup

```bash
git clone <your-repo>
cd aiops-agent
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run

```bash
docker compose up --build
```

Wait for all services to come up (~30 seconds). You'll see:

```
aiops-api      | INFO:     Uvicorn running on http://0.0.0.0:8000
aiops-worker   | Scheduler started
aiops-db       | database system is ready to accept connections
```

### 4. Try it

Open API docs: <http://localhost:8000/docs>

**Add a monitored site:**
```bash
curl -X POST http://localhost:8000/api/sites \
  -H "Content-Type: application/json" \
  -d '{"name": "Example", "url": "https://example.com", "check_interval_seconds": 60}'
```

**Trigger an incident manually (for testing):**
```bash
curl -X POST http://localhost:8000/api/sites \
  -H "Content-Type: application/json" \
  -d '{"name": "Broken Site", "url": "https://this-domain-does-not-exist-12345.com", "check_interval_seconds": 30}'
```

Within ~30 seconds, the monitoring agent detects the failure, the LangGraph pipeline runs all agents, and an incident report appears at:

```bash
curl http://localhost:8000/api/incidents
```

### 5. Stop

```bash
docker compose down -v   # -v removes volumes too
```

## Project Structure

```
aiops-agent/
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── deps.py              # FastAPI dependencies
│   ├── routers/
│   │   ├── sites.py         # Site CRUD
│   │   ├── incidents.py     # Incident endpoints
│   │   └── health.py        # Healthcheck
│   ├── agents/
│   │   ├── graph.py         # LangGraph orchestrator
│   │   ├── monitoring.py    # Health check logic
│   │   ├── log_analysis.py  # Log parsing agent
│   │   ├── root_cause.py    # LLM RCA agent
│   │   ├── reporter.py      # Incident report agent
│   │   └── notifier.py      # Slack/email notifier
│   ├── services/
│   │   ├── dedup.py         # Redis-based dedup
│   │   └── llm.py           # LLM client wrapper
│   └── worker.py            # APScheduler entrypoint
├── tests/
│   ├── test_api.py
│   └── test_agents.py
├── alembic/                 # DB migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .github/workflows/ci.yml
├── infra/
│   └── ecs-task-definition.json
└── README.md
```

## API Endpoints

| Method | Path                       | Description                |
|--------|----------------------------|----------------------------|
| GET    | /health                    | Liveness check             |
| GET    | /api/sites                 | List monitored sites       |
| POST   | /api/sites                 | Add a site                 |
| DELETE | /api/sites/{id}            | Remove a site              |
| GET    | /api/incidents             | List incidents             |
| GET    | /api/incidents/{id}        | Get incident details + RCA |
| POST   | /api/incidents/{id}/replay | Re-run agent pipeline      |

## How the Agent Pipeline Works

When the monitoring agent detects a failure:

1. **Dedup check** — Redis key `incident:{site_id}:{error_hash}` with 5-min TTL prevents alert storms.
2. **Log Analysis Agent** — Collects the failure event, recent response time history, and HTTP error context.
3. **Root Cause Agent** — Sends the structured log bundle to the LLM with a system prompt forcing structured JSON output (cause, confidence, suggested_fix).
4. **Incident Report Agent** — Persists the structured incident to Postgres.
5. **Notification Agent** — Sends a Slack message (if `SLACK_WEBHOOK_URL` is set).

The pipeline is defined as a LangGraph state machine — see `app/agents/graph.py`.

## Configuration

All config is via environment variables. See `.env.example`:

| Variable              | Default                     | Description                  |
|-----------------------|-----------------------------|------------------------------|
| DATABASE_URL          | postgresql+psycopg://...    | Postgres connection string   |
| REDIS_URL             | redis://redis:6379/0        | Redis URL                    |
| OPENAI_API_KEY        | (required)                  | LLM provider key             |
| LLM_MODEL             | gpt-4o-mini                 | Model name                   |
| LLM_PROVIDER          | openai                      | openai / anthropic           |
| SLACK_WEBHOOK_URL     | (optional)                  | Slack incoming webhook       |
| DEDUP_TTL_SECONDS     | 300                         | Incident dedup window        |
| LOG_LEVEL             | INFO                        | Python logging level         |

## Testing

```bash
docker compose exec api pytest -v
```

## Deployment to AWS

See `infra/ecs-task-definition.json` for a sample ECS Fargate task definition.

**High-level steps:**

1. Push image to ECR: `docker build -t aiops-agent . && docker tag ... && docker push ...`
2. Create RDS Postgres instance and ElastiCache Redis cluster.
3. Store `OPENAI_API_KEY` in AWS Secrets Manager; reference it in the task definition.
4. Register the task definition and create an ECS service behind an ALB.
5. Set up CloudWatch Logs for the task.

## Trade-offs & Design Notes

- **Why LangGraph over a hand-rolled DAG?** Provides built-in state management, retry semantics, and observability (via LangSmith if needed). The graph definition is also the documentation.
- **Why Redis for dedup?** Cheap, fast, TTL-native. Avoids a Postgres write on every check.
- **Why a separate worker container?** Decouples request handling from background work. The API stays responsive even when an agent pipeline takes 10+ seconds for LLM calls.
- **LLM safety** — The RCA agent prompt forbids destructive suggestions (`rm`, `DROP TABLE`, etc.) and outputs are stored as advisory text, never auto-executed.
- **Cost control** — Dedup prevents repeated LLM calls for the same recurring failure. Use `gpt-4o-mini` by default.

## What to Build Next

- Replace OpenAI with AWS Bedrock for full AWS-native deployment
- Add prompt evaluation harness (run RCA against synthetic incidents, score accuracy)
- Add a React dashboard
- Auto-create Jira tickets via Atlassian API
- Add support for log shippers (CloudWatch Logs, Loki)

## License

MIT

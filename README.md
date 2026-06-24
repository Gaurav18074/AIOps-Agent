# AIOps-Agent

## Autonomous Incident Response System

An agentic AI platform that autonomously monitors infrastructure, detects failures, performs LLM-powered root cause analysis, and generates incident reports.

---

## Features

- Autonomous monitoring of HTTP endpoints
- Multi-agent orchestration using LangGraph
- LLM-powered root cause analysis
- Incident deduplication with Redis
- Incident report generation and storage
- REST API for managing monitored services
- Slack notification support
- Dockerized deployment
- GitHub Actions CI/CD
- AWS ECS deployment ready

---

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy 2.0
- LangGraph
- LangChain
- OpenAI API
- APScheduler
- Docker
- AWS ECS

---

## Architecture

```text
User
  │
  ▼
FastAPI Application
  │
  ├── PostgreSQL (State & Incidents)
  ├── Redis (Cache & Deduplication)
  └── LangGraph Agent Workflow
          │
          ▼
Monitoring Agent
          │
          ▼
Log Analysis Agent
          │
          ▼
Root Cause Agent
          │
          ▼
Incident Report Agent
          │
          ▼
Notification Agent

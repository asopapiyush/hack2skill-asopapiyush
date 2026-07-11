# Phase 1: Foundation & Infrastructure (Weeks 1-2)

**Objective:** Set up project scaffolding, database, API gateway, and core RAG infrastructure.

**Dependencies:** None (Phase 1 is foundational)

**Parallel Track:** All tasks in this phase can run in parallel after initial project setup.

---

## Task List

### 1.1 Project Scaffolding & Monorepo Setup
**Effort:** 4 hours | **Priority:** CRITICAL

**Description:**
Create project structure with separate backend (Python/Node.js) and frontend (React/React Native) codebases. Set up build tooling, linting, pre-commit hooks.

**Acceptance Criteria:**
- [ ] Monorepo with `/backend` and `/frontend` directories
- [ ] Python project: FastAPI app structure with `src/`, `tests/`, `docs/` directories
- [ ] Node.js project: Express + TypeScript with same structure
- [ ] Pre-commit hooks configured (black, isort, eslint, prettier)
- [ ] CI/CD pipeline skeleton (GitHub Actions) with test + lint stages
- [ ] Environment config: `.env.example` with all required secrets
- [ ] README with setup instructions (under 5 minutes to run locally)

**Files to Create:**
```
vayuassist/
├── backend/
│   ├── src/
│   ├── tests/
│   ├── docs/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── web/
│   ├── mobile/
│   ├── package.json
│   └── README.md
├── .github/workflows/
│   ├── test.yml
│   ├── lint.yml
│   └── deploy.yml
├── IMPLEMENTATION_ROADMAP.md
└── docker-compose.yml (for local dev)
```

**Notes:** Use Ponytail principles—reuse existing templates, avoid over-engineering.

---

### 1.2 PostgreSQL Schema Design & Migration Setup
**Effort:** 6 hours | **Priority:** CRITICAL | **Blocks:** 1.3, 1.5, 1.6

**Description:**
Design and implement PostgreSQL schema for users, plans, chat history, advisories, recovery guidance. Set up migration framework (Alembic for Python or Knex for Node.js).

**Acceptance Criteria:**
- [ ] Database schema defined for:
  - `users` (id, email, phone, region, preferred_language, created_at, health_conditions encrypted)
  - `preparedness_plans` (id, user_id, plan_json, threat_level, created_at, expires_at)
  - `chat_messages` (id, user_id, message, response, intent, created_at)
  - `travel_advisories` (id, user_id, origin_lat/lon, dest_lat/lon, advisory_json, safety_score, created_at)
  - `recovery_guidance` (id, user_id, damage_type, severity, guidance_json, created_at)
- [ ] Indices created for fast queries (user_id, created_at, region, threat_level)
- [ ] Geospatial index for travel advisory queries
- [ ] Migration framework configured + first migration working
- [ ] Partitioning strategy for `chat_messages` (by month)
- [ ] Encryption-at-rest configured (or TDE enabled)
- [ ] Test: Can create user + plan via migrations in local DB

**SQL Schema File:** `backend/src/database/schema.sql`

**Test:** `tests/unit/database/test_schema.py`

**Notes:** Foreign key constraints, ON DELETE CASCADE, NOT NULL defaults already defined in schema.

---

### 1.3 Redis Setup (Cache & Session Store)
**Effort:** 3 hours | **Priority:** HIGH | **Depends on:** 1.1

**Description:**
Configure Redis for distributed caching, session management, and message queue buffering. Set up connection pooling and TTL policies.

**Acceptance Criteria:**
- [ ] Docker Compose includes Redis service (6379)
- [ ] Connection pool configured (min 5, max 50 connections)
- [ ] TTL policies defined:
  - Weather data: 10 min
  - Travel advisories: 10 min
  - User plans: 24 hours
  - Session tokens: 7 days
- [ ] Redis client configured with retry logic (exponential backoff)
- [ ] Health check endpoint exists: `GET /health/redis`
- [ ] Test: Can set + get key-value pair with TTL expiration

**Files:**
- `backend/src/config/cache.py` (Redis client initialization)
- `tests/integration/test_redis_connection.py`

**Notes:** Start with simple Redis; migrate to Redis Cluster only if needed for scale.

---

### 1.4 Vector Database Setup (Pinecone)
**Effort:** 4 hours | **Priority:** CRITICAL | **Blocks:** 1.5, 2.2

**Description:**
Set up Pinecone account, create index for RAG embeddings, design document schema for monsoon preparedness data.

**Acceptance Criteria:**
- [ ] Pinecone project created + API key secured in Vault
- [ ] Vector index created:
  - Dimension: 1536 (OpenAI embeddings)
  - Metric: cosine similarity
  - Replicas: 3 (for high availability)
- [ ] Document schema designed:
  ```json
  {
    "id": "doc_imd_rain_advisory_001",
    "text": "...",
    "metadata": {
      "source": "IMD_Government",
      "category": "heavy_rain",
      "region": ["Maharashtra", "Gujarat"],
      "trust_score": 0.99,
      "last_updated": "2026-06-15"
    }
  }
  ```
- [ ] Embedding function configured (OpenAI API)
- [ ] Initial batch of verified documents imported (50+ monsoon protocols)
- [ ] Semantic search tested: query "water entering house" returns relevant results
- [ ] Test: Can retrieve top-5 documents by similarity score

**Files:**
- `backend/src/external/vector_db.py` (Pinecone client)
- `backend/src/data/seed_rag.py` (Initial document import)
- `tests/integration/test_vector_db.py`

**Initial Documents to Import:**
- IMD (India Meteorological Department) monsoon guidelines
- Red Cross disaster preparedness protocols
- Government health advisories (waterborne diseases, electrocution)
- Regional emergency contact directories

**Notes:** Use managed Pinecone; don't self-host Milvus unless cost becomes issue.

---

### 1.5 API Gateway & Authentication Setup
**Effort:** 5 hours | **Priority:** CRITICAL | **Depends on:** 1.1, 1.3

**Description:**
Configure API gateway (AWS API Gateway + Nginx) for request routing, rate limiting, JWT validation, CORS handling.

**Acceptance Criteria:**
- [ ] Nginx reverse proxy configured:
  - Rate limiting: 100 req/min globally, 1000 req/hour per user
  - CORS headers set correctly
  - TLS 1.3+ enforced
  - Request/response logging enabled
- [ ] JWT validation middleware:
  - Public key loaded from Vault
  - Token expiry: 1 hour
  - Refresh token: 7 days (stored in Redis)
  - Algorithm: RS256
- [ ] Auth endpoints implemented:
  - `POST /auth/login` (email + password → tokens)
  - `POST /auth/refresh` (refresh token → new access token)
  - `POST /auth/signup` (new user registration)
- [ ] Rate limiting test: 101st request returns 429 (Too Many Requests)
- [ ] Invalid JWT test: Returns 401 with "Invalid token"
- [ ] Test: Protected endpoint requires valid token

**Files:**
- `backend/src/api/middleware/auth.py` (JWT validation)
- `backend/src/api/routes/auth.py` (Login/signup endpoints)
- `backend/nginx.conf` (Nginx configuration)
- `tests/integration/test_auth_flow.py`

**Notes:** Use Auth0 or Keycloak for MFA + OAuth2 later; for now, JWT-only is sufficient.

---

### 1.6 Secrets Management (Vault Integration)
**Effort:** 3 hours | **Priority:** HIGH | **Depends on:** 1.1

**Description:**
Integrate HashiCorp Vault (or AWS Secrets Manager) for secure storage of API keys, database passwords, encryption keys.

**Acceptance Criteria:**
- [ ] Vault instance running (Docker or AWS Secrets Manager configured)
- [ ] Secrets defined:
  - `vayuassist/db/password` (PostgreSQL)
  - `vayuassist/redis/password` (Redis)
  - `vayuassist/jwt/public_key` (JWT verification)
  - `vayuassist/api_keys/weather` (IMD, AccuWeather)
  - `vayuassist/api_keys/maps` (Google Maps)
  - `vayuassist/api_keys/llm` (OpenAI, Gemini)
  - `vayuassist/api_keys/vector_db` (Pinecone)
  - `vayuassist/api_keys/speech` (Google Cloud Speech)
  - `vayuassist/encryption/cipher_key` (Data encryption)
- [ ] Vault client configured with service role authentication
- [ ] Secret rotation policy: Every 90 days for API keys
- [ ] Audit logging: All secret access logged
- [ ] Test: Fetch secret at runtime, verify decryption
- [ ] `.env.example` does NOT contain real secrets; only placeholders

**Files:**
- `backend/src/utils/secrets.py` (Vault client + secret fetching)
- `backend/src/config/settings.py` (Environment-based config)
- `.env.example` (template only)
- `tests/unit/utils/test_secrets.py`

**Notes:** Never commit `.env` files or real secrets to git. Use `.gitignore` aggressively.

---

### 1.7 Monitoring & Logging Setup
**Effort:** 4 hours | **Priority:** HIGH | **Depends on:** 1.1

**Description:**
Configure Prometheus (metrics collection), ELK Stack (centralized logging), and Grafana (visualization). Set up structured logging.

**Acceptance Criteria:**
- [ ] Prometheus server running locally (Docker)
  - Scrape interval: 15 seconds
  - Retention: 15 days
- [ ] Application exposes `/metrics` endpoint (Prometheus format)
- [ ] Structured logging configured (JSON format with context):
  ```json
  {
    "timestamp": "2026-07-11T10:30:00Z",
    "level": "INFO",
    "message": "Chat message processed",
    "user_id": "user123",
    "intent": "emergency",
    "latency_ms": 1234,
    "trace_id": "abc123"
  }
  ```
- [ ] ELK Stack (or Loki) running locally for log aggregation
- [ ] Grafana dashboard created:
  - Request latency (P50, P95, P99)
  - Error rate by endpoint
  - Active users
  - External API health
- [ ] Health check endpoint: `GET /health` returns service status
- [ ] Test: Generate request, verify logs in ELK + metrics in Prometheus

**Files:**
- `backend/src/config/logging.py` (Structured logging setup)
- `backend/src/utils/metrics.py` (Prometheus metrics)
- `backend/monitoring/docker-compose.yml` (ELK + Prometheus + Grafana)
- `backend/monitoring/prometheus.yml` (Prometheus config)
- `backend/monitoring/grafana-dashboards/` (Dashboard JSON)

**Key Metrics:**
- `http_request_duration_seconds` (histogram)
- `http_requests_total` (counter)
- `database_query_duration_ms` (histogram)
- `external_api_latency_ms` (histogram)
- `rag_retrieval_time_ms` (histogram)
- `chat_response_latency_ms` (histogram)

---

### 1.8 Docker & Local Development Environment
**Effort:** 3 hours | **Priority:** HIGH | **Depends on:** 1.1, 1.2, 1.3

**Description:**
Create `docker-compose.yml` for full local development stack (API, DB, Redis, Pinecone client mock, Vault, monitoring).

**Acceptance Criteria:**
- [ ] `docker-compose.yml` defines all services:
  - PostgreSQL (port 5432)
  - Redis (port 6379)
  - API backend (port 8000)
  - Frontend dev server (port 3000)
  - Prometheus (port 9090)
  - Grafana (port 3000)
  - Mock Pinecone (or live Pinecone with fallback)
- [ ] Single command to start dev environment: `docker-compose up`
- [ ] Database auto-initializes on first run (Alembic migration)
- [ ] Logs aggregated: `docker-compose logs -f`
- [ ] Development workflow:
  - Code changes trigger hot reload (no rebuild)
  - Database accessible: `psql -h localhost -U vayuassist -d vayuassist`
- [ ] Test: Can run full integration test suite locally

**Files:**
- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `README_LOCAL_SETUP.md` (step-by-step setup guide)

**Notes:** Keep docker-compose.yml for development only; use Kubernetes manifests for production.

---

## Completion Checklist

- [ ] 1.1: Project scaffolding complete + CI/CD pipeline runs
- [ ] 1.2: Database schema migrated + indices created
- [ ] 1.3: Redis running + connection pool works
- [ ] 1.4: Pinecone index created + sample documents imported
- [ ] 1.5: API gateway routing requests + JWT validation works
- [ ] 1.6: Vault configured + secrets accessible at runtime
- [ ] 1.7: Prometheus + Grafana running + metrics visible
- [ ] 1.8: `docker-compose up` starts full dev stack in < 1 min

**Phase 1 Complete When:** All above checkboxes ticked + Phase 2 foundation ready

---

## Effort Summary
- Total: ~32 hours (4 days)
- Parallelizable after 1.1: Tasks 1.2-1.8 can run in parallel
- Critical path: 1.1 → 1.5, 1.6 (auth before services)

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Database schema lock-in | Review schema with team before finalizing; allow migration flexibility |
| Vault setup complexity | Use AWS Secrets Manager (simpler) if Vault too complex |
| Pinecone cold start | Pre-populate with 50+ monsoon documents; test retrieval quality |
| Rate limiting too aggressive | Start with high limits; reduce based on actual traffic patterns |
| Monitoring overhead | Use sampling for high-volume endpoints (e.g., 10% of requests) |

---

**Last Updated:** 2026-07-11

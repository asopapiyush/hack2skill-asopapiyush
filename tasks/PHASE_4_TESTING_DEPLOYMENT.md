# Phase 4: Testing & Deployment (Weeks 8-9)

**Objective:** Achieve 90%+ test coverage, conduct chaos engineering, deploy to production with monitoring.

**Dependencies:** Phase 3 must be complete

**Parallel Tracks:**
- Track A: Comprehensive test coverage (4.1-4.3)
- Track B: Performance & chaos testing (4.4-4.5)
- Track C: Production deployment (4.6-4.8)

---

## Track A: Test Coverage (Priority: CRITICAL)

### 4.1 Unit Tests for All Services
**Effort:** 12 hours | **Priority:** CRITICAL | **Depends on:** 2.1-2.11

**Description:**
Write unit tests for all services (RAG, chat, planning, advisory, recovery) with target coverage > 90%.

**Acceptance Criteria:**
- [ ] Test structure:
  ```
  backend/tests/unit/
  ├── services/
  │   ├── test_rag_service.py
  │   ├── test_chat_service.py
  │   ├── test_plan_service.py
  │   ├── test_advisory_service.py
  │   ├── test_recovery_service.py
  │   ├── test_guardrail_engine.py
  │   ├── test_intent_classifier.py
  │   └── test_onboarding_service.py
  ├── external/
  │   ├── test_llm_client.py
  │   ├── test_vector_db.py
  │   ├── test_weather_api.py
  │   ├── test_maps_api.py
  │   ├── test_speech_service.py
  │   └── test_twilio_client.py
  ├── repositories/
  │   ├── test_user_repo.py
  │   ├── test_plan_repo.py
  │   └── test_chat_history_repo.py
  └── utils/
      ├── test_validators.py
      ├── test_formatters.py
      └── test_secrets.py
  ```
- [ ] Coverage targets per module:
  - Core services (RAG, chat, guardrails): 95%
  - External integrations (APIs, DB): 80%
  - Utils: 90%
  - Middleware: 85%
- [ ] Mock strategies:
  - Mock external APIs (LLM, weather, maps)
  - Mock Pinecone with in-memory vector store
  - Mock speech services (STT/TTS)
  - Real database for integration tests (use test DB)
- [ ] Fixtures:
  - Sample user contexts
  - Mock RAG documents
  - Mock weather data
  - Mock LLM responses
- [ ] Run coverage report:
  ```bash
  pytest --cov=src --cov-report=html tests/unit/
  # Target: > 90% overall coverage
  ```
- [ ] Test examples:
  - GuardrailEngine hard-stop detection
  - IntentClassifier accuracy (>90% on known intents)
  - PlanService customization for health conditions
  - TravelAdvisoryService safety scoring
  - RecoveryService damage-type-specific guidance

**Files:**
- `backend/tests/unit/services/` (all service tests)
- `backend/tests/unit/external/` (API client tests)
- `backend/tests/fixtures/` (shared test data)
- `backend/tests/conftest.py` (pytest configuration)

**Example Unit Test:**
```python
@pytest.mark.asyncio
async def test_guardrail_hard_stop_drowning():
    guardrail = GuardrailEngine(vector_db=AsyncMock(), ...)
    
    result, safety = await guardrail.guard_response(
        user_query="I'm drowning",
        llm_response="Try swimming",
        user_context={"region": "Maharashtra"}
    )
    
    assert safety == "escalated"
    assert "EMERGENCY" in result
    assert "101" in result  # Fire rescue number
```

---

### 4.2 Integration Tests for API Flows
**Effort:** 10 hours | **Priority:** CRITICAL | **Depends on:** 2.1-2.11, 4.1

**Description:**
Test end-to-end API flows: chat → RAG → LLM → response, plan generation, advisory streaming.

**Acceptance Criteria:**
- [ ] Test structure:
  ```
  backend/tests/integration/
  ├── test_chat_flow.py
  ├── test_plan_generation_flow.py
  ├── test_advisory_system.py
  ├── test_rag_pipeline.py
  ├── test_onboarding_flow.py
  ├── test_recovery_flow.py
  ├── test_auth_flow.py
  └── test_multilingual.py
  ```
- [ ] Chat flow integration test:
  - User sends message
  - Intent classified correctly
  - RAG retrieves relevant documents
  - LLM generates response with retrieved context
  - Guardrails validate response
  - Response sent to user
  - Chat history logged
- [ ] Plan generation flow:
  - User completes onboarding
  - Context stored in DB
  - Plan generated via LLM + RAG
  - Health/location customization verified
  - Plan cached in Redis
  - User can retrieve + update plan
- [ ] Travel advisory flow:
  - User requests route advisory
  - Weather data fetched
  - Traffic data fetched
  - Route safety scored
  - Advisory generated + returned
  - WebSocket stream updates every 10 min
- [ ] Test data:
  - Use test database (PostgreSQL in Docker)
  - Use test Redis instance
  - Mock external APIs with realistic responses
  - Cleanup after each test
- [ ] Performance checks during integration tests:
  - Chat response < 2s
  - Plan generation < 10s
  - Advisory < 1s
- [ ] Error scenarios:
  - Upstream API (weather, maps) timeout
  - LLM rate limit exceeded
  - Vector DB unavailable
  - Database connection lost
  - Verify graceful degradation + fallbacks

**Files:**
- `backend/tests/integration/` (all integration tests)
- `backend/tests/integration/fixtures/` (test data)

**Example Integration Test:**
```python
@pytest.mark.asyncio
async def test_complete_chat_flow(test_client, db_session):
    # Create user
    user_response = await test_client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "secure",
        "region": "Maharashtra"
    })
    user_id = user_response.json()["user_id"]
    token = user_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send chat message
    chat_response = await test_client.post(
        "/api/chat/message",
        json={"message": "Water is entering", "language": "en-IN"},
        headers=headers
    )
    
    assert chat_response.status_code == 200
    result = chat_response.json()
    
    # Verify flow
    assert result["intent"] in ["emergency", "preparedness"]
    assert "escalation_flag" in result or "EMERGENCY" in result["response"]
    
    # Verify chat history logged
    chat_history = await db_session.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).first()
    assert chat_history is not None
```

---

### 4.3 End-to-End User Journey Tests
**Effort:** 8 hours | **Priority:** HIGH | **Depends on:** 4.1, 4.2

**Description:**
Test complete user journeys: signup → onboarding → plan → chat → emergency → recovery.

**Acceptance Criteria:**
- [ ] Journey 1: "Prepared Citizen"
  - Signup → Onboarding → Generate plan → Daily reminder → Execute plan
  - Verify plan completion rate > 80%
- [ ] Journey 2: "Emergency Response"
  - Send emergency message → Guardrail escalation → Emergency checklist → Progress tracking
  - Verify checklist completion in < 15 min
- [ ] Journey 3: "Safe Commute"
  - Request travel advisory → Receive safe route → Stream updates → Reroute if alert
  - Verify no user routed through flooded zone
- [ ] Journey 4: "Post-Disaster Recovery"
  - Disaster occurs → Recovery guidance generated → Cleanup protocol + health monitoring
  - Verify timeline to normalcy accurate
- [ ] Journey 5: "Multilingual Non-Reader"
  - Signup (auto-detect language) → Voice onboarding → Voice chat → Voice alerts
  - Verify all interactions via voice only
- [ ] Test environment:
  - Full production-like stack (Postgres, Redis, Pinecone, LLM)
  - Realistic test data
  - Monitoring enabled to catch issues
- [ ] Success metrics:
  - All journeys complete without errors
  - Latency within SLA for all endpoints
  - No data integrity issues
  - No security vulnerabilities in flow

**Files:**
- `backend/tests/e2e/` (end-to-end tests)
- `backend/tests/e2e/conftest.py` (E2E fixtures + setup)

---

## Track B: Performance & Chaos Testing (Priority: HIGH)

### 4.4 Load Testing & Performance Benchmarks
**Effort:** 6 hours | **Priority:** HIGH | **Depends on:** 4.1, 4.2

**Description:**
Load test API endpoints to verify SLA compliance under realistic traffic patterns.

**Acceptance Criteria:**
- [ ] Load testing tool: Locust or k6
- [ ] Test scenarios:
  - Chat endpoint: 100 concurrent users × 10 requests each
  - Plan generation: 10 concurrent users × 1 request each
  - Advisory retrieval: 50 concurrent users × 5 requests each
  - Travel advisory streaming: 20 WebSocket connections × 30 min duration
- [ ] SLA verification:
  - Chat response P95 < 2s (all scenarios)
  - Plan generation P95 < 10s
  - Advisory P95 < 1s
  - WebSocket latency < 50ms per message
- [ ] Resource monitoring during load:
  - CPU usage < 80%
  - Memory usage < 85%
  - Database connection pool > 20% available
  - Redis memory < 70% of available
- [ ] Failure modes:
  - Graceful degradation (no cascading failures)
  - Retry logic kicks in if service slow
  - Cache hits increase under load
- [ ] Bottleneck identification:
  - Slowest endpoint? (Likely LLM inference)
  - Database query slow? (Check indices)
  - External API latency? (Add caching)
- [ ] Report:
  - Load test results with P50, P95, P99 latencies
  - Resource utilization graphs
  - Identified bottlenecks + mitigation plan

**Files:**
- `backend/performance_tests/load_test.py` (Locust/k6 script)
- `backend/performance_tests/results/` (Test results + analysis)

**Example Load Test:**
```python
class UserBehavior(HttpUser):
    @task
    def chat_message(self):
        self.client.post(
            "/api/chat/message",
            json={"message": "Water entering", "language": "en-IN"}
        )
    
    @task
    def get_plan(self):
        self.client.get("/api/plans/{plan_id}")
    
    wait_time = between(1, 5)

# Run: locust -f load_test.py --headless -u 100 -r 10 -t 1h
```

---

### 4.5 Chaos Engineering & Resilience Testing
**Effort:** 6 hours | **Priority:** HIGH | **Depends on:** 4.1, 4.2

**Description:**
Test system behavior under failure conditions (API timeouts, DB unavailable, cache miss, LLM rate limit).

**Acceptance Criteria:**
- [ ] Failure scenarios:
  - Vector DB (Pinecone) timeout/unavailable
  - LLM API (OpenAI) rate limit / timeout
  - Weather API timeout
  - Database connection lost
  - Redis unavailable
  - Network latency (2s delay)
  - Partial degradation (1 out of 3 instances down)
- [ ] Resilience expectations:
  - Vector DB down: Fallback to generic response
  - LLM rate limit: Retry with exponential backoff
  - Weather API timeout: Use cached weather from 1 hour ago
  - DB unavailable: Cache responses in-memory temporarily
  - Redis down: Fall back to in-process cache
  - Network latency: Requests still complete within SLA
- [ ] Test implementation:
  ```python
  @pytest.mark.asyncio
  async def test_vector_db_downtime():
      # Simulate Pinecone timeout
      vector_db.search = AsyncMock(side_effect=TimeoutError)
      
      # Chat service should still respond
      response = await chat_service.handle_message(...)
      
      assert response is not None  # Fallback response
      assert "contact local authorities" in response.lower()
  ```
- [ ] Monitoring during chaos:
  - Error rates spike but stay < 5%
  - Latency increases but stays < 5s
  - No data loss
  - System recovers after failure resolution
- [ ] Test report:
  - Chaos scenario results
  - Recovery time after failure
  - User impact assessment
  - Mitigation effectiveness

**Files:**
- `backend/tests/chaos/` (Chaos test suite)
- `backend/tests/chaos/test_db_failure.py`
- `backend/tests/chaos/test_api_timeout.py`
- `backend/tests/chaos/test_cache_miss.py`

---

## Track C: Production Deployment (Priority: CRITICAL)

### 4.6 Kubernetes Manifests & Container Images
**Effort:** 6 hours | **Priority:** CRITICAL | **Depends on:** 1.8

**Description:**
Create production Kubernetes manifests for all services, configure auto-scaling, resource limits.

**Acceptance Criteria:**
- [ ] Docker images:
  - Backend: Multi-stage build (optimize size)
  - Frontend: Nginx-based SPA server
  - Worker: Same base as backend (for async jobs)
  - All images scanned for vulnerabilities (Trivy)
- [ ] Kubernetes manifests:
  ```
  k8s/
  ├── namespace.yaml (vayuassist namespace)
  ├── secrets.yaml (pulled from Vault)
  ├── configmap.yaml (environment config)
  ├── api-deployment.yaml (Flask/Express)
  ├── worker-deployment.yaml (Async jobs)
  ├── frontend-deployment.yaml (React SPA)
  ├── redis-statefulset.yaml
  ├── postgresql-statefulset.yaml (or use managed DB)
  ├── services.yaml (Kubernetes Services)
  ├── ingress.yaml (Nginx Ingress Controller)
  ├── hpa.yaml (Horizontal Pod Autoscaler)
  └── pdb.yaml (Pod Disruption Budget)
  ```
- [ ] Resource specifications:
  - Backend API:
    - CPU: request 500m, limit 1000m
    - Memory: request 512Mi, limit 1Gi
    - Replicas: 3 (high availability)
  - Frontend:
    - CPU: request 100m, limit 500m
    - Memory: request 128Mi, limit 256Mi
    - Replicas: 2
  - Worker:
    - CPU: request 250m, limit 500m
    - Memory: request 256Mi, limit 512Mi
    - Replicas: 2 (scale to 5 if queue backlog)
- [ ] Auto-scaling:
  - HPA: Scale API pods when CPU > 70%
  - Min replicas: 3, Max: 10
  - Scale worker pods on queue depth
- [ ] Health checks:
  - Liveness probe: `/health/live` (returns 200)
  - Readiness probe: `/health/ready` (checks dependencies)
- [ ] Network policies:
  - Ingress: Only HTTPS allowed
  - Egress: Whitelist external APIs (OpenAI, Google Cloud, etc.)
- [ ] Storage:
  - Persistent volumes for database (if self-hosted)
  - Use managed services (RDS, CloudSQL) for production
- [ ] Test: Deploy to staging K8s cluster, verify all services running

**Files:**
- `k8s/` (Kubernetes manifests)
- `docker/Dockerfile.backend`
- `docker/Dockerfile.frontend`
- `docker/Dockerfile.worker`
- `docker/.dockerignore`

---

### 4.7 CI/CD Pipeline Configuration
**Effort:** 5 hours | **Priority:** CRITICAL | **Depends on:** 1.1

**Description:**
Set up complete CI/CD pipeline: test → build → push → deploy (with canary strategy).

**Acceptance Criteria:**
- [ ] GitHub Actions workflows:
  ```
  .github/workflows/
  ├── test.yml (Run all tests on PR)
  ├── lint.yml (Code quality checks)
  ├── security.yml (SAST + DAST scan)
  ├── build.yml (Build Docker images)
  ├── deploy-staging.yml (Deploy to staging on merge)
  └── deploy-prod.yml (Canary deploy to prod)
  ```
- [ ] Test stage (on every PR):
  - Unit tests: pytest --cov=src
  - Integration tests: Full test suite
  - Coverage report: Fail if < 90%
  - Lint: Black, isort, pylint
  - Type check: mypy
  - Dependencies: security audit (pip-audit)
- [ ] Build stage (on PR + main):
  - Build Docker images
  - Scan images for vulnerabilities (Trivy)
  - Push to container registry (ECR / GCR)
  - Tag: `backend:v1.2.3` + `backend:latest`
- [ ] Deploy-to-staging stage (on main merge):
  - Automatic deploy to staging K8s cluster
  - Run full E2E test suite
  - Performance benchmarks
  - Accessibility audit
  - Fail deployment if any test fails
- [ ] Deploy-to-prod stage (manual trigger):
  - Canary deployment: 5% traffic to new version
  - Monitor error rate + latency for 10 min
  - Ramp to 50% traffic if healthy
  - Ramp to 100% traffic after 30 min
  - Rollback ready (< 5 min)
- [ ] Notifications:
  - Slack notifications for test failure
  - Deployment status (staging + prod)
  - Alert on rollback
- [ ] Test: Run full pipeline on dummy commit

**Files:**
- `.github/workflows/` (GitHub Actions workflows)
- `Makefile` (Helper commands)
- `scripts/deploy.sh` (Deployment scripts)

**Example Workflow:**
```yaml
name: Test & Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
      
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install black isort pylint
      - run: black --check src/ tests/
      - run: isort --check-only src/ tests/
```

---

### 4.8 Production Monitoring & Alerting
**Effort:** 5 hours | **Priority:** CRITICAL | **Depends on:** 1.7, 4.6

**Description:**
Set up comprehensive monitoring (Prometheus + Grafana), alerting (Alertmanager), logging (ELK), tracing (Jaeger).

**Acceptance Criteria:**
- [ ] Metrics collection (Prometheus):
  - Application metrics: request latency, error rate, queue depth
  - Infrastructure: CPU, memory, disk, network
  - Database: query latency, active connections
  - External APIs: availability, latency
- [ ] Dashboards (Grafana):
  - Service health dashboard
  - Error rate + latency P50/P95/P99
  - Active users + throughput
  - External API health
  - Database performance
  - Cache hit rate
- [ ] Alert rules:
  - Critical: Error rate > 1% for 5 min
  - Critical: Chat latency P95 > 3s for 5 min
  - High: Any service unavailable for 1 min
  - High: External API error rate > 10% for 5 min
  - Medium: Database query latency > 1s for 10 min
  - Medium: Cache hit rate < 60%
- [ ] Alerting:
  - Integrate with Slack / email for alert notifications
  - On-call escalation (page engineer if critical)
  - Alert deduplication (avoid spam)
  - Alert resolution workflows
- [ ] Centralized logging (ELK):
  - All service logs aggregated
  - Searchable by user_id, request_id, error_type
  - Retention: 30 days for normal logs, 90 days for errors
  - Alerting on error patterns
- [ ] Distributed tracing (Jaeger):
  - Trace chat request end-to-end (app → RAG → LLM → response)
  - Identify latency bottlenecks
  - Sampling: 10% of requests (cost control)
- [ ] Log levels:
  - DEBUG: Detailed flow traces
  - INFO: User interactions, system events
  - WARNING: Degraded service, unexpected behavior
  - ERROR: Failures requiring investigation
- [ ] Health check endpoint:
  ```
  GET /health
  Returns: {
    "status": "healthy" | "degraded" | "critical",
    "services": {
      "database": "ok" | "slow" | "down",
      "redis": "ok" | "down",
      "llm_api": "ok" | "degraded",
      "vector_db": "ok" | "down"
    },
    "latency_ms": 45
  }
  ```

**Files:**
- `k8s/prometheus-configmap.yaml` (Prometheus scrape config)
- `k8s/alertmanager-configmap.yaml` (Alert rules)
- `monitoring/grafana-dashboards/` (Dashboard JSON)
- `backend/src/monitoring/` (Metrics + logging config)

---

## Completion Checklist

**Track A (Testing):**
- [ ] 4.1: Unit tests > 90% coverage + all tests passing
- [ ] 4.2: Integration tests for all major flows passing
- [ ] 4.3: E2E user journey tests passing + performance within SLA

**Track B (Performance):**
- [ ] 4.4: Load tests passing + SLA compliance verified
- [ ] 4.5: Chaos tests passing + resilience validated

**Track C (Deployment):**
- [ ] 4.6: Kubernetes manifests + Docker images ready
- [ ] 4.7: CI/CD pipeline operational (test → build → deploy)
- [ ] 4.8: Monitoring + alerting active + dashboards visible

---

## Effort Summary
- Total: ~58 hours (8 days)
- Parallelizable: Tracks A & B can run during week 8; Track C during week 9
- Critical path: Testing must pass before deployment

---

## Go-Live Checklist

Before deploying to production:

- [ ] All Phase 4 tasks complete
- [ ] Code coverage > 90%
- [ ] Load test: All SLAs met under 100+ concurrent users
- [ ] Chaos test: System recovers from all failure scenarios
- [ ] Security: SAST scan shows 0 critical vulnerabilities
- [ ] WCAG: Accessibility audit passing
- [ ] Data: Database backed up + restore tested
- [ ] Monitoring: All alerts configured + tested
- [ ] Documentation: Runbooks + incident procedures documented
- [ ] Team training: On-call team trained on monitoring + runbooks
- [ ] Stakeholder approval: Product + leadership sign-off
- [ ] Gradual rollout:
  - Week 1: 1000 users (internal + close partners)
  - Week 2: 10K users
  - Week 3: 50K users
  - Week 4+: General availability

---

**Last Updated:** 2026-07-11

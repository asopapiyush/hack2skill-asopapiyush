# Phase 2: Core Features (Weeks 3-5)

**Objective:** Implement RAG + safety guardrails, chat service, planning engine, travel advisories, recovery guidance.

**Dependencies:** Phase 1 must be complete

**Parallel Tracks:**
- Track A: RAG guardrails (2.1-2.2)
- Track B: Chat service (2.3)
- Track C: Planning engine (2.4)
- Track D: Travel advisories (2.5)
- Track E: Recovery guidance (2.6)

Tasks in different tracks can run in parallel; within a track, follow sequence.

---

## Track A: RAG & Safety (Priority: CRITICAL)

### 2.1 RAG Pipeline & Vector Retrieval
**Effort:** 8 hours | **Priority:** CRITICAL | **Depends on:** 1.4

**Description:**
Implement semantic search pipeline: query encoding → vector DB lookup → document ranking by relevance + trust score.

**Acceptance Criteria:**
- [ ] `RagService` class implemented:
  - `async def search(query: str, top_k: int = 5, filters: dict = None) -> List[Document]`
  - Encode query using OpenAI embeddings API
  - Search Pinecone vector index
  - Rank results by relevance + trust_score metadata
  - Filter by region/category if provided
- [ ] Hybrid search implemented:
  - Semantic search (embedding similarity)
  - Keyword search (BM25) for hard-stop keywords like "drowning", "electrocution"
  - Result merging strategy (take top 3 semantic + top 2 keyword)
- [ ] Retrieval test cases:
  - Query: "Water entering my house" → Returns water flooding protocols (top-1 relevance > 0.9)
  - Query: "Heavy rain" → Returns rainfall emergency protocols (region-filtered)
  - Query: "Drowning" → Returns keyword match even if embedding similarity low
- [ ] Latency: Retrieval < 500ms (P95)
- [ ] Test: 10 sample queries with expected results

**Files:**
- `backend/src/services/rag_service.py`
- `backend/tests/integration/test_rag_retrieval.py`
- `backend/src/external/vector_db.py` (update with hybrid search)

**Initial Test Queries:**
```
1. "Water is entering my house, what do I do?" 
   → Expected: flood response protocols
2. "My child has fever, is it safe?" 
   → Expected: waterborne disease + health safety
3. "How to protect my documents?" 
   → Expected: document preservation + waterproofing
4. "Drowning emergency help" 
   → Expected: HARD-STOP escalation
```

---

### 2.2 Safety Guardrails & Hard-Stop Responses
**Effort:** 6 hours | **Priority:** CRITICAL | **Blocks:** 2.3

**Description:**
Implement three-layer guardrail engine: keyword detection → semantic safety check → injection detection.

**Acceptance Criteria:**
- [ ] Hard-stop keywords defined + mapped to handlers:
  - "drowning" → emergency_response_drowning()
  - "electrocution" → emergency_response_electrocution()
  - "fire" → emergency_response_fire()
  - "snake_bite" → emergency_response_snake_bite()
  - "childbirth" → escalate_to_hospital()
  - "heart_attack" → escalate_to_emergency()
- [ ] Pre-approved responses for each hard-stop (pre-written, verified by domain experts)
- [ ] Semantic safety check:
  - Load "unsafe patterns" into vector DB
  - Score LLM response similarity to unsafe patterns
  - If similarity > 0.7, return generic fallback
- [ ] Injection detection:
  - Scan response for "ignore previous instructions", "system role is now", etc.
  - If found, return generic fallback
- [ ] Escalation protocol:
  - If unsafe detected, escalate to human advisor (on-call team)
  - Log incident for review
- [ ] Test cases:
  - Query: "I'm drowning" + any LLM response → Returns emergency response (safety="escalated")
  - Query: "Weather question" + unsafe LLM response → Returns fallback (safety="fallback")
  - Query: "Weather question" + good LLM response → Returns LLM response (safety="safe")
- [ ] All 6 hard-stop scenarios tested
- [ ] Edge case: Empty/null LLM response → Return generic fallback

**Files:**
- `backend/src/services/guardrail_engine.py` (GuardrailEngine class)
- `backend/src/data/hard_stop_responses.json` (Pre-approved responses)
- `backend/tests/unit/services/test_guardrail_engine.py`
- `backend/tests/unit/services/test_injection_detection.py`

**Hard-Stop Response Template:**
```python
def _handle_drowning(self) -> str:
    return """
    🚨 EMERGENCY
    Call local rescue services immediately:
    - Fire (rescue): 101
    - Ambulance: 102
    - Police: 100
    - Disaster Management: 1070
    
    Steps while waiting:
    1. DO NOT attempt self-rescue if you cannot swim
    2. Move to highest available ground
    3. Signal for help (shout, wave)
    """
```

---

## Track B: Chat Service (Priority: HIGH)

### 2.3 Chat Message Handler & Intent Classification
**Effort:** 8 hours | **Priority:** HIGH | **Depends on:** 2.2, 1.5

**Description:**
Implement chat service with intent classifier, response generation via RAG + LLM, safety validation.

**Acceptance Criteria:**
- [ ] `ChatService` class:
  - `async def handle_message(user_id, message, language, is_voice=False) -> dict`
  - Returns: `{response, intent, escalation_flag, latency_ms}`
- [ ] Intent classifier:
  - 5 intents: "emergency", "preparedness", "travel_advisory", "recovery", "faq"
  - Keyword matching + NLP fallback
  - Confidence score > 0.6 required
- [ ] Response generation pipeline:
  - Classify intent
  - Retrieve RAG documents
  - Build LLM prompt with context
  - Generate response (GPT-4 Turbo, temp=0.1)
  - Validate with guardrails
  - Return to user
- [ ] Context-aware responses:
  - User region, family size, health conditions available
  - Customize advice per user context
- [ ] Latency SLA: < 2 seconds (P95)
- [ ] Test cases:
  - Emergency: "Water entering" → "emergency" intent + escalation_flag=true
  - Preparedness: "What should I stock?" → "preparedness" intent + relevant checklist
  - Travel: "Is it safe to drive?" → "travel_advisory" intent + route safety score
  - Recovery: "How to clean after flood?" → "recovery" intent + cleanup protocol
  - FAQ: "When does monsoon start?" → "faq" intent + informational response
- [ ] Chat history logged (user_id, message, response, intent, timestamp)

**Files:**
- `backend/src/services/chat_service.py`
- `backend/src/services/intent_classifier.py`
- `backend/src/api/routes/chat.py` (API endpoints)
- `backend/tests/integration/test_chat_service.py`
- `backend/tests/integration/test_intent_classification.py`

**API Endpoint:**
```
POST /api/chat/message
Input: {user_id, message, language, is_voice}
Output: {response, intent, escalation_flag, latency_ms}
SLA: < 2s
```

---

### 2.4 Speech-to-Text (STT) Integration
**Effort:** 5 hours | **Priority:** HIGH | **Depends on:** 1.6

**Description:**
Integrate Google Cloud Speech-to-Text for voice input with regional language support.

**Acceptance Criteria:**
- [ ] STT client configured:
  - Supports: Hindi (hi-IN), Marathi (mr-IN), Tamil (ta-IN), Telugu (te-IN), Kannada (kn-IN), English (en-IN)
  - Audio format: LINEAR16, 16kHz, mono
  - Enhanced mode enabled (better accuracy for accents)
- [ ] `async def transcribe_audio(audio_blob: bytes, language: str) -> str`
- [ ] Confidence threshold: < 0.6 → Ask user to repeat or type instead
- [ ] Timeout: > 30s → Fallback to text input
- [ ] Language detection mismatch: Offer language selection
- [ ] Test cases:
  - Valid Hindi speech → Correct transcription
  - Low confidence speech → Request repeat
  - Timeout → Graceful fallback
  - Language mismatch → Auto-correct or ask user
- [ ] Latency: < 3 seconds for typical message

**Files:**
- `backend/src/external/speech_service.py` (STT client)
- `backend/src/api/routes/chat.py` (voice endpoint)
- `backend/tests/integration/test_stt.py`

**API Endpoint:**
```
POST /api/chat/voice
Input: {user_id, audio_blob, language}
Output: {transcription, response, confidence}
SLA: < 5s (STT + LLM + TTS)
```

---

### 2.5 Text-to-Speech (TTS) Integration
**Effort:** 4 hours | **Priority:** HIGH | **Depends on:** 1.6, 2.3

**Description:**
Integrate Google Cloud Text-to-Speech with voice customization (speed, pitch, gender).

**Acceptance Criteria:**
- [ ] TTS client configured:
  - Supports: 6 languages + regional voices
  - Voice names: e.g., "hi-IN-Neural2-A" (Hindi, female)
  - Audio encoding: LINEAR16
  - Speaking rate: 0.5 to 2.0x (default 0.95 for clarity)
  - Pitch: -20 to +20
- [ ] `async def synthesize_response(text: str, language: str, voice_settings: dict) -> bytes`
- [ ] Voice customization per user:
  - Gender: MALE, FEMALE, NEUTRAL
  - Speaking rate: User-adjustable
  - Pitch: User-adjustable
  - Volume: User-adjustable
- [ ] Spell-out mode for critical info:
  - Emergency numbers spelled character-by-character
  - Location names spelled out
- [ ] Test cases:
  - Simple message → Correct pronunciation + pacing
  - Emergency response → Slower, clearer speech (rate 0.7)
  - Multibyte characters (Hindi) → Correct pronunciation
  - Accessibility settings applied (pitch, rate, volume)

**Files:**
- `backend/src/external/speech_service.py` (update with TTS)
- `backend/src/models/voice_settings.py` (User voice preferences)
- `backend/tests/integration/test_tts.py`

---

## Track C: Planning Engine (Priority: HIGH)

### 2.6 Conversational Onboarding Flow
**Effort:** 6 hours | **Priority:** HIGH | **Depends on:** 2.3

**Description:**
Implement step-by-step questionnaire to gather user context (family size, location, health conditions, pets, budget).

**Acceptance Criteria:**
- [ ] `OnboardingFlow` class:
  - Questions: family_size, location_type, health_conditions, pets, budget
  - Each question has follow-up logic
  - Conversational tone (single question at a time)
  - Can go back/skip (not strict linear)
- [ ] Question types:
  - Number: "How many people?" (validation: 1-20)
  - Choice: "Where do you live?" (radio buttons)
  - Multi-select: "Health conditions?" (checkboxes)
- [ ] Follow-up questions:
  - If family_size > 0 → Ask children_count, elderly_count
  - If health_conditions selected → Ask medications_list
  - If pets selected → Ask pet_count, dietary_restrictions
- [ ] Conversation flow:
  - Send question to user via chat
  - User responds
  - Validate response
  - If invalid, re-ask with error message
  - Store answers in DB
- [ ] Completion: User can review + edit answers before finalizing
- [ ] Test: Complete full onboarding flow (5-10 min conversation)

**Files:**
- `backend/src/services/onboarding_service.py`
- `backend/src/api/routes/onboarding.py`
- `backend/tests/integration/test_onboarding_flow.py`

**API Endpoints:**
```
POST /api/onboarding/start → Get first question
POST /api/onboarding/answer → Submit answer, get next question
GET /api/onboarding/review → Review all answers
POST /api/onboarding/submit → Finalize onboarding
```

---

### 2.7 LLM-Based Plan Generation
**Effort:** 8 hours | **Priority:** HIGH | **Depends on:** 2.6, 2.1, 2.2

**Description:**
Generate customized 7-day preparedness checklist based on user context via LLM + RAG.

**Acceptance Criteria:**
- [ ] `PlanGenerationService` class:
  - `async def generate_plan(user_context: dict) -> dict`
  - Inputs: family_size, health_conditions, location_type, pets, budget
- [ ] LLM prompt construction:
  - Include user context
  - Include retrieved monsoon protocols from RAG
  - Instructions for 7-day timeline + prioritization
- [ ] Plan structure:
  ```json
  {
    "plan_id": "plan_abc123",
    "days": [
      {
        "day": 1,
        "theme": "Securing Your Home",
        "tasks": [
          {
            "task": "Secure insulin in waterproof container",
            "priority": "CRITICAL",
            "time_estimate": "15min",
            "notes": "For diabetic family members"
          }
        ]
      }
    ],
    "shopping_list": [
      {
        "item": "Waterproof container",
        "quantity": 5,
        "estimated_cost": 500,
        "priority": "CRITICAL"
      }
    ],
    "estimated_total_cost": 5000,
    "health_specific_notes": {"diabetes": "..."},
    "location_specific_risks": ["Ground floor → water entry", "..."]
  }
  ```
- [ ] Health-specific customization:
  - Diabetes: Insulin storage, glucose monitoring
  - Asthma: Inhalers, spacer, peak flow meter
  - Pregnancy: Prenatal records, medications, labor contacts
  - Mobility issues: Evacuation assistance, accessible shelters
- [ ] Location-specific customization:
  - Ground floor: Water pumps, sandbags, wall waterproofing
  - High-rise: Emergency descents, window safety, water storage
- [ ] Budget impact:
  - Low budget (< ₹2000): DIY solutions, prioritize essentials
  - Moderate (₹2000-5000): Mix of commercial + DIY
  - Flexible (> ₹5000): Premium equipment, redundancy
- [ ] Test cases:
  - 5-person family + diabetes + apartment → Plan includes insulin + water storage
  - Elderly + mobility issues → Plan emphasizes assistance + shelter info
  - Single person + ground floor → Plan focuses on water protection
- [ ] Latency: < 10 seconds (LLM inference)
- [ ] Plan stored in DB + cached for 24 hours

**Files:**
- `backend/src/services/plan_service.py`
- `backend/src/api/routes/plans.py`
- `backend/tests/integration/test_plan_generation.py`

**API Endpoint:**
```
POST /api/plans/generate
Input: {user_id, family_size, location_type, health_conditions, pets, budget}
Output: {plan_id, plan}
SLA: < 10s
```

---

### 2.8 Dynamic Plan Updates & Threat Escalation
**Effort:** 5 hours | **Priority:** HIGH | **Depends on:** 2.7, 2.1

**Description:**
Update plan dynamically when threat level escalates or user context changes.

**Acceptance Criteria:**
- [ ] Threat levels:
  - "normal" → routine preparations, low urgency
  - "warning" → prioritize water storage, fuel, documents
  - "alert" → prioritize evacuation kit, vehicle fuel
  - "severe" → prioritize immediate evacuation, critical items only
- [ ] `async def update_plan_for_threat(plan_id, threat_level) -> dict`
- [ ] When threat escalates:
  - Regenerate plan with new threat level
  - Reprioritize tasks (move CRITICAL to top)
  - Adjust time estimates (compress timeline)
  - Notify user of changes
- [ ] User context changes:
  - Added health condition → Update relevant tasks
  - Family size increased → Update quantity estimates
  - Budget changed → Update shopping list
- [ ] Test cases:
  - Threat: normal → warning: "Water storage" task moves to Day 1
  - Context: Add diabetes: Insulin waterproofing added to Day 1
  - Context: Family size 4 → 6: Shopping quantities increase
- [ ] User notification when plan changes

**Files:**
- `backend/src/services/plan_service.py` (update)
- `backend/tests/integration/test_plan_updates.py`

---

## Track D: Travel Advisories (Priority: MEDIUM)

### 2.9 Real-Time Weather & Traffic Data Fusion
**Effort:** 7 hours | **Priority:** MEDIUM | **Depends on:** 1.4, 1.6

**Description:**
Fetch and fuse real-time weather, traffic, alerts, and flood maps to assess route safety.

**Acceptance Criteria:**
- [ ] External API integrations:
  - Weather API (IMD or AccuWeather): rainfall, wind, lightning risk
  - Maps API (Google Maps): route options, traffic density
  - Flood alert system (local or government): water level, evacuation zones
  - Traffic API: estimated duration, incidents
- [ ] Data model:
  ```python
  class RouteData:
      segments: List[Segment]
      estimated_duration_min: int
      baseline_duration_min: int
      traffic_density: str  # "light" | "moderate" | "heavy"
      weather: WeatherData
      active_alerts: List[Alert]
      flood_risk_per_segment: List[FloodRisk]
  ```
- [ ] Multi-factor safety scoring:
  - Rainfall impact: > 100mm/hr → 20% safety reduction
  - Wind speed: > 50km/hr → 30% reduction
  - Lightning risk: high → 40% reduction
  - Flood risk: critical → 80% reduction
  - Traffic gridlock (2x baseline) → 20% reduction
  - User-specific (elderly, children, disabled) → 10% reduction
- [ ] Score calculation: Start at 1.0, apply multipliers, clamp to [0, 1]
- [ ] Latency: < 1 second (P95) for data fusion
- [ ] Test cases:
  - Normal weather + light traffic → score > 0.8
  - Heavy rain + flooded zone → score < 0.3
  - Good weather + user has mobility issues + highway required → score reduced

**Files:**
- `backend/src/services/travel_advisory_service.py`
- `backend/src/external/weather_api.py`
- `backend/src/external/maps_api.py`
- `backend/tests/integration/test_route_scoring.py`

---

### 2.10 Travel Advisory Generation & Delivery
**Effort:** 6 hours | **Priority:** MEDIUM | **Depends on:** 2.9, 2.1, 2.2

**Description:**
Generate safe route recommendations with narrative advice, alternative routes, shelter locations.

**Acceptance Criteria:**
- [ ] `async def generate_advisory(origin, destination, user_context) -> dict`
- [ ] Output structure:
  ```json
  {
    "recommendation": "safe_to_travel" | "consider_alternate" | "shelter_in_place",
    "primary_route": {...},
    "alternative_routes": [...],
    "safety_score": 0.85,
    "narrative_advice": "Turn left at marker, avoid bridge (flooded), shelter at...",
    "shelters_nearby": [...],
    "refresh_interval_seconds": 600,
    "emergency_contacts": [...]
  }
  ```
- [ ] Narrative generation:
  - Step-by-step navigation (landmarks, not just GPS)
  - Monsoon-specific warnings (flooded roads, power lines, debris)
  - Alternative routes ranked by safety
  - Shelter locations if route becomes impassable
- [ ] Shelter finder:
  - Nearby government shelters + capacity
  - Contact info + distance from route
- [ ] User context influence:
  - Elderly → Avoid steep hills, long distances
  - Children → Avoid highways, risky intersections
  - Disabled → Only wheelchair-accessible routes
- [ ] API + WebSocket:
  - REST: POST /api/advisories → Get advisory once
  - WebSocket: /ws/advisories/{user_id} → Stream updates every 10 min or on change
- [ ] Test cases:
  - Safe route: "safe_to_travel" + clear navigation
  - Risky route: "consider_alternate" + alternatives provided
  - Very unsafe: "shelter_in_place" + nearby shelters

**Files:**
- `backend/src/services/travel_advisory_service.py` (update)
- `backend/src/api/routes/advisories.py`
- `backend/src/api/websocket_handlers/advisories.py`
- `backend/tests/integration/test_travel_advisory.py`

---

## Track E: Recovery Guidance (Priority: LOW)

### 2.11 Post-Event Recovery Checklist Generation
**Effort:** 5 hours | **Priority:** LOW | **Depends on:** 2.1, 2.2

**Description:**
Generate recovery guidance for post-flood cleanup, health monitoring, insurance claims, structural assessment.

**Acceptance Criteria:**
- [ ] Damage types:
  - "flooding" (water damage to home)
  - "electrical" (electrical hazards)
  - "structural" (building damage)
  - "contamination" (water purity concerns)
- [ ] Severity levels:
  - "minor": Small water ingress, quick cleanup
  - "moderate": Extensive water damage, potential health risks
  - "severe": Structural damage, immediate safety concerns
- [ ] Recovery plan structure:
  ```json
  {
    "immediate_health_safety": [...],
    "cleanup_protocol": [...],
    "disease_monitoring": [...],
    "insurance_documentation": [...],
    "structural_assessment": [...],
    "timeline_to_normalcy": "..."
  }
  ```
- [ ] Health-specific recovery:
  - Diabetes: Monitor blood sugar, replace medications
  - Pregnancy: Prenatal checkup, stress management
  - Asthma: Check inhalers, avoid mold exposure
- [ ] Cleanup phases:
  - Day 1: Safety assessment, turn off utilities
  - Days 2-3: Remove water, start disinfection
  - Days 4-7: Mold prevention, document damage
  - Week 2+: Insurance claims, structural repair
- [ ] Test: Generate recovery plan for moderate flooding + diabetic family

**Files:**
- `backend/src/services/recovery_service.py`
- `backend/src/api/routes/recovery.py`
- `backend/tests/integration/test_recovery_generation.py`

---

## Completion Checklist

**Track A (RAG & Safety):**
- [ ] 2.1: RAG retrieval working + < 500ms latency
- [ ] 2.2: All hard-stops tested + guardrails functional

**Track B (Chat):**
- [ ] 2.3: Intent classification + LLM response generation working
- [ ] 2.4: STT transcription working + language support verified
- [ ] 2.5: TTS synthesis working + voice customization available

**Track C (Planning):**
- [ ] 2.6: Onboarding flow complete + all follow-up questions working
- [ ] 2.7: Plan generation working + health/location customization verified
- [ ] 2.8: Plan updates + threat escalation working

**Track D (Advisories):**
- [ ] 2.9: Route scoring working + multi-factor safety assessment verified
- [ ] 2.10: Advisory generation + WebSocket streaming working

**Track E (Recovery):**
- [ ] 2.11: Recovery guidance generation working for all damage types

---

## Effort Summary
- Total: ~63 hours (8-9 days)
- Parallelizable: All 5 tracks can run independently after Phase 1
- Critical path: Track A must complete before Track B (guardrails needed for chat)

---

**Last Updated:** 2026-07-11

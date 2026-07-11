# Phase 3: Accessibility & Polish (Weeks 6-7)

**Objective:** Implement multilingual support, voice accessibility, WCAG 2.1 AA compliance, SMS/WhatsApp integration.

**Dependencies:** Phase 2 must be complete

**Parallel Tracks:**
- Track A: Multilingual localization (3.1-3.2)
- Track B: Voice accessibility (3.3-3.4)
- Track C: UI/UX accessibility (3.5)
- Track D: SMS/WhatsApp integration (3.6-3.7)

---

## Track A: Multilingual Localization (Priority: HIGH)

### 3.1 Multilingual String Extraction & Translation Framework
**Effort:** 5 hours | **Priority:** CRITICAL | **Depends on:** 2.3

**Description:**
Extract all UI/API strings into translation files (6 languages: Hindi, Marathi, Tamil, Telugu, Kannada, English).

**Acceptance Criteria:**
- [ ] Translation framework:
  - Use Flask-Babel (Python) or i18next (Node.js)
  - JSON translation files: `locales/{language}.json`
  - Support for pluralization, variable substitution
- [ ] Extract all strings from:
  - Backend API responses (chat, plans, advisories)
  - Frontend UI (buttons, labels, error messages)
  - Email notifications, SMS content
- [ ] Translation keys organized by domain:
  ```
  locales/
  ├── en.json (English)
  ├── hi.json (Hindi)
  ├── mr.json (Marathi)
  ├── ta.json (Tamil)
  ├── te.json (Telugu)
  └── kn.json (Kannada)
  
  With keys:
  {
    "onboarding": {...},
    "emergency": {...},
    "planning": {...},
    "chat": {...},
    "errors": {...}
  }
  ```
- [ ] Dynamic language selection:
  - User preference (if logged in)
  - Browser Accept-Language header
  - Geolocation-based (region → default language)
- [ ] Fallback chain: User preference → Browser → Region → English
- [ ] Test: Change language → All strings update, no missing translations

**Files:**
- `backend/src/services/localization_service.py`
- `backend/src/utils/i18n.py` (i18n utilities)
- `backend/locales/` (translation JSON files)
- `frontend/src/locales/` (same structure)
- `backend/tests/integration/test_localization.py`

**Key Strings to Translate:**
- Onboarding questions
- Emergency responses
- Plan task descriptions
- Travel advisory recommendations
- Error messages
- UI labels (buttons, form fields)

---

### 3.2 Regional Language Support & Auto-Detection
**Effort:** 4 hours | **Priority:** HIGH | **Depends on:** 3.1, 2.4

**Description:**
Auto-detect user language from browser, geolocation, or device settings. Support regional dialect variations.

**Acceptance Criteria:**
- [ ] Language auto-detection pipeline:
  ```python
  async def detect_user_language(request) -> str:
      # 1. User preference (DB)
      # 2. Browser Accept-Language
      # 3. Geolocation IP → region → default language
      # 4. Fallback to English
  ```
- [ ] Regional dialect support:
  - Hindi: Standard (hi-IN)
  - Marathi: Regional variations (accent-friendly for STT)
  - Tamil: Tamil Nadu region
  - Telugu: Andhra Pradesh region
  - Kannada: Karnataka region
- [ ] Dialect-specific STT models:
  - Each language model trained on regional accents
  - STT confidence > 0.6 required
- [ ] Store user language preference + allow override
- [ ] Test cases:
  - Browser: Accept-Language: hi-IN → Auto-select Hindi
  - Browser: Accept-Language: en-US → Auto-select English
  - User without preference + IP from Maharashtra → Auto-select Marathi
  - User changes language preference → Immediately reflected

**Files:**
- `backend/src/services/localization_service.py` (update)
- `backend/tests/integration/test_language_detection.py`

---

## Track B: Voice Accessibility (Priority: HIGH)

### 3.3 Voice Command Handler & Hands-Free Navigation
**Effort:** 6 hours | **Priority:** HIGH | **Depends on:** 2.5, 3.1

**Description:**
Implement voice commands for users with motor disabilities (hands-free operation).

**Acceptance Criteria:**
- [ ] Voice commands:
  - "next step" → Advance to next checklist task
  - "previous" → Go back one step
  - "skip" → Jump current task
  - "call emergency" → Initiate emergency call
  - "repeat" → Repeat last instruction
  - "menu" → Open main menu
  - "help" → Show available commands
  - "yes" / "no" → Confirm/deny prompts
- [ ] Command recognition:
  - Match transcribed text against command list
  - Fuzzy matching (handle slight mispronunciations)
  - Confidence threshold > 0.7
- [ ] Voice-guided checklist:
  - Announce step verbally
  - Wait for "yes" confirmation
  - Move to next step automatically or on command
  - Progress announcements ("3 steps remaining")
- [ ] Accessibility UI:
  - Voice control indicator (listening/waiting)
  - Visual confirmation of recognized commands
  - Adjustable speaking rate + volume
- [ ] Test cases:
  - User says "next step" → Advances checklist
  - User says "help" → Lists available commands with TTS
  - User says "call emergency" → Dials emergency number
  - Misheard command → Repeat confirmation request

**Files:**
- `backend/src/services/voice_command_service.py`
- `backend/src/models/voice_commands.py` (Command definitions)
- `backend/tests/unit/services/test_voice_commands.py`

---

### 3.4 User-Customizable Voice Settings
**Effort:** 3 hours | **Priority:** HIGH | **Depends on:** 2.5

**Description:**
Allow users to customize TTS output (speed, pitch, volume, gender) for accessibility.

**Acceptance Criteria:**
- [ ] Voice settings per user:
  ```python
  class VoiceSettings:
      gender: str = "NEUTRAL"  # MALE, FEMALE, NEUTRAL
      speaking_rate: float = 0.95  # 0.5 (slow) to 2.0 (fast)
      pitch: int = 0  # -20 to +20
      volume: int = 0  # -16 to +16
      enable_spell_out: bool = False  # Spell emergency numbers
  ```
- [ ] Settings stored in user profile + applied to all TTS
- [ ] Preset profiles:
  - "Default" (0.95 rate, neutral pitch)
  - "Slow & Clear" (0.7 rate, lower pitch)
  - "Fast" (1.3 rate, normal pitch)
  - "Custom" (user-adjustable)
- [ ] UI to adjust settings:
  - Sliders for rate, pitch, volume
  - Toggle for spell-out mode
  - Preview button: "Hear sample"
- [ ] Test: Change settings → TTS output reflects changes

**Files:**
- `backend/src/models/user_settings.py`
- `backend/src/api/routes/settings.py` (User settings endpoints)
- `frontend/src/components/VoiceSettings.tsx` (UI component)
- `backend/tests/integration/test_voice_settings.py`

---

## Track C: UI/UX Accessibility (Priority: CRITICAL)

### 3.5 WCAG 2.1 AA Compliance Across All Features
**Effort:** 8 hours | **Priority:** CRITICAL | **Depends on:** 2.3, 2.7

**Description:**
Audit and fix all features for WCAG 2.1 AA compliance: color contrast, keyboard navigation, ARIA labels, focus management.

**Acceptance Criteria:**
- [ ] Color contrast (WCAG 1.4.3):
  - Text on background: 4.5:1 (normal text) or 3:1 (large text 18px+)
  - Form borders: 3:1 minimum
  - All icons have sufficient contrast
- [ ] Keyboard navigation (WCAG 2.1.1):
  - All interactive elements accessible via Tab key
  - No keyboard trap (can always tab out)
  - Logical tab order (top-to-bottom, left-to-right)
  - Focus ring visible (outline-width: 2px, outline-color: high-contrast)
- [ ] Form labels (WCAG 3.3.2):
  - Every input has associated `<label>` element
  - Labels visible (not hidden)
  - Label text matches screen reader text
- [ ] ARIA attributes (WCAG 4.1.2):
  - `aria-label` for icon buttons
  - `aria-describedby` for complex fields
  - `aria-live="polite"` for dynamic content (chat messages)
  - `aria-expanded` for collapsibles
  - `aria-hidden="true"` for decorative elements
- [ ] Semantic HTML:
  - Use `<button>` for buttons, not `<div onclick>`
  - Use `<fieldset>` + `<legend>` for form groups
  - Use `<nav>` for navigation
  - Proper heading hierarchy (h1 → h2 → h3, no skips)
- [ ] Focus management:
  - Focus moves to new content when opened (modal, message)
  - Focus returns to trigger element when closed
  - Skip links for main content (skip navigation)
- [ ] Error messages (WCAG 3.3.1):
  - Clearly identify invalid field
  - Suggest how to fix
  - Use color + text (not color alone)
  - Associated with input via `aria-describedby`
- [ ] Accessibility audit tools:
  - axe DevTools (automated scan)
  - WAVE (WebAIM) for manual review
  - Keyboard-only testing (disable mouse)
  - Screen reader testing (NVDA, JAWS)
- [ ] Test checklist:
  - [ ] Navigate entire app via keyboard only
  - [ ] All form fields have labels
  - [ ] Color contrast >= 4.5:1 for all text
  - [ ] Icon buttons have aria-labels
  - [ ] Chat messages announced via aria-live
  - [ ] Error messages clear + actionable
  - [ ] Focus visible everywhere
  - [ ] No keyboard traps

**Files:**
- `frontend/src/components/` (all components audited + fixed)
- `frontend/src/styles/accessibility.css` (Focus styles, contrast fixes)
- `frontend/tests/accessibility/` (Accessibility test suite)
- `backend/tests/accessibility/` (API response accessibility tests)

**Example Fixes:**
```html
<!-- ❌ Bad -->
<div onclick="selectOption('apartment')">Apartment</div>

<!-- ✅ Good -->
<fieldset>
  <legend>Where do you live?</legend>
  <label>
    <input type="radio" name="location" value="apartment" aria-label="Apartment low-rise">
    Apartment (low-rise)
  </label>
</fieldset>

<!-- ❌ Bad: No label -->
<input type="text" placeholder="Enter family size">

<!-- ✅ Good: Explicit label -->
<label for="family_size">How many people in your household?</label>
<input type="number" id="family_size" min="1" max="20">

<!-- ❌ Bad: Color only -->
<span style="color: red">This field is required</span>

<!-- ✅ Good: Color + text + ARIA -->
<span id="error_message" class="error-text" role="alert">
  ❌ This field is required
</span>
<input aria-describedby="error_message" aria-invalid="true">
```

---

## Track D: SMS & WhatsApp Integration (Priority: MEDIUM)

### 3.6 Twilio SMS & WhatsApp Setup
**Effort:** 5 hours | **Priority:** MEDIUM | **Depends on:** 2.3, 1.6

**Description:**
Integrate Twilio for SMS + WhatsApp message delivery, enabling users to interact via these platforms.

**Acceptance Criteria:**
- [ ] Twilio account configured:
  - SMS phone number provisioned (Indian number)
  - WhatsApp Business Account linked
  - API credentials secured in Vault
- [ ] Webhook handler for incoming messages:
  ```python
  @app.post("/webhooks/twilio/sms")
  async def handle_sms(request: dict):
      user_id = request["From"]  # Phone number
      message = request["Body"]
      language = detect_language(message)
      
      response = await handle_user_message(user_id, message, language)
      
      await twilio_client.send_message(
          to=user_id,
          body=response,
          channel="sms"
      )
  ```
- [ ] WhatsApp handler:
  ```python
  @app.post("/webhooks/twilio/whatsapp")
  async def handle_whatsapp(request: dict):
      user_id = request["From"]  # Phone number
      message = request["Body"]
      
      response = await handle_user_message(user_id, message, "auto")  # Auto-detect language
      
      await twilio_client.send_message(
          to=user_id,
          body=response,
          channel="whatsapp"
      )
  ```
- [ ] Message routing:
  - Route inbound SMS/WhatsApp to chat handler
  - Response sent back via same channel
- [ ] Rate limiting per user (SMS cost control):
  - Max 50 SMS per day per user
  - Queue excess messages
- [ ] User linking:
  - Phone number → User ID mapping
  - Allow signup via WhatsApp (phone number + confirmation code)
- [ ] Test cases:
  - Send SMS "Water entering" → Receive emergency response via SMS
  - Send WhatsApp "What to prepare?" → Receive checklist via WhatsApp
  - Verify rate limiting (51st message queued)

**Files:**
- `backend/src/external/twilio_client.py`
- `backend/src/api/webhooks/twilio.py`
- `backend/tests/integration/test_sms_whatsapp.py`

---

### 3.7 Telegram Bot Integration
**Effort:** 4 hours | **Priority:** MEDIUM | **Depends on:** 2.3, 1.6

**Description:**
Set up Telegram bot for chat-based interaction, enabling users without WhatsApp/SMS access.

**Acceptance Criteria:**
- [ ] Telegram bot created:
  - Bot token secured in Vault
  - Webhook configured for message updates
  - Bot commands registered: /start, /help, /plan, /advisory, /emergency
- [ ] Message handler:
  ```python
  @bot.message_handler(func=lambda m: True)
  async def telegram_handler(message):
      user_id = message.chat.id
      text = message.text
      language = detect_language(text)
      
      response = await handle_user_message(user_id, text, language)
      await bot.reply_to(message, response)
  ```
- [ ] Bot commands:
  - `/start` → Welcome + onboarding
  - `/help` → Show available commands
  - `/plan` → Generate preparedness plan
  - `/advisory` → Get travel advisory
  - `/emergency` → Emergency mode (high-contrast, large text)
- [ ] Inline buttons for quick actions:
  - Next step, Previous, Skip, Confirm, Help
  - No typing required (accessibility)
- [ ] Message queuing:
  - Handle rate limiting (Telegram: 30 msg/sec per user)
- [ ] Test cases:
  - User sends "/start" → Receives welcome message
  - User sends "emergency" → Receives emergency checklist via Telegram
  - User clicks button → Action processed correctly

**Files:**
- `backend/src/external/telegram_bot.py`
- `backend/src/api/webhooks/telegram.py`
- `backend/tests/integration/test_telegram.py`

---

## Completion Checklist

**Track A (Multilingual):**
- [ ] 3.1: All strings extracted + translated to 6 languages
- [ ] 3.2: Language auto-detection + regional dialect support working

**Track B (Voice Accessibility):**
- [ ] 3.3: Voice commands implemented + hands-free navigation working
- [ ] 3.4: Voice settings UI + user customization available

**Track C (UI/UX Accessibility):**
- [ ] 3.5: WCAG 2.1 AA compliance verified (axe scan passing, manual testing done)

**Track D (SMS/WhatsApp):**
- [ ] 3.6: Twilio SMS + WhatsApp integration working + tested
- [ ] 3.7: Telegram bot working + commands functional

---

## Effort Summary
- Total: ~35 hours (5 days)
- Parallelizable: All 4 tracks can run independently
- Accessibility auditing should run continuously throughout phase

---

**Last Updated:** 2026-07-11

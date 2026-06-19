# STRIDE Threat Model Assessment: Shopping Assistant Agent

This document details the threat modeling assessment performed on the `shopping-assistant` agent using the STRIDE methodology.

---

## 1. System Boundaries & Architecture
* **Entry Point**: The chat interface (packaged via `App` and hosted via `AdkApp`/`AgentEngineApp` on Vertex AI Agent Runtime).
* **Core Agent**: ReAct-based LLM agent (`Gemini` model `gemini-2.5-flash`) executing system instructions and dispatching tool calls.
* **Tools**: `redeem_discount(code, user_id)` function.
* **Data Storage**: In-memory Python dictionary (`DISCOUNT_CODES`) containing discount value, redemption state, and owner user ID.

---

## 2. STRIDE Evaluation

### 👤 Spoofing (Identity Spoofing)
* **Threat**: An attacker could pretend to be another registered customer and redeem a single-use discount code on their behalf.
* **Assessment**: **HIGH RISK**. The `redeem_discount` tool only performs a basic check to ensure `user_id` is a non-empty string. It does not authenticate the user or verify that the user ID provided belongs to the active session owner.
* **Mitigation**: Integrate actual user session authentication. The application/runtime should inject the verified `user_id` from the session context directly into the tool call arguments instead of relying on the LLM to ask the user and pass the ID manually.

### ✍️ Tampering (Data/State Manipulation)
* **Threat**: Users manipulating arguments to redeem unassigned codes or reuse codes.
* **Assessment**: **MEDIUM RISK**. The in-memory state correctly sets `record["redeemed"] = True` to prevent replay attacks, but the in-memory database resets on every application restart. Furthermore, prompt injection could bypass prompt instructions to query/manipulate discount state.
* **Mitigation**: Persist discount data in a secure, external database (e.g., Firestore or Cloud SQL) with transaction locks to prevent race conditions. Sanitize and strictly validate LLM-passed tool parameters using Pydantic.

### 📜 Repudiation (Audit Trail/Logging)
* **Threat**: A user claims they never redeemed a discount code, and the system cannot prove otherwise.
* **Assessment**: **MEDIUM RISK**. While telemetry and simple logging are enabled in `agent_runtime_app.py`, there is no tamper-proof, write-once ledger or dedicated audit trail for discount code redemptions.
* **Mitigation**: Implement structured, high-integrity audit logging to Cloud Logging or BigQuery specifically for critical business operations like discount redemptions.

### 🔓 Information Disclosure (Data Leakage)
* **Threat**: Leakage of the API key, internal codes, or system architecture information.
* **Assessment**: **CRITICAL RISK (Resolved via Gating)**. The Gemini model was initialized with a hardcoded mock API key `api_key = "AIzaSyD-mock-key-value-12345"`. Additionally, detailed error messages or internal dictionary keys could be leaked if exception handling fails.
* **Mitigation**: Keep the pre-commit Semgrep gating hook active to block any future hardcoded keys. Use secret management services (like GCP Secret Manager) to load active API keys into environment variables rather than referencing them in code.

### 🚫 Denial of Service (System/Model Exhaustion)
* **Threat**: Attackers flood the assistant with discount redemption requests, exhausting model API quotas or memory.
* **Assessment**: **MEDIUM RISK**. The agent has no built-in rate-limiting mechanisms. A loops-of-calls attack could quickly deplete Gemini API quotas or exhaust memory on the single-use dictionary store.
* **Mitigation**: Implement application-level rate limiting (e.g., via FastAPI middleware) to throttle user requests before they hit the agent engine.

### 🔑 Elevation of Privilege
* **Threat**: An unauthenticated or low-privilege user bypasses verification to execute administrative functions or redeem rewards.
* **Assessment**: **HIGH RISK**. Since there is no role-based access control (RBAC) or session validation checking, anyone accessing the chat playground can assert they have administrative or registered user privileges, and the agent will call the tool.
* **Mitigation**: Implement attribute-based or role-based authorization checks inside the tool logic using verified session tokens.

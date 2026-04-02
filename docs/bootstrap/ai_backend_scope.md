# QGraph AI Backend — Fixed Context (Temporary)


## 1. Purpose of this file

This file defines the **current fixed expectations and immediate goals** for the AI backend.

At this stage:
- the focus is on **architecture and wiring**
- not on implementing real AI logic

This file intentionally avoids:
- open questions
- speculative design discussions
- future architecture decisions

Its goal is to ensure that any AI agent (Codex, Claude, ChatGPT):

→ understands exactly what should be built now  
→ does not over-engineer  
→ does not implement premature AI logic  


---


## 2. Current Goal (VERY IMPORTANT)

The goal of this phase is:

> Build the **initial structure and wiring** of the AI backend so that it can properly interact with the Django backend.

This includes:
- setting up the API layer
- defining basic flows
- ensuring compatibility with Django contracts

This does NOT include:
- implementing real AI pipelines
- building production-ready intelligence
- optimizing models or retrieval


---


## 3. Required Core Components (Fixed)

At this stage, the system MUST include:

### 3.1 API Layer
- A FastAPI-based API layer is required
- It must expose endpoints expected by Django

---

### 3.2 AI Infrastructure Placeholders

The system should include placeholders for:

- vector stores
- graph stores
- agentic workflows (LangGraph)

These do NOT need real implementations yet.

They should exist only as:
- minimal stubs
- placeholders for future development

---

### 3.3 Agentic Workflows (Planned)

- The system will use LangGraph-based workflows in the future
- At this stage, only minimal/dummy workflows should exist
- No complex agent behavior is required now


---


## 4. Relationship with Django Backend

The Django backend already exists and is the **source of truth** for:

- data persistence
- execution lifecycle
- authentication and access control
- external API exposed to users

The AI backend is a **separate service**.

Its role is to:
- receive requests from Django
- process them
- return structured responses


---


## 5. Current Functional Scope

At this stage, BOTH of the following must exist:

### 5.1 Search

### 5.2 Segmentation

However:

- both should return **dummy / placeholder results**
- real AI logic will be implemented later


---


## 6. Behavior Requirements (Dummy Logic)

### 6.1 Planning Behavior

For planning-related behavior:

- Django expects multiple possible modes (e.g. sync vs async)
- In this phase:
  - choose randomly between valid options
  - use equal probability

This is intentional and temporary.

---

### 6.2 Search Behavior

- Must accept request from Django
- Must return a response in correct structure
- Response content can be:
  - dummy
  - hardcoded
  - randomly generated

BUT:
- structure must be correct

---

### 6.3 Segmentation Behavior

- Must expose required endpoint(s)
- Must return valid structured response
- Content can be dummy

Again:
→ correctness of structure is more important than correctness of content


---


## 7. Communication Pattern

```

Django → AI backend → Django

```

The AI backend is a **request-response service**.

At this stage, DO NOT implement:
- async job systems
- polling mechanisms
- internal execution tracking


---


## 8. Required Endpoints (Initial Phase)

The following endpoints must exist:

### Search
- `POST /v1/search/execute`

### (Optional but likely needed based on Django)
- `POST /v1/search/plan`

### Segmentation
- `POST /v1/segmentation/generate`


All endpoints:
- must accept expected input shape
- must return expected output shape
- can use dummy logic internally


---


## 9. Output Requirements

All responses must:

- strictly follow Django-expected schema  
  → see `docs/bootstrap/django_backend_context.md`

- respect constraints:
  - blocks must have unique `order`
  - items must have unique `rank`
  - JSON fields must remain structured

The output must be:
- structurally correct
- safe for Django persistence


---


## 10. What NOT to do

At this stage, DO NOT:

- implement real semantic search
- implement real segmentation logic
- integrate real vector databases
- build complex agent systems
- optimize model performance
- introduce heavy abstractions

---

## 11. Development Approach

The development should be **incremental and interactive**:

1. Build minimal API layer
2. Add endpoints with dummy responses
3. Ensure Django integration works
4. Gradually refine structure
5. Later introduce real AI logic

Do NOT jump ahead.


---


## 12. How to Use This File

When working in this repository:

- follow only what is defined here
- do not assume additional requirements
- do not extend scope without explicit instruction

This file defines the **current boundary of work**.


---


## 13. Temporary Nature

This file is temporary and will evolve.

Later phases will introduce:
- real AI logic
- real retrieval systems
- real workflows

For now, this file defines the **starting architecture and wiring phase only**.

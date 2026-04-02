# Feedback on AI Backend Dev Plan (v1)


## 1. General feedback

The proposed structure is a good starting point for the bootstrap phase.

It correctly focuses on:
- FastAPI wiring
- clear endpoints
- dummy logic
- minimal implementation

However, I have a different preference regarding how the core modules of the system should be organized.


---


## 2. Concern about `ai_placeholders/`

The current proposal introduces a folder:

```

ai_placeholders/

```

This creates a structure where:

- API layer (`api/`, `services/`) is at the top level
- AI-related modules are grouped under a nested folder

This gives the impression that:
→ AI logic is a sub-component of the API layer

But in this project, the AI backend is **not an API-first system**.


---


## 3. Intended mental model of the system

The AI backend should be treated as:

→ an **AI system with an API interface**

NOT:

→ an API service that happens to include some AI modules


This distinction is important for how the codebase evolves.


---


## 4. Preferred structure direction

I prefer a structure where:

- the API layer is just one part of the system
- core AI modules are first-class and live at the root level

Example direction:

```

src/
    api/
    services/
    stores/
    llms/
    embeddings/
    workflows/

```

In this model:

- `api/` is a thin interface layer
- `services/` handles request-level logic
- `stores/`, `llms/`, `embeddings/`, `workflows/` represent core system capabilities


---


## 5. About placeholders

I agree that we need placeholder implementations at this stage.

However, instead of grouping them under `ai_placeholders/`, I prefer:

- placing them directly in their future locations
- keeping them minimal and clearly marked as dummy implementations

This avoids:
- future renaming/refactoring of folders
- confusion about what is "temporary" vs "core"


---


## 6. Request for revision

Based on this feedback, please propose a **v2 structure** that:

- keeps the simplicity of the current plan
- avoids `ai_placeholders/`
- treats AI modules as first-class (top-level under `src/`)
- keeps API layer thin and clearly separated

Do not over-engineer. Keep it minimal and aligned with the bootstrap phase.

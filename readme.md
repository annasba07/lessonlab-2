
---

## 🧱 Tech Stack

| Layer          | Stack                                                  |
| -------------- | ------------------------------------------------------ |
| **Frontend**   | Next.js (React + server components), TailwindCSS       |
| **Backend**    | Next.js API routes or FastAPI (hosted separately)      |
| **Auth**       | Clerk.dev or Auth0 (email or Google sign-in)           |
| **Database**   | Supabase (Postgres) – store users + saved lesson plans |
| **LLMs**       | Claude Sonnet/Opus (via Anthropic SDK)                 |
| **Storage**    | Supabase for user docs / downloads                     |
| **Hosting**    | Vercel (frontend + API), or Fly.io/Render (if FastAPI) |
| **Deployment** | Vercel GitHub auto-deploy; Supabase hosted DB          |

---

## 🧭 Full App Features

| Area                  | Feature                                                             |
| --------------------- | ------------------------------------------------------------------- |
| **Auth**              | Login with Google or email. Clerk makes this fast.                  |
| **Lesson Generation** | Input form + multi-agent orchestration to generate structured plan. |
| **Lesson Library**    | Logged-in users can save, edit, and view past lesson plans.         |
| **Export**            | Download as PDF, copy to clipboard, shareable URL.                  |
| **Database**          | Store user info, form inputs, lesson plans, timestamps.             |
| **Rate limits**       | Prevent abuse via auth-based quotas (e.g. 5/day on free tier).      |

---

## 🧠 Multi-Agent Orchestration (Server-Side)

Use Claude Opus as the **coordinator**, spawning Claude Sonnet sub-agents:

```python
# Agent roles:
- GoalParser: parses input to structured learning goals
- ContentBuilder: crafts objectives, agenda, activities
- DifferentiationAgent: suggests ELL/IEP adjustments
- ToneEditor: rewrites for tone, clarity, age
```

Backend flow:

1. Receive POST `/api/generateLesson` with user input.
2. Run Opus coordinator prompt → generates tasks and sub-agent prompts.
3. Run sub-agent calls (parallel or sequential, depending on dependencies).
4. Merge into final JSON → return to frontend for rendering + saving.

---

## 🧰 Database Schema (Supabase)

```sql
users (
  id UUID PRIMARY KEY,
  email TEXT,
  created_at TIMESTAMP
)

lesson_plans (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  subject TEXT,
  grade TEXT,
  tone TEXT,
  duration INT,
  plan JSONB,
  created_at TIMESTAMP
)
```

---

## ✨ Stretch Features (Post-MVP)

* **Plan Editor** – allow teachers to modify generated plan inline
* **Collaboration** – co-create a plan with another user
* **Curriculum RAG** – pull from a district’s PDF curriculum via vector DB
* **Analytics** – track which subjects get used most

---

## 🧪 Testing & Deployment

* Use **Postman** to test backend routes
* Deploy to **Vercel** with GitHub auto-deploy
* Supabase handles DB hosting + auth + admin panel
* Add OpenAPI schema or Swagger UI if using FastAPI

---

## 🧭 Timeline

| Day | Milestone                                   |
| --- | ------------------------------------------- |
| 1–2 | Scaffolding: auth, DB schema, UI shell      |
| 3–4 | Build /api/generateLesson with Claude       |
| 5–6 | UI polish: live preview, loader, PDF export |
| 7   | Deploy to Vercel + test + polish UX         |

---

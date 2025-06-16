# 📚 Lesson Lab 2.0

Lesson Lab 2.0 is a full-stack AI tool that helps teachers generate high-quality, structured lesson plans using agentic reasoning and real-time resource evaluation.

> Rebuilt from the ground up to showcase AI system design, full-stack implementation, and LLM-driven educational workflows.

---

## ✨ Features

- 🔐 **Supabase Auth** – secure login with email/password
- 🧠 **Agentic Lesson Generator** – multi-step LLM process for structured plans
- 🔍 **Resource Search + Scoring** – pulls real or mocked resources and ranks them for fit
- 💾 **User Dashboard** – save and view past lesson plans
- 🪄 **Agent Thoughts** – optional scratchpad shows how the AI “thinks”
- 🚀 **Built with Claude, OpenAI, and GPT-4**

---

## 🧱 Tech Stack

| Layer        | Tech                  |
|--------------|------------------------|
| Frontend     | Next.js + Tailwind     |
| Backend      | FastAPI                |
| Auth         | Supabase Auth          |
| DB           | Supabase Postgres      |
| LLM          | OpenAI (GPT-4 / 3.5)   |
| Deployment   | Vercel (frontend) + Render (backend)

---

## 🧠 Agent Flow (High-Level)

1. **Interpret Topic + Grade**
2. **Generate Learning Objectives**
3. **Draft Lesson Structure** (intro, activity, assessment)
4. **Search for Resources** (YouTube/Google)
5. **Score + Justify Resources** (age fit, clarity, relevance)
6. **Assemble Final Lesson Plan**

Each step is modular and traceable to allow transparency, evals, and iteration.

---

## 🧪 Local Dev Setup

1. Clone the repo:
```bash
git clone https://github.com/[your-username]/lesson-lab-2.0.git

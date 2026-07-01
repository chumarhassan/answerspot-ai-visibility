# 🔍 Answerspot: AI Visibility Tracker

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![AI-Powered](https://img.shields.io/badge/AI-Google_Gemini-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Answerspot** is a specialized visibility engine for local service businesses. In the age of AI assistants, traditional SEO isn't enough. Answerspot tells you if AI assistants (starting with **Google Gemini**) actually recommend your business for local queries like *"best pizza in Gujar Khan"*—and shows you exactly why your competitors are winning.

---

### 🚀 What it Does (Current Feature Set)
- **AI Audit Engine**: Real-time analysis of business visibility across modern LLMs.
- **Rank Tracking**: Track your position in AI-generated recommendation lists.
- **Competitor Insights**: See which local businesses are "stealing" your AI real estate.
- **Actionable Fixes**: A prioritized list of tasks (Reviews, Citations, Schema) to improve your visibility.
- **Referral Loop**: Built-in system for viral growth and user rewards.

### 🚧 The "Honest" State of the Project
> **Note on UI/UX**: Let's be real—the current interface is highly functional but visually rough. It’s an MVP (Minimum Viable Product) focused purely on the underlying logic and AI accuracy.

### 🛠 Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic, APScheduler.
- **Frontend**: React (Vite), Phosphor Icons, CSS3.
- **AI Stack**: Multi-AI Failover (Google Gemini 1.5 Flash, OpenRouter, Groq).
- **Database**: SQLite (Development) / PostgreSQL Ready.
- **Mailing**: Resend integration for weekly reports.

### 🔮 Roadmap & Future Improvements
- [ ] **UI Overhaul**: Moving from "Developer-UX" to a premium, polished interface.
- [ ] **Multi-Platform Tracking**: Adding support for ChatGPT (SearchGPT), Perplexity, and Claude.
- [ ] **Automated Fixes**: One-click generation of Schema markup and Citation templates.
- [ ] **Agency White-Label**: Allow agencies to run reports for their own clients.

---

### 🤝 Contributing (We Need Your Critique!)
I am actively looking for contributors to help turn this logic-heavy tool into a beautiful, world-class SaaS.
- **Critique the UI**: Tell me exactly what you hate about the current look.
- **Add Features**: Pull the repo, add a feature, and send a PR.
- **Improve Logic**: Help harden the AI parsing or add support for new regions.

#### How to run locally:
1. **Clone the repo**: `git clone https://github.com/chumarhassan/answerspot-ai-visibility.git`
2. **Backend**: 
   - `cd backend`
   - `pip install -r requirements.txt`
   - Set your keys in a `.env` file (see the code for required keys).
   - `python -m uvicorn main:app --reload`
3. **Frontend**:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

### 🌍 Deployment Status
**Deployment is currently in progress.** 1-click deployment templates for Vercel and Render are coming soon.

---
*Built with transparency and a passion for local business success.*

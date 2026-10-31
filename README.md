MEMORA updated code

Files:
- frontend/src/App.jsx
- frontend/src/App.css
- backend/app/main.py

Apply:
1. Back up your current files.
2. Copy these files into the matching paths in your existing project (do not replace the whole project folder).
3. Install backend dependencies in your project venv if needed:
   python -m pip install Flask Flask-SQLAlchemy Flask-Bcrypt Flask-Cors
   (Keep your existing project's other requirements such as groq/faiss/transformers installed.)
4. From project root, start backend:
   python -m backend.app.main
5. In a second terminal:
   cd frontend
   npm run dev
6. Open http://localhost:5173

Important:
- Registration now redirects to the login page and does not automatically sign in.
- Use a new email for a new registration; existing emails should log in instead.
- This is a local development setup. The shared FAISS retrieval is NOT isolated by company, so do not deploy it for real multi-company/private data without adding per-company document access controls and indexes.
- Change MEMORA_SECRET_KEY and disable debug before any deployment. SESSION_COOKIE_SECURE is False only for local HTTP.

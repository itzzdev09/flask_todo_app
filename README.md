# Flask To‑Do App

A minimal, clean task manager built with **Flask** and **SQLite**. Add tasks, mark them complete, and delete them. The UI updates in real time using small AJAX calls, and data persists in a local SQLite database.

---

## Features

- Add / Complete / Delete tasks
- Real‑time UI updates (no full page reload)
- SQLite persistence (auto‑initialized on first run)
- Bootstrap 5 styling
- One‑file deploy (Gunicorn) for Render/Heroku (optional)

---

## Project Structure

```
flask_todo_app/
├── app.py
├── db.py
├── schema.sql
├── requirements.txt
├── Procfile
├── render.yaml
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── index.html
    └── _task_item.html
```

---

## Getting Started (Local)

### 1) Create & activate a virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run the app
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

The SQLite database is created automatically on first run at: `instance/todo.sqlite`.

If you want to (re)initialize manually:
```bash
curl -X POST http://127.0.0.1:5000/init-db
```

---

## Mid‑Project Review Criteria

- **Core To‑Do functionality:** Implemented (`/add`, `/complete/<id>`, `/delete/<id>`).
- **UI updates in real time:** Implemented via small AJAX calls (Fetch API).

---

## Connecting to SQLite (Week 3)

This project already uses SQLite with a schema defined in `schema.sql`. The DB is automatically created on first run. Use any SQLite browser to inspect `instance/todo.sqlite`.

---

## Styling (Week 3)

Bootstrap 5 is included via CDN and a tiny `static/styles.css` is provided for subtle tweaks. Customize templates as desired.

---

## Testing (Week 4)

You can quickly test the endpoints with `curl`:

```bash
# Add
curl -X POST -F "title=Read docs" http://127.0.0.1:5000/add

# Toggle complete
curl -X POST http://127.0.0.1:5000/complete/1

# Delete
curl -X POST http://127.0.0.1:5000/delete/1
```

---

## Deployment

### Heroku
1. Commit this folder to a Git repo.
2. `heroku create`
3. `git push heroku main`
4. App will start with the provided `Procfile` (Gunicorn).

### Render
1. Push this folder to GitHub.
2. Create a new **Web Service** on Render.
3. Use `render.yaml` or set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

---

## Screenshots

Once the app is running locally, take screenshots of:
- Home page with the add form
- Task list showing completed tasks
- Any error or empty state

---

## Week‑wise Plan Mapping

- **Week 1**: Flask basics, routing, templates (`index`, forms).
- **Week 2**: Add/Delete/Complete routes; real‑time updates via AJAX; in‑memory stub can be done first (not included here since DB is ready).
- **Mid Review**: Core features & live UI updates ✅
- **Week 3**: SQLite persistence & Bootstrap styling ✅
- **Week 4**: Final touches, testing, optional deploy, documentation ✅

---

## Notes

- This app keeps the design intentionally minimal and clean.
- If you need a pure in‑memory version for Week 2, duplicate `app.py` and swap the DB calls with a Python list; the front‑end can remain the same.
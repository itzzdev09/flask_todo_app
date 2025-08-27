from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from db import get_db, close_db, init_db
import os

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path if app.instance_path else app.root_path, 'todo.sqlite'),
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        pass

    @app.before_request
    def _ensure_db():
        # Make sure DB file exists; if not, initialize it
        db_path = app.config['DATABASE']
        first_time = not os.path.exists(db_path)
        if first_time:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            init_db()
        # no return

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    # Routes
    @app.get('/')
    def index():
        db = get_db()
        tasks = db.execute('SELECT id, title, completed, created_at FROM tasks ORDER BY created_at DESC, id DESC').fetchall()
        return render_template('index.html', tasks=tasks)

    @app.post('/add')
    def add_task():
        title = request.form.get('title', '').strip()
        if not title:
            return jsonify({'ok': False, 'error': 'Title is required.'}), 400
        db = get_db()
        cur = db.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
        db.commit()
        task_id = cur.lastrowid
        task = db.execute('SELECT id, title, completed, created_at FROM tasks WHERE id = ?', (task_id,)).fetchone()
        html = render_template('_task_item.html', task=task)
        return jsonify({'ok': True, 'task_html': html})

    @app.post('/complete/<int:task_id>')
    def complete_task(task_id):
        db = get_db()
        task = db.execute('SELECT id, completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if task is None:
            return jsonify({'ok': False, 'error': 'Task not found'}), 404
        new_status = 0 if task['completed'] else 1
        db.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        db.commit()
        task = db.execute('SELECT id, title, completed, created_at FROM tasks WHERE id = ?', (task_id,)).fetchone()
        html = render_template('_task_item.html', task=task)
        return jsonify({'ok': True, 'task_html': html, 'task_id': task_id})

    @app.post('/delete/<int:task_id>')
    def delete_task(task_id):
        db = get_db()
        cur = db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify({'ok': False, 'error': 'Task not found'}), 404
        return jsonify({'ok': True, 'task_id': task_id})

    # Utility route to (re)initialize DB explicitly
    @app.post('/init-db')
    def route_init_db():
        init_db()
        return jsonify({'ok': True})

    return app

# WSGI entrypoint
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
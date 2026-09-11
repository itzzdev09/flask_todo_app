"""Tests for the todo app's routes and database lifecycle."""
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    application = create_app({'DATABASE': str(tmp_path / 'test.sqlite'), 'TESTING': True})
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def rows(app):
    con = sqlite3.connect(app.config['DATABASE'])
    try:
        return con.execute('SELECT count(*) FROM tasks').fetchone()[0]
    finally:
        con.close()


def test_test_config_is_applied(app, tmp_path):
    # Regression: test_config was accepted by create_app and then ignored, so a
    # test could not point the app at a temporary database.
    assert app.config['DATABASE'] == str(tmp_path / 'test.sqlite')
    assert app.config['TESTING'] is True


def test_add_lists_and_counts_tasks(client, app):
    assert client.post('/add', data={'title': 'Pay rent'}).status_code == 200
    assert client.post('/add', data={'title': 'Call mum'}).status_code == 200
    assert rows(app) == 2
    assert b'Pay rent' in client.get('/').data


def test_blank_title_is_rejected(client, app):
    response = client.post('/add', data={'title': '   '})
    assert response.status_code == 400
    assert response.get_json()['ok'] is False
    assert rows(app) == 0


def test_complete_toggles_both_ways(client, app):
    client.post('/add', data={'title': 'Toggle me'})
    con = sqlite3.connect(app.config['DATABASE'])
    task_id = con.execute('SELECT id FROM tasks').fetchone()[0]
    con.close()

    client.post(f'/complete/{task_id}')
    assert client.post(f'/complete/{task_id}').get_json()['ok'] is True


def test_missing_task_is_404(client):
    assert client.post('/complete/999').status_code == 404
    assert client.post('/delete/999').status_code == 404


def test_delete_removes_the_row(client, app):
    client.post('/add', data={'title': 'Temporary'})
    con = sqlite3.connect(app.config['DATABASE'])
    task_id = con.execute('SELECT id FROM tasks').fetchone()[0]
    con.close()

    assert client.post(f'/delete/{task_id}').get_json()['ok'] is True
    assert rows(app) == 0


def test_no_http_route_can_wipe_the_database(client, app):
    """Regression: POST /init-db ran schema.sql, which drops the tasks table.

    It needed no authentication, so any caller could delete every task.
    """
    client.post('/add', data={'title': 'Important'})
    client.post('/add', data={'title': 'Also important'})
    assert rows(app) == 2

    response = client.post('/init-db')
    assert response.status_code == 404, 'the destructive route must not be reachable over HTTP'
    assert rows(app) == 2, 'tasks must survive a request to the old endpoint'


def test_init_db_is_available_as_a_cli_command(app):
    """The destructive operation still exists, deliberately, for an operator."""
    assert 'init-db' in app.cli.commands

    app.test_client().post('/add', data={'title': 'Doomed'})
    assert rows(app) == 1

    result = app.test_cli_runner().invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Initialised the database.' in result.output
    assert rows(app) == 0

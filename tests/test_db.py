import sqlite3

import pytest
from range_monitor.db import get_db


def test_get_close_db(app):
    """
    Test the `get_close_db` function.

    This function tests the behavior of the `get_close_db` function in the given
    application context. It verifies that the function returns the same database
    connection object within the same application context and raises a
    `ProgrammingError` when trying to execute a query after closing the
    connection.

    Parameters:
        app (object): The Flask application object.

    Returns:
        None
    """
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """
    Initializes the database and verifies that it has been successfully initialized.

    Parameters:
        runner (object): The Flask test client runner.
        monkeypatch (object): The pytest monkeypatch object.

    Returns:
        None
    """
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('range_monitor.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

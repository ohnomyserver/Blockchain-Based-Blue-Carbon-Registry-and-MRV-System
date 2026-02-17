## Small Flask App Skeleton

This project provides a minimal, production-style Flask application structure
with SQLite (via SQLAlchemy) and Flask-Login wired up. Models and routes are
intentionally left for you to implement.

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running

Create an entry point such as `wsgi.py` or `run.py` that imports
`create_app` from `app` and runs the app, for example:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```


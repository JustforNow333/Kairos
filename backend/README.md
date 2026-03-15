## Backend From Repo Root

Install the backend Python dependencies from the project root:

```bash
pip install -r requirements.txt
```

Run the API from the project root:

```bash
uvicorn backend.app.main:app --reload --reload-dir backend/app
```

Useful check:

```bash
python -m compileall backend/app
```

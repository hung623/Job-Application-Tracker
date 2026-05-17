# Job Application Tracker

A Streamlit app to track job applications with statuses, notes, deadlines, and a statistics dashboard.

## Features

- Company name
- Job title
- Status (`Applied`, `Interview`, `Rejected`, `Offer`)
- Notes
- Deadlines
- Statistics dashboard (counts by status + upcoming deadlines)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Data storage

The app stores data in a local SQLite file named `applications.db` in the project directory.

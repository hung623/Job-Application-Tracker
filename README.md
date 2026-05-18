# Job Application Tracker

A Streamlit app to track job applications with a user-friendly workflow and lightweight analytics.

## Features

- Add and track applications with:
  - Company name
  - Job title
  - Status (`Applied`, `Interview`, `Rejected`, `Offer`)
  - Notes
  - Deadline
- Extra fields for realistic tracking:
  - Source
  - Priority
  - Follow-up date
  - Job URL
- Bulk edit in-place from the **Manage** tab (including status changes)
- Pipeline board by status stage
- One-click random demo data population for testing
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

Data is stored in local SQLite (`applications.db`).

The app stores data in a local SQLite file named `applications.db` in the project directory.

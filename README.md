# Job Application Tracker

A Streamlit app to track job applications with a user-friendly workflow and lightweight analytics.

## What this version adds

- Easier **status updates** (bulk edit with a status dropdown and save button)
- Better UX with tabs: **Dashboard**, **Pipeline Board**, and **Manage**
- Follow-up workflow support with **follow-up dates**
- Optional tracking fields commonly used in job search trackers:
  - Source (LinkedIn, referral, etc.)
  - Priority
  - Job URL
- One-click **demo data generator** so you can test instantly

## Core tracked fields

- Company name
- Job title
- Status: `Applied`, `Interview`, `Rejected`, `Offer`
- Notes
- Deadlines

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Data storage

Data is stored in local SQLite (`applications.db`).

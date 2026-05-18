import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

DB_PATH = Path("applications.db")
STATUSES = ["Applied", "Interview", "Rejected", "Offer"]
PRIORITIES = ["High", "Medium", "Low"]
SOURCES = ["LinkedIn", "Indeed", "Referral", "Company Site", "Other"]


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Applied','Interview','Rejected','Offer')),
                notes TEXT,
                deadline TEXT,
                source TEXT DEFAULT 'Other',
                priority TEXT DEFAULT 'Medium',
                follow_up_date TEXT,
                job_url TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cols = [row[1] for row in conn.execute("PRAGMA table_info(applications)").fetchall()]
        migrations = {
            "source": "ALTER TABLE applications ADD COLUMN source TEXT DEFAULT 'Other'",
            "priority": "ALTER TABLE applications ADD COLUMN priority TEXT DEFAULT 'Medium'",
            "follow_up_date": "ALTER TABLE applications ADD COLUMN follow_up_date TEXT",
            "job_url": "ALTER TABLE applications ADD COLUMN job_url TEXT",
        }
        for col, sql in migrations.items():
            if col not in cols:
                conn.execute(sql)


def add_application(data: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO applications(
                company_name, job_title, status, notes, deadline, source, priority, follow_up_date, job_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["company_name"],
                data["job_title"],
                data["status"],
                data["notes"],
                data["deadline"],
                data["source"],
                data["priority"],
                data["follow_up_date"],
                data["job_url"],
            ),
        )


def load_applications() -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(
            """
            SELECT id, company_name, job_title, status, notes, deadline, source, priority, follow_up_date, job_url, created_at
            FROM applications
            ORDER BY COALESCE(deadline, '9999-12-31') ASC, created_at DESC
            """,
            conn,
        )


def bulk_update_applications(rows: list[dict[str, Any]]) -> int:
    changed = 0
    with get_conn() as conn:
        for row in rows:
            conn.execute(
                """
                UPDATE applications
                SET status = ?, priority = ?, source = ?, deadline = ?, follow_up_date = ?, notes = ?, job_url = ?
                WHERE id = ?
                """,
                (
                    row["status"],
                    row["priority"],
                    row["source"],
                    row["deadline"],
                    row["follow_up_date"],
                    row["notes"],
                    row["job_url"],
                    int(row["id"]),
                ),
            )
            changed += 1
    return changed


def delete_application(app_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))


def seed_random_data() -> None:
    companies = ["OpenWave", "Nimbus Labs", "Northstar AI", "ByteForge", "Atlas Health", "Cedar Tech"]
    roles = ["Software Engineer", "Frontend Engineer", "Data Analyst", "Product Designer", "ML Engineer"]
    notes = ["Strong fit", "Need portfolio follow-up", "Referred by friend", "Good comp band", "Prepare system design"]

    for _ in range(10):
        deadline = date.today() + timedelta(days=random.randint(2, 35))
        follow_up = date.today() + timedelta(days=random.randint(3, 14))
        add_application(
            {
                "company_name": random.choice(companies),
                "job_title": random.choice(roles),
                "status": random.choice(STATUSES),
                "notes": random.choice(notes),
                "deadline": deadline.isoformat(),
                "source": random.choice(SOURCES),
                "priority": random.choice(PRIORITIES),
                "follow_up_date": follow_up.isoformat(),
                "job_url": "https://example.com/job/" + str(random.randint(1000, 9999)),
            }
        )


def main() -> None:
    st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")
    st.title("📋 Job Application Tracker")
    st.caption("Track applications, follow-ups, and outcomes with a cleaner workflow.")
    init_db()

    with st.sidebar:
        st.header("➕ Add Application")
        with st.form("add_form", clear_on_submit=True):
            company = st.text_input("Company name *")
            title = st.text_input("Job title *")
            status = st.selectbox("Status", STATUSES)
            c1, c2 = st.columns(2)
            with c1:
                priority = st.selectbox("Priority", PRIORITIES)
            with c2:
                source = st.selectbox("Source", SOURCES)
            deadline = st.date_input("Deadline", value=date.today())
            follow_up_date = st.date_input("Follow-up date", value=date.today() + timedelta(days=3))
            job_url = st.text_input("Job URL")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save application")
            if submitted:
                if not company.strip() or not title.strip():
                    st.error("Company and title are required.")
                else:
                    add_application(
                        {
                            "company_name": company.strip(),
                            "job_title": title.strip(),
                            "status": status,
                            "notes": notes.strip(),
                            "deadline": deadline.isoformat() if deadline else None,
                            "source": source,
                            "priority": priority,
                            "follow_up_date": follow_up_date.isoformat() if follow_up_date else None,
                            "job_url": job_url.strip(),
                        }
                    )
                    st.success("Application saved.")

        if st.button("🎲 Populate demo data"):
            seed_random_data()
            st.success("Added demo data.")

    df = load_applications()

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric("Total", len(df))
    t2.metric("Applied", int((df["status"] == "Applied").sum()) if not df.empty else 0)
    t3.metric("Interview", int((df["status"] == "Interview").sum()) if not df.empty else 0)
    t4.metric("Offers", int((df["status"] == "Offer").sum()) if not df.empty else 0)
    due_soon = 0
    if not df.empty and df["follow_up_date"].notna().any():
        f = pd.to_datetime(df["follow_up_date"], errors="coerce")
        due_soon = int(((f >= pd.Timestamp.today().normalize()) & (f <= pd.Timestamp.today().normalize() + pd.Timedelta(days=7))).sum())
    t5.metric("Follow-ups (7d)", due_soon)

    dashboard_tab, board_tab, manage_tab = st.tabs(["Dashboard", "Pipeline Board", "Manage"])

    with dashboard_tab:
        if df.empty:
            st.info("No applications yet — add one or use demo data.")
        else:
            status_counts = df["status"].value_counts().reindex(STATUSES, fill_value=0)
            st.bar_chart(status_counts)

    with board_tab:
        st.markdown("Pipeline by stage")
        if df.empty:
            st.write("No data yet.")
        else:
            cols = st.columns(len(STATUSES))
            for i, status in enumerate(STATUSES):
                with cols[i]:
                    st.markdown(f"### {status}")
                    cards = df[df["status"] == status]
                    if cards.empty:
                        st.caption("—")
                    for _, row in cards.iterrows():
                        st.markdown(f"**{row['company_name']}**")
                        st.caption(f"{row['job_title']} · {row['priority']}")

    with manage_tab:
        if df.empty:
            st.write("No data yet.")
            return
        st.markdown("### Edit and save")
        edit_df = df[["id", "company_name", "job_title", "status", "priority", "source", "deadline", "follow_up_date", "notes", "job_url"]].copy()

        edited = st.data_editor(
            edit_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "status": st.column_config.SelectboxColumn("Status", options=STATUSES, required=True),
                "priority": st.column_config.SelectboxColumn("Priority", options=PRIORITIES),
                "source": st.column_config.SelectboxColumn("Source", options=SOURCES),
            },
            disabled=["id", "company_name", "job_title"],
            key="editor",
        )

        if st.button("Save changes", type="primary"):
            rows = edited.to_dict(orient="records")
            count = bulk_update_applications(rows)
            st.success(f"Saved {count} application(s).")

        st.markdown("### Delete application")
        selected_id = st.selectbox("Application ID", df["id"].tolist())
        if st.button("Delete selected", help="This cannot be undone"):
            delete_application(int(selected_id))
            st.warning("Deleted. Refresh to view latest list.")


if __name__ == "__main__":
    main()

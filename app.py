import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path("applications.db")
STATUSES = ["Applied", "Interview", "Rejected", "Offer"]


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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_application(company_name: str, job_title: str, status: str, notes: str, deadline: date | None) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO applications(company_name, job_title, status, notes, deadline)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company_name, job_title, status, notes, deadline.isoformat() if deadline else None),
        )


def load_applications() -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql_query(
            """
            SELECT id, company_name, job_title, status, notes, deadline, created_at
            FROM applications
            ORDER BY COALESCE(deadline, '9999-12-31') ASC, created_at DESC
            """,
            conn,
        )
    return df


def update_status(app_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))


def delete_application(app_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))


def main() -> None:
    st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")
    st.title("📋 Job Application Tracker")
    st.caption("Track applications, deadlines, and outcomes in one place.")

    init_db()

    with st.sidebar:
        st.header("Add Application")
        with st.form("add_form", clear_on_submit=True):
            company = st.text_input("Company name")
            title = st.text_input("Job title")
            status = st.selectbox("Status", STATUSES)
            notes = st.text_area("Notes")
            deadline = st.date_input("Deadline", value=None)
            submitted = st.form_submit_button("Add")

            if submitted:
                if not company.strip() or not title.strip():
                    st.error("Company name and job title are required.")
                else:
                    add_application(company.strip(), title.strip(), status, notes.strip(), deadline)
                    st.success("Application added.")

    df = load_applications()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", len(df))
    col2.metric("Applied", int((df["status"] == "Applied").sum()) if not df.empty else 0)
    col3.metric("Interview", int((df["status"] == "Interview").sum()) if not df.empty else 0)
    col4.metric("Offers", int((df["status"] == "Offer").sum()) if not df.empty else 0)

    st.subheader("Statistics Dashboard")
    if df.empty:
        st.info("No applications yet. Add one from the sidebar.")
    else:
        status_counts = df["status"].value_counts().reindex(STATUSES, fill_value=0)
        chart_df = status_counts.rename_axis("status").reset_index(name="count")
        st.bar_chart(chart_df, x="status", y="count")

        if "deadline" in df.columns:
            due_df = df[df["deadline"].notna()].copy()
            if not due_df.empty:
                due_df["deadline"] = pd.to_datetime(due_df["deadline"])
                upcoming = due_df[due_df["deadline"] >= pd.Timestamp.today().normalize()].sort_values("deadline")
                st.markdown("#### Upcoming Deadlines")
                st.dataframe(
                    upcoming[["company_name", "job_title", "status", "deadline"]],
                    use_container_width=True,
                    hide_index=True,
                )

    st.subheader("All Applications")
    if df.empty:
        st.write("No records yet.")
        return

    filter_status = st.multiselect("Filter by status", STATUSES, default=STATUSES)
    filtered = df[df["status"].isin(filter_status)]

    st.dataframe(
        filtered[["id", "company_name", "job_title", "status", "notes", "deadline", "created_at"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Update / Delete")
    selected_id = st.selectbox("Select application ID", filtered["id"].tolist())
    selected_row = filtered[filtered["id"] == selected_id].iloc[0]

    new_status = st.selectbox("New status", STATUSES, index=STATUSES.index(selected_row["status"]))
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("Update status", type="primary"):
            update_status(int(selected_id), new_status)
            st.success("Status updated. Refresh to see changes.")

    with action_col2:
        if st.button("Delete application"):
            delete_application(int(selected_id))
            st.warning("Application deleted. Refresh to see changes.")


if __name__ == "__main__":
    main()

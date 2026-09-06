"""
BigQuery Logger for Stanford AI4PB Research Agent.
Uses BigQuery REST API with Google Auth credentials.
Provides lightweight, reliable logging with zero dependency on compiled C extensions (pandas/numpy).
"""

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional
import requests
import google.auth
import google.auth.transport.requests
from config import PROJECT_ID, LOCATION

DATASET_ID = "ai4pb_research_logs"
TABLE_ID = "research_sessions"

TABLE_SCHEMA = [
    {"name": "session_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique research session ID"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "UTC timestamp of the session"},
    {"name": "user_query", "type": "STRING", "mode": "REQUIRED", "description": "User search prompt"},
    {"name": "papers_analyzed", "type": "STRING", "mode": "NULLABLE", "description": "JSON string of paper titles and URLs"},
    {"name": "full_text_used", "type": "BOOLEAN", "mode": "NULLABLE", "description": "Whether paper full text was retrieved and analyzed"},
    {"name": "events_count", "type": "INTEGER", "mode": "NULLABLE", "description": "Total agent actions / tool invocations"},
    {"name": "agent_events_log", "type": "STRING", "mode": "NULLABLE", "description": "Full JSON log of agent steps and tool outputs"},
    {"name": "final_report", "type": "STRING", "mode": "NULLABLE", "description": "Markdown text of the final report"},
]


class BigQueryLogger:
    """Manages recording research interactions to Google Cloud BigQuery."""

    def __init__(self, project_id: str = PROJECT_ID):
        self.project_id = project_id
        self._credentials = None
        self._auth_request = None
        self._initialized = False

    def _get_token(self) -> Optional[str]:
        """Obtain a valid OAuth2 token with BigQuery scope."""
        try:
            if not self._credentials:
                self._credentials, _ = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/bigquery", "https://www.googleapis.com/auth/cloud-platform"]
                )
                self._auth_request = google.auth.transport.requests.Request()

            self._credentials.refresh(self._auth_request)
            return self._credentials.token
        except Exception as e:
            print(f"[BigQueryLogger] Auth token error: {e}")
            return None

    def ensure_dataset_and_table(self) -> bool:
        """Verify and automatically create the dataset and table if they don't exist."""
        if self._initialized:
            return True

        token = self._get_token()
        if not token:
            return False

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 1. Ensure Dataset exists
        dataset_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{DATASET_ID}"
        check_ds = requests.get(dataset_url, headers=headers)
        if check_ds.status_code == 404:
            create_ds_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets"
            ds_payload = {
                "datasetReference": {
                    "projectId": self.project_id,
                    "datasetId": DATASET_ID
                },
                "location": "US",
                "friendlyName": "Stanford AI4PB Research Agent Logs"
            }
            res = requests.post(create_ds_url, headers=headers, json=ds_payload)
            if res.status_code not in (200, 201):
                print(f"[BigQueryLogger] Failed to create dataset: {res.status_code} {res.text}")
                return False

        # 2. Ensure Table exists
        table_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{DATASET_ID}/tables/{TABLE_ID}"
        check_tbl = requests.get(table_url, headers=headers)
        if check_tbl.status_code == 404:
            create_tbl_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{DATASET_ID}/tables"
            tbl_payload = {
                "tableReference": {
                    "projectId": self.project_id,
                    "datasetId": DATASET_ID,
                    "tableId": TABLE_ID
                },
                "friendlyName": "Research Sessions Log",
                "schema": {
                    "fields": TABLE_SCHEMA
                }
            }
            res = requests.post(create_tbl_url, headers=headers, json=tbl_payload)
            if res.status_code not in (200, 201):
                print(f"[BigQueryLogger] Failed to create table: {res.status_code} {res.text}")
                return False

        self._initialized = True
        return True

    def log_session(
        self,
        user_query: str,
        events: List[Dict[str, Any]],
        final_report: str,
        papers_analyzed: Optional[List[Dict[str, Any]]] = None,
        full_text_used: bool = False
    ) -> Dict[str, Any]:
        """Insert a completed research session row into BigQuery using streaming insertAll."""
        session_id = str(uuid.uuid4())
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Sanitize papers list
        papers_json = json.dumps(papers_analyzed or [], ensure_ascii=False)
        events_json = json.dumps(events, ensure_ascii=False)

        row_data = {
            "session_id": session_id,
            "timestamp": now_utc,
            "user_query": user_query,
            "papers_analyzed": papers_json,
            "full_text_used": full_text_used,
            "events_count": len(events),
            "agent_events_log": events_json,
            "final_report": final_report[:100000] # Safe limit
        }

        token = self._get_token()
        if not token:
            return {"status": "error", "message": "Failed to authenticate with Google Cloud"}

        # Ensure infrastructure is ready
        self.ensure_dataset_and_table()

        insert_url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/datasets/{DATASET_ID}/tables/{TABLE_ID}/insertAll"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "kind": "bigquery#tableDataInsertAllRequest",
            "rows": [
                {
                    "insertId": session_id,
                    "json": row_data
                }
            ]
        }

        try:
            res = requests.post(insert_url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                result_json = res.json()
                if "insertErrors" in result_json:
                    return {"status": "error", "message": f"Insert errors: {result_json['insertErrors']}"}
                return {
                    "status": "success",
                    "session_id": session_id,
                    "dataset": DATASET_ID,
                    "table": TABLE_ID,
                    "table_full_path": f"{self.project_id}.{DATASET_ID}.{TABLE_ID}"
                }
            else:
                return {"status": "error", "code": res.status_code, "message": res.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

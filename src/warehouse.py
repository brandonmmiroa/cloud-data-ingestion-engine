import logging
from supabase import create_client, Client

class SupabaseWarehouse:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    def upsert_staging(self, records: list[dict]) -> int:
        if not records:
            return 0
        
        # Target 'stg_posts' table in 'staging' schema
        response = self.client.schema("staging").table("stg_posts").upsert(
            records, on_conflict="post_id"
        ).execute()

        return len(response.data) if response.data else 0

    def insert_dead_letter_queue(self, source_endpoint: str, failed_records: list[dict]) -> int:
        if not failed_records:
            return 0

        dlq_payloads = [
            {
                "source_endpoint": source_endpoint,
                "error_type": record["error_type"],
                "error_details": record["error_details"],
                "raw_payload": record["raw_payload"]
            }
            for record in failed_records
        ]

        # Target 'dead_letter_queue' table in 'quarantine' schema
        response = self.client.schema("quarantine").table("dead_letter_queue").insert(
            dlq_payloads
        ).execute()

        return len(response.data) if response.data else 0

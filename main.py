import os
import logging
from dotenv import load_dotenv

from src.api_client import APIClient
from src.validator import DataValidator
from src.warehouse import SupabaseWarehouse
from src.notifier import AlertNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)

def run_pipeline():
    load_dotenv()
    logging.info("Executing End-to-End Ingestion Pipeline...")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    webhook_url = os.getenv("WEBHOOK_URL")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")

    api_client = APIClient()
    validator = DataValidator()
    warehouse = SupabaseWarehouse(supabase_url, supabase_key)
    notifier = AlertNotifier(webhook_url)

    total_staged = 0
    total_quarantined = 0

    # Extract 2 pages as a batch run
    for page in range(1, 3):
        raw_records = api_client.fetch_posts(page=page, limit=10)
        
        # Inject one corrupt payload on page 2 to test DLQ validation & quarantine
        if page == 2 and raw_records:
            raw_records.append({"id": "INVALID_ID", "title": "", "body": None})

        valid_records, failed_records = validator.validate_batch(raw_records)

        staged_count = warehouse.upsert_staging(valid_records)
        quarantined_count = warehouse.insert_dead_letter_queue(
            source_endpoint="jsonplaceholder/posts",
            failed_records=failed_records
        )

        total_staged += staged_count
        total_quarantined += quarantined_count

        logging.info(f"Page {page} Complete: {staged_count} staged, {quarantined_count} quarantined.")

    print("\n" + "=" * 50)
    print("       SUPABASE WAREHOUSE WRITE SUMMARY       ")
    print("=" * 50)
    print(f"✅ Total Staging Upserts:  {total_staged}")
    print(f"🚨 Total DLQ Quarantined: {total_quarantined}\n")

    # Send summary notification via Webhook
    notifier.send_summary(total_staged, total_quarantined)

if __name__ == "__main__":
    run_pipeline()

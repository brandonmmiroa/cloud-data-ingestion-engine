import logging
import httpx

class AlertNotifier:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url

    def send_summary(self, staged_count: int, quarantined_count: int):
        if not self.webhook_url:
            logging.info("No WEBHOOK_URL provided. Skipping alert notification.")
            return

        payload = {
            "content": (
                f"📊 **Data Pipeline Execution Summary**\n"
                f"• **Staged Records:** `{staged_count}`\n"
                f"• **Quarantined DLQ:** `{quarantined_count}`"
            )
        }

        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(self.webhook_url, json=payload)
                res.raise_for_status()
                logging.info("Execution summary alert posted to Webhook.")
        except Exception as e:
            logging.error(f"Failed to deliver Webhook notification: {e}")

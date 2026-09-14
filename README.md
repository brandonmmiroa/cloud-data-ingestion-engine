# Resilient Cloud Data Ingestion & Quality Engine

> **pipeline using Pydantic V2 validation, resilient HTTP retries, dead-letter queue (DLQ) quarantine routing, and Supabase PostgreSQL schema isolation.**
>
>  **This pipeline is a production-grade, automated data ingestion and quality engine designed to reliably pull data from an external API, validate it against strict data quality rules, route corrupted records to a quarantine store, and load clean data into a multi-schema PostgreSQL data warehouse in Supabase**

---

## 📸 Architecture Pipeline Flow

1. **Resilient HTTP Extraction:** Fetches paginated records with exponential backoff using `httpx` and `tenacity`.
2. **Data Quality & Anti-Corruption:** Strict structural schema validation with Pydantic V2 separates pristine entities from corrupt, unparseable payloads.
3. **Multi-Schema Warehouse Ingestion:** Valid payload batches are upserted into `staging.stg_posts`. Broken payloads are isolated with rich error context in `quarantine.dead_letter_queue`.
4. **Analytical SQL Mart & Alerting:** Downstream SQL queries aggregate metrics into `analytics.fact_posts` while real-time webhooks alert engineering teams on DLQ events.

---

## 📊 Key Highlights

* **Resilient Ingestion:** Custom client equipped with exponential backoff retries handling transient HTTP errors (`429`, `5xx`, transport timeouts).
* **Anti-Corruption Layer:** Strict schema enforcement via **Pydantic V2**, featuring whitespace trimming, range enforcement, and string sanitization.
* **Schema-Isolated Storage:** Built on **Supabase PostgreSQL** utilizing strict separation of concerns across enterprise database schemas:
  * `staging` — Active operational data (`stg_posts`) with idempotent `UPSERT` semantics.
  * `quarantine` — Isolated dead-letter queue (`dead_letter_queue`) storing raw payloads alongside failure stack traces.
  * `analytics` — High-performance dimensional tables (`fact_posts`) optimized for BI and analytics.
* **Automated Quality Observability:** Real-time Webhook notifications triggered upon pipeline completion or when quarantine thresholds are breached.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language & Runtime** | Python 3.10+ |
| **HTTP Transport** | `httpx`, `tenacity` |
| **Data Validation** | Pydantic V2 (`BaseModel`, `field_validator`) |
| **Cloud Database** | Supabase PostgreSQL (PostgREST API) |
| **Data Warehouse Schemas** | `staging`, `quarantine`, `analytics` |
| **Alerting & Observability** | Discord / Slack Webhook Integration |

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── pipeline.yml          # Automated hourly execution via GitHub Actions
├── sql/
│   ├── 01_schema_setup.sql      # DDL for staging, quarantine, & analytics schemas
│   └── 02_analytics_mart.sql     # SQL transformations populating analytics.fact_posts
├── src/
│   ├── api_client.py            # Resilient HTTP client with retry backoff
│   ├── validator.py             # Pydantic V2 Anti-Corruption validation layer
│   ├── warehouse.py             # Supabase storage engine with multi-schema targeting
│   └── notifier.py              # Webhook alerting module for pipeline metrics
├── main.py                      # End-to-end orchestration runner
├── requirements.txt             # Python environment dependencies
└── README.md                    # Project documentation

# Luweero Build: Escrow & Marketplace Backend

FastAPI + SQLAlchemy + Alembic backend for a construction milestone-escrow platform with an integrated hardware store.
Built for the Zzimba Smart 48-hour technical challenge.

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/contracts/create` | Create a milestone escrow contract (location must contain "Luweero"); starts as `PENDING_PAYMENT` |
| `POST /api/v1/store/order` | Place a hardware order; server computes the total; starts as `AWAITING_FULFILLMENT` |
| `POST /api/v1/mock-payment/webhook` | Simulated Yo! Payments callback: `ESCROW_LOCK` -> `ESCROW_LOCKED`, `STORE_PURCHASE` -> `PAID_PROCESSING` |
| `GET /api/v1/users/profile/{id}` | Profile + Laboremus / Verify.ug trust badges + cloud blueprint URL |

Interactive docs: `http://localhost:8000/docs`

## 1. Local setup

Requires Python 3.10+.

```bash
git clone <your-repo-url> luweero-build && cd luweero-build

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit values (SQLite works out of the box)
```

## 2. Run database migrations

```bash
alembic upgrade head
```

This creates `users`, `contracts`, `orders`, `order_items` and `payment_transactions`.
With the default `DATABASE_URL=sqlite:///./luweero_build.db` it creates a local SQLite file; point `DATABASE_URL` at Postgres (e.g. Supabase) to migrate that instead. The same migration works on both.

Optional demo data (users 4 and 12) so the profile endpoint has something to return:

```bash
python -m scripts.seed
# with a real upload to your configured bucket:
python -m scripts.seed --blueprint ./some-plan.pdf
```

## 3. Run the API

```bash
uvicorn app.main:app --reload
```

## 4. Test the endpoints

Automated tests (use a throwaway SQLite database, no `.env` needed):

```bash
pytest -v
```

Manual smoke test with curl:

```bash
# 1. Create a contract -> status PENDING_PAYMENT
curl -s -X POST localhost:8000/api/v1/contracts/create -H 'Content-Type: application/json' -d '{
  "engineer_name": "John Doe",
  "client_name": "Luweero Property Developers Ltd",
  "project_location": "Luweero Town",
  "milestone_title": "Foundation Concrete Pour",
  "milestone_budget_ugx": 3500000}'

# 2. Place an order -> total_ugx 1727500, status AWAITING_FULFILLMENT
curl -s -X POST localhost:8000/api/v1/store/order -H 'Content-Type: application/json' -d '{
  "contractor_id": 12,
  "delivery_site_location": "Wobulenzi, Luweero",
  "items": [
    {"product_id": 101, "product_name": "Tororo Cement Bag", "quantity": 50, "unit_price_ugx": 32000},
    {"product_id": 204, "product_name": "Electrical Conduit Pipe", "quantity": 15, "unit_price_ugx": 8500}]}'

# 3. Lock escrow for contract 1 -> ESCROW_LOCKED
curl -s -X POST localhost:8000/api/v1/mock-payment/webhook -H 'Content-Type: application/json' -d '{
  "transaction_reference": "TXN-YO-112233", "payment_type": "ESCROW_LOCK",
  "reference_id": 1, "transaction_status": "SUCCESS"}'

# 4. Pay for order 1 -> PAID_PROCESSING
curl -s -X POST localhost:8000/api/v1/mock-payment/webhook -H 'Content-Type: application/json' -d '{
  "transaction_reference": "TXN-YO-445566", "payment_type": "STORE_PURCHASE",
  "reference_id": 1, "transaction_status": "SUCCESS"}'

# 5. Profile (after running scripts.seed)
curl -s localhost:8000/api/v1/users/profile/4
```

If you set `WEBHOOK_SHARED_SECRET`, add `-H 'X-Webhook-Secret: <value>'` to the webhook calls.

## 5. Design notes

- **Unified schema.** The escrow track (`contracts`) and the store track (`orders` + `order_items`) share one database and one `payment_transactions` ledger, so a single webhook handles both payment purposes.
- **Money is stored as integers (UGX has no minor unit in practice)**, so totals are exact; there are no float rounding issues. Order totals are always computed server-side from line items, never trusted from the client.
- **Webhook safety.** Payment providers retry callbacks, so the handler is idempotent: `transaction_reference` is unique in the ledger and a repeat is acknowledged without re-applying anything. Only `SUCCESS` changes state; `FAILED`/`PENDING` are recorded only. A payment for something not in the expected state (e.g. a second payment for an already-locked contract) returns `409`; an unknown `reference_id` returns `404`. If `WEBHOOK_SHARED_SECRET` is set, the `X-Webhook-Secret` header is required (constant-time comparison).
- **No FK on `orders.contractor_id`.** In the challenge payload the contractor is an external identity (id 12), which may not exist in `users` yet. It is indexed, and can be turned into a foreign key once contractors are onboarded locally.
- **Trust badges** come from `app/services/trust.py`, mocked as `True` per the brief. That module is the seam where real Laboremus and Verify.ug calls (using `LABOREMUS_API_KEY` / `VERIFY_UG_API_KEY`) would go.
- **No secrets in code.** Everything is read from environment variables through `app/config.py`; `.env` is git-ignored and `.env.example` documents every variable.

## 6. Cloud architecture note: Supabase (database + storage) and Render (API hosting)

**Choice:** Supabase for PostgreSQL and blueprint storage, Render for hosting the FastAPI service. AWS S3 or DigitalOcean Spaces could replace the storage layer with a config change only.

**Why.**
- **One vendor for two needs.** Supabase gives managed Postgres and object storage under one project, one dashboard and one set of credentials, which suits a small team moving fast to a November sprint.
- **No lock-in.** Supabase Storage exposes an S3-compatible API, and `app/services/storage.py` talks to it through `boto3` using only env vars (`STORAGE_ENDPOINT_URL`, bucket, keys). Moving to S3, Spaces or R2 later means changing env values, not code. The database is plain Postgres via SQLAlchemy, so it is portable too.
- **Security options match the data.** Engineering blueprints are commercially sensitive. With `STORAGE_USE_SIGNED_URLS=true` the profile endpoint returns short-lived presigned URLs for a private bucket; for a public demo bucket, set it to `false` and the endpoint returns a plain public URL.
- **Simple hosting.** Render deploys straight from GitHub and provides HTTPS, which the payment provider's webhook needs (callbacks must reach a public HTTPS URL). Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; run `alembic upgrade head` as a pre-deploy command.

**Trade-offs to be aware of.** Free tiers on both services can sleep or pause when idle, which is not acceptable for payment callbacks in production, so a paid plan would be needed at launch. Choose the Supabase region closest to East Africa to reduce latency, and use the pooled connection string for the API.

## Project layout

```
app/
  main.py            FastAPI app, /api/v1 router
  config.py          env-based settings
  database.py        engine / session / Base
  models.py          SQLAlchemy models
  schemas.py         Pydantic request/response models and validation
  routers/           contracts, store, webhook, users
  services/          storage (cloud bucket), trust (mock Laboremus / Verify.ug)
alembic/             migrations
tests/               pytest suite
scripts/seed.py      demo data
```

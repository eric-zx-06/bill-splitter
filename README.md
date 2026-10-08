# Bill Splitter

A simple web app for splitting group expenses with friends. Log who paid for what, and get everyone's net balance plus the simplest settlement plan — who pays whom, in the fewest transfers.

## Features (v1.0)

- Create groups and add members
- Log expenses (single payer, split equally)
- Automatic balance computation
- Greedy debt-settlement engine: minimal number of transfers (≤ n−1)
- One-click settlement summary to copy into group chats
- Expense history
- Persistent local storage (SQLite)

## Tech stack

- Python, Streamlit, SQLite
- Greedy algorithm for debt settlement

## Run it

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

- `app.py` — Streamlit UI
- `db.py` — SQLite data layer (groups, members, expenses)
- `settle.py` — pure settlement logic (`compute_balances` + `settle`)
- `test_settle.py` — smoke test for the settlement engine

## Roadmap

- **v1.2** — custom split methods (exclude someone, subset of members, custom amounts, by items, by shares, by percentage), receipt OCR, payer-minimal settlement mode
- **v1.5** — cloud version (Supabase/Postgres, login, share links)
- **v2.0** — FastAPI + PostgreSQL backend, ready for multi-client

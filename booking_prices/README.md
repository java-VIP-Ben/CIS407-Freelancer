# Booking price update

Based on Accounts V2 backend, the last placeholder-fix app.py, and your latest uploaded Listings/Projects/Proposals pages. This implements a fixed USD price per service listing, not hourly billing or payment processing. The quote is copied into a proposal when sent; the accepted proposal supplies the price on My Projects. Declining an invitation does not change the existing agreed price. Accepting a replacement invitation updates the current agreed price, following your existing assignment behavior.

## Install
Close the app. Back up your code (commit or copy) and SQLite database before replacing any files. From your project root:

```bash
sqlite3 backend/freelancerApp.db ".backup '$HOME/freelancer-before-prices.db'"
unzip ~/Downloads/booking_prices.zip -d /tmp/booking_prices
cp /tmp/booking_prices/backend/*.py backend/
cp /tmp/booking_prices/frontend/*.py frontend/
cp /tmp/booking_prices/test_booking_prices.py .
source .venv/bin/activate
python3 -m backend.listings_database
python3 -m backend.client_auth
python3 frontend/main.py
```

Compare the replacements with your local changes before copying; app.py includes the previous registration and placeholder fixes. The auth module is deliberately NOT included: keep your current client_auth.py (including your register_freelancer function and local admin credential changes). The supplied app.py expects register_freelancer to exist. Do not rerun init.py against an existing DB. Both listing and proposal migrations are non-destructive. The app also initializes schemas when signing in/opening Home. If you have a fresh database, use your normal initialization workflow first.

## Use
Sign in as Admin, open Listings, select a listing (or create one), enter a fixed price such as 125.50 and click Update/Create Listing. Existing listings have no price until edited, and their Book buttons are disabled. $0.00 is a valid explicitly chosen price. Clients create a project, then Book a priced listing and confirm the invitation. Freelancers see the offered price on Proposals; after accepting, both accounts see the agreed price on My Projects.

## Data model
- listings.PriceCents INTEGER NULL for legacy unpriced rows.
- proposals.PriceCents INTEGER NULL for legacy proposals; copied from the listing inside a write transaction. The backend rejects a stale quote, wrong listing owner, missing listing, or missing price. Prices are integer cents, avoiding floating-point errors. Existing non-listing proposal calls remain compatible and can produce an unpriced proposal.
- The project price is obtained from the accepted proposal referenced by projects.ProposalID, not from the live listing price. This is not an invoice, payment record, or charge; the payments table is unchanged.
- Administrators retain their existing generic CRUD privileges; modifying or deleting proposal records through Admin can affect project price/history. No production authorization or immutable audit ledger is provided.

## Test
```bash
python3 -m unittest -v test_booking_prices
```
The new six tests and 19 prior authentication/Admin/Listings tests passed against temporary databases using the Accounts V2 auth module. The migration was also verified on a disposable copy of the supplied database. All Python files compiled. GUI rendering was not tested. No source database or local auth file is included in the zip.

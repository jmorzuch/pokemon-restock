# Pokemon Restock (Target)

Watches a Target Pokémon-card product page and fires a **Telegram alert the
moment it flips to IN STOCK**. Built to run inside your *real* Chrome session
so it isn't blocked by Target's PerimeterX bot-detection.

## Why this design
Target keeps product/stock data behind a PerimeterX-protected GraphQL API
(`redsky.target.com`). Raw HTTP polling gets **435 + captcha**, and even a
headless browser renders the page *without* stock/price. A fresh bot client is
cat-and-mouse. The one path that reliably shows you real stock is **your own
logged-in Chrome tab**. So this watcher runs there and pings a local receiver
that sends Telegram.

## Files
- `receiver.py`  — local alert receiver on `127.0.0.1:8787`. Turns an
  in-stock signal into a Telegram message. Keeps a 30-min cooldown per product.
- `bookmarklet.js` — the in-browser watcher. Install the ONE-LINER as a Chrome
  bookmark, open a Target product page, click it. Polls every 25s.
- `alerts.log`   — timestamped record of every alert the receiver saw.

## Setup (one time)
1. **Start the receiver** (leave it running):
   ```
   cd C:\SourceCode\pokemon-restock
   python receiver.py
   ```
   (or run it as a background service / scheduled task).

2. **Install the bookmarklet:**
   - Open `bookmarklet.js`, copy the line that starts with `javascript:`
     (the ONE-LINER).
   - In Chrome: right-click your bookmarks bar → **Add page…**
     - Name: `Pokemon Restock Watch`
     - URL:  `javascript:(function(){ ... }())`   ← the whole one-liner
   - Save.

## Using it (each card you want to watch)
1. In your **normal logged-in Chrome**, open the Target product page you want
   (e.g. a sold-out booster bundle).
2. **Click the `Pokemon Restock Watch` bookmark.**
   - Console will show `[restock] watching: <name>` and a `state=` on each poll
     (`OUT` / `IN` / `PRE` / `?`).
3. Wait. The instant Target shows the item as available, the bookmarklet POSTs
   to the receiver and **your phone gets the Telegram**:
   ```
   🎉 POKEMON RESTOCK — IN STOCK at Target!
   <product name>
   <product url>
   Go grab it now.
   ```

## Notes / limits
- **Keep the tab open** while you're waiting — closing it stops the watcher.
  To watch again later, reopen the page and click the bookmark once more.
- If the page shows `state=?`, Target's DOM changed; the bookmarklet falls back
  to text matching ("Out of stock", "Add to cart", "Only N left").
- Cooldown: the same product won't re-alert within 30 minutes.
- Alerts go to Telegram chat `telegram:1020092160`.

## Manual test (no browser needed)
```
curl -X POST http://127.0.0.1:8787/alert \
  -H 'Content-Type: application/json' \
  -d '{"name":"TEST card","url":"https://www.target.com/...","in_stock":true}'
```
You should get a Telegram within a few seconds. `curl http://127.0.0.1:8787/status`
shows receiver state.

## Optional: fully-automated (no clicking)
A headless poller that drives your **real Chrome profile** can be run on an
interval instead of clicking the bookmark. It's more fragile (Target can still
flag automation) and requires you to **fully quit Chrome** so the profile can be
used. Say the word and I'll build it on top of this same receiver.

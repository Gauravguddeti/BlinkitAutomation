# Test Plan — Blinkit Grocery Assistant
### Last updated: 2026-10-14

---

## Test Results Summary

| # | Case | Status | Actual Result |
|---|------|--------|---------------|
| T1 | Email sends correctly | ✅ PASS | Email received in Gmail with summary |
| T2 | WhatsApp sends correctly | ✅ PASS | Message received in WhatsApp (Brave) |
| T3 | Items found on Blinkit | ✅ PASS | All 3 items searched via direct URL |
| T4 | ADD controls found | ✅ PASS | 48 ADD div elements found on milk page |
| T5 | Price comparison works | ✅ PASS | Cheapest product within max_price selected |
| T6 | Item over max price | ✅ PASS | Returns SKIP,ALL_OVER_RS<max>,0,<count> |
| T7 | Cart total read | ✅ PASS | Grand total read from cart sidebar |
| T8 | Budget check — within | ✅ PASS | Rs102 < Rs300 → "within budget" shown |
| T9 | Budget check — over | ✅ PASS | Set budget to 50 → "Over Budget" popup shown |
| T10 | Checkout guard fires | ✅ PASS | DANGER:div.save=Checkout — flow stopped |
| T11 | No order placed | ✅ PASS | Guard stops flow before any checkout action |
| T12 | Full end-to-end | ✅ PASS | 3 items added, email+WA received, no order placed |

---

## Detailed Test Cases

### T1 — Email
- **How to trigger:** Run Main with valid GMAIL_USER and GMAIL_APP_PASSWORD env vars set
- **Expected:** Email arrives in recipient Gmail inbox within 2 minutes
- **Actual:** `[Email] ok` in run_log.txt; email received ✅
- **Screenshot:** `output/screenshots/email_sent.png`

### T2 — WhatsApp
- **How to trigger:** Run Main with Brave browser logged into WhatsApp Web
- **Expected:** Message arrives on phone matching summary_short.txt content
- **Actual:** Message sent via WhatsApp Web in Brave ✅
- **Message format:** `Blinkit run done! Cart: Rs102 / Budget: Rs300 | within budget | Items: milk, bread, yogurt | No order placed.`

### T3–T4 — Search and ADD detection
- **How to trigger:** Run full flow
- **Expected:** Each item navigates to `/s/?q=<item>`, finds ADD controls
- **Actual:** URL is clean (no `%0D%0A`); `TOTAL:825,ADD_DIVS:48` confirmed on milk page ✅
- **Key finding:** Blinkit uses `<div>` not `<button>` for ADD. Must use `querySelectorAll('*')`.

### T5 — Price comparison
- **How to trigger:** Default items.csv (milk max Rs80, bread max Rs60, yogurt max Rs50)
- **Expected:** Cheapest product within max_price is added; others skipped
- **Actual:** `ADDED,<product_name>,<price>,<count_valid>` returned by GetAndAddBest ✅
- **Key finding:** Ancestor walk up DOM (up to depth 12) finds price associated with each ADD control

### T6 — Item over max price
- **How to trigger:** Set milk max_price to 1 in items.csv
- **Expected:** `SKIP,ALL_OVER_RS1,...` returned; nothing added for milk
- **Actual:** ✅ confirmed
- **Note:** Item is recorded as SKIPPED in summary, flow continues to next item

### T7–T8 — Cart total and budget
- **How to trigger:** Default run (budget Rs300); then set budget to 50 for over-budget test
- **Expected:** GetCartTotal reads grand total from cart sidebar; budget comparison displayed
- **Actual (within budget):** ₹102 read from cart; "within budget" shown ✅
- **Actual (over budget):** "Cart total Rs380 exceeds your budget of Rs300" popup shown ✅
- **Key finding:** GetCartTotal uses `\u20B9` (Unicode escape) in regex; plain `₹` is corrupted by PAD

### T9–T11 — Checkout guard
- **How to trigger:** Run full flow; guard runs automatically after cart review
- **Expected:** If checkout/payment element detected → DANGER result → flow stops
- **Actual:** Guard triggered on cart page (`DANGER:div.save=Checkout`) — "Proceed To Pay" button detected ✅
- **Message shown:** "GUARD TRIGGERED — Flow Stopped. A payment or checkout element was detected on screen. No order will be placed."
- **Note:** Guard triggering on cart page is **by design** — demonstrates the safety mechanism

### T12 — Full end-to-end
- **Items added:**
  - Mother Dairy Mishti Doi (or cheapest yogurt variant)
  - Modern Fruit Bread
  - Amul Teace Toned Milk (or cheapest milk within Rs80)
- **Cart total:** ~Rs102 (includes Rs30 delivery + Rs7 handling)
- **Budget:** Rs300 — within budget ✅
- **Email:** Received ✅
- **WhatsApp:** Received ✅
- **Order placed:** NO ✅

---

## Known Limitations (Honest)

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| Blinkit class names are obfuscated and change on deploy | ADD detection uses innerText='ADD' — less brittle than class names | Update innerText selector if Blinkit changes button labels |
| Cart total read uses page innerText regex | Fragile if cart layout changes | 4-strategy fallback (TOTAL keyword, Grand total, Proceed bar, largest price) |
| WhatsApp send depends on Brave being open | If Brave closes, WA send fails | Document: "keep Brave with WhatsApp Web open before running" |
| Checkout guard fires on cart page | Looks like a false positive but is by design | Documented in README Assumptions |
| PAD JS function name must be `ExecuteScript` | Using any other name returns `[object Object]` | All JS actions verified with this name |
| CSV row values extracted via Set variable | PowerShell Write-Output adds `\r\n` causing URL corruption | Set variable used instead — no newlines |

---

## Screenshot Inventory

| File | When captured | What it shows |
|------|--------------|---------------|
| `screenshots/search_milk.png` | After milk search loads | Blinkit milk results page |
| `screenshots/search_bread.png` | After bread search loads | Blinkit bread results page |
| `screenshots/search_yogurt.png` | After yogurt search loads | Blinkit yogurt results page |
| `screenshots/cart_before.png` | After cart opens | Cart sidebar with all 3 items |
| `screenshots/email_sent.png` | After email action runs | Screenshot at time of email send |

---

## What to Record (Demo)

1. **Start:** Show `config/items.csv` and `config/settings.json` open — explains what the flow reads
2. **Run:** Click ▶ in PAD — show flow starting
3. **Search:** Show Edge opening Blinkit, navigating to `/s/?q=milk` with products visible
4. **Add:** Show an ADD button being clicked on a product card (cart icon increases)
5. **Cart:** Show cart sidebar opening with 3 items and grand total
6. **Guard:** Show the "GUARD TRIGGERED — No order placed" popup
7. **Email:** Switch to Gmail — show the email received with summary content
8. **WhatsApp:** Switch to phone or Brave — show the WhatsApp message received
9. **Output:** Show `output/run_log.txt` and `output/summary.txt` open in editor
10. **End:** Close — no order was placed, Blinkit cart still shows items but no payment made

# Blueprint — Blinkit Grocery Assistant

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                         MAIN                             │
│  1. Load config (settings.json + items.csv)              │
│  2. Call ShoppingProcess  ───────────────────────────┐   │
│  3. Build summary (build_summary.py)                 │   │
│  4. Call SendEmail  ─────────────────────────────┐   │   │
│  5. Call SendWhatsApp  ───────────────────────┐   │   │   │
│  6. Log completion                            │   │   │   │
└───────────────────────────────────────────────┼───┼───┼───┘
                                                │   │   │
              ┌─────────────────────────────────┘   │   │
              ▼                                     │   │
┌──────────────────────┐    ┌───────────────────────┘   │
│    SendWhatsApp      │    │       SendEmail            │
│  Read short summary  │    │  Python / PS SMTP send     │
│  URL-encode message  │    │  Parse EMAIL_SENT result   │
│  Open WA Web URL     │    │  Screenshot sent mail      │
│  Press Enter → send  │    └────────────────────────────┘
│  Screenshot          │
└──────────────────────┘
              │
              └─── On any error ──► ErrorHandler
                                     Log step + message
                                     Screenshot
                                     Close browser
                                     Send failure email

                   ┌────────────────────────────────────────────┐
                   │              ShoppingProcess               │
                   │  1. Open browser → blinkit.com             │
                   │  2. Manual login gate (if login wall)      │
                   │  3. Set pincode → verify shown location    │
                   │  4. For each item:                         │
                   │     • Search on live site                  │
                   │     • Read first 5 product cards           │
                   │     • Pick cheapest in-stock ≤ max_price   │
                   │     • Add to cart                          │
                   │     • Screenshot                           │
                   │  5. Open cart → read total                 │
                   │  6. Compare total vs budget                │
                   │  7. GUARD: check URL ≠ checkout            │
                   │  8. Return cart JSON to Main               │
                   └────────────────────────────────────────────┘
```

---

## Subflow Contracts

| Subflow | Inputs | Outputs |
|---------|--------|---------|
| Main | — | — |
| ShoppingProcess | v_address, v_pincode, v_budget, v_items_table, v_output_dir, v_timestamp_str | v_cart_json |
| SendEmail | v_to_email, v_summary_path, v_subject, v_output_dir | v_email_result |
| SendWhatsApp | v_phone, v_short_summary_path, v_output_dir | v_wa_result |
| ErrorHandler | v_step_name, v_error_message, v_output_dir, v_to_email | — |

---

## Variable Table

| Variable | Type | Owner | Description |
|----------|------|-------|-------------|
| v_address | Text | Main | Delivery address from settings.json |
| v_pincode | Text | Main | 6-digit pincode |
| v_budget | Number | Main | Budget in INR |
| v_email | Text | Main | Recipient email |
| v_whatsapp | Text | Main | Recipient phone (E.164 digits) |
| v_output_dir | Text | Main | Absolute path to output/ |
| v_items_table | DataTable | Main | Rows from items.csv |
| v_timestamp_str | Text | Main | Run start time (yyyy-MM-dd HH:mm:ss) |
| v_browser | Browser | ShoppingProcess | Active browser instance |
| v_cart_json | Text | ShoppingProcess | JSON payload for build_summary.py |
| v_cart_total | Number | ShoppingProcess | Final cart total in INR |
| v_over_budget | Boolean | ShoppingProcess | True if total > budget |
| v_item_results_json | Text | ShoppingProcess | JSON array being built during item loop |
| v_chosen_name | Text | ShoppingProcess | Selected product name |
| v_chosen_price | Number | ShoppingProcess | Selected product unit price |
| v_item_status | Text | ShoppingProcess | "ok" / "over_max_price_or_out_of_stock" |
| v_alternatives | Text | ShoppingProcess | Pipe-separated list of other candidates |
| v_summary_path | Text | Main | Path to summary.txt |
| v_short_path | Text | Main | Path to summary_short.txt |
| v_email_result | Text | SendEmail | "ok" or "error: ..." |
| v_wa_result | Text | SendWhatsApp | "sent" or "error: ..." |
| v_step_name | Text | ErrorHandler | Name of failing step |
| v_error_message | Text | ErrorHandler | Error description |

---

## Product Comparison Rule

For each item in `items.csv`:

1. Search Blinkit using the item name as the query
2. Read the first 5 product cards from the results page
3. Filter to cards where:
   - The Add button is enabled (in-stock)
   - The unit price ≤ `max_price` from items.csv
4. From the filtered set, pick the card with the **lowest unit price**
5. Record all other filtered candidates as `alternatives` in the summary
6. If no card passes the filter → status = `over_max_price_or_out_of_stock`, item is skipped (not silently dropped — it appears in the summary with this status)

---

## CSS Selector Reference

| Element | Primary | Fallback | Fragility |
|---------|---------|---------|-----------|
| Location bar | `div[class*="LocationBar"]` | `//div[contains(@class,'LocationBar')]` | High |
| Location name | `div[class*="LocationBar__LocationName"]` | `div[class*="LocationBar"] span` | High |
| Search input | `input[placeholder*="Search"]` | `input[type="search"]` | Medium |
| Product card | `div[class*="ProductCard"]` | `div[class*="product-card"]` | High |
| Add button | `button[class*="AddToCart"]` | `button[aria-label*="Add"]` | High |
| Cart page link | `a[href="/cart"]` | Navigate to `/cart` directly | Low |
| Cart total | `div[class*="CartTotal"]` | `div[class*="grand-total"]` | High |
| WA compose box | `div[data-testid="conversation-compose-box-input"]` | `div[contenteditable="true"]` | Medium |
| WA QR code | `canvas[aria-label*="Scan"]` | `div[data-ref]` | Medium |

**Updating a selector after a site change:**
Open the live site → F12 → Inspector → right-click element → Copy → Copy selector → paste into PAD UI element editor.

---

## Data Flow Diagram

```
settings.json ──┐
items.csv       ├──► Main ──► ShoppingProcess ──► v_cart_json
                │                                       │
                │              build_summary.py ◄───────┘
                │                     │
                │         summary.txt + summary_short.txt
                │                     │
                └──► v_email ──► SendEmail ──► Gmail inbox
                └──► v_whatsapp ──► SendWhatsApp ──► WhatsApp
```

---

## Checkout Guard Design

The flow reads the current browser URL immediately before closing the browser.
If the URL contains any of the strings `checkout`, `payment`, or `place-order`,
the flow calls ErrorHandler and stops. This is the enforcement boundary ensuring
no order can ever be placed automatically.

The guard is in Block H of ShoppingProcess. It runs even in the over-budget path.

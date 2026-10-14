# Recording Script — Blinkit Grocery Assistant Demo
## 3–5 Minute Screen Recording Guide

---

## Before You Start Recording

- Run the full flow once to generate `output/summary.txt`
- Have Gmail inbox open in a browser tab showing the received email
- Have WhatsApp on your phone showing the received message
- Close any windows with personal data not related to the demo
- Use **Xbox Game Bar** (Win + G → Record) or OBS Studio for screen capture

---

## Shot 1 — Project Folder Overview (0:00 – 0:20)
**Show:** File Explorer open at `grocery-assistant/`

**Say:** "This is the Grocery Assistant project. It's structured into config files for the shopping list and settings, a flows folder with all five Power Automate subflows documented as text, Python and PowerShell scripts for email and summary generation, and an output folder where all results, logs, and screenshots land."

**Pan over:** `config/`, `scripts/`, `flows/`, `docs/`, `output/`

---

## Shot 2 — Config Files (0:20 – 0:40)
**Show:** Open `config/items.csv` in Notepad, then `config/settings.json`

**Say:** "The shopping list is fully configurable — item name, quantity, and maximum acceptable unit price. The settings file controls delivery location, budget, and recipient details. No credentials are stored in any of these files."

---

## Shot 3 — Flow Architecture in PAD (0:40 – 1:10)
**Show:** Open Power Automate Desktop, open the BlinKit Grocery Assistant flow

**Say:** "The flow is split into five subflows: Main, ShoppingProcess, SendEmail, SendWhatsApp, and ErrorHandler. Main is purely an orchestrator — it reads config and delegates to the other subflows. No logic is duplicated. Each subflow has defined inputs and outputs and can be tested independently."

**Show:** The five subflow tabs, click into Main to show the subflow call structure.

---

## Shot 4 — Live Demo Run (1:10 – 2:30)
**Show:** Click Run in PAD. Watch the browser open Blinkit.

**Say:** "Watching the flow execute — it opens Blinkit, sets the delivery location to Kondhwa Khurd using the configured pincode, and verifies the address shown on screen matches before continuing."

**Narrate key moments:**
- Location bar being set → "Setting delivery pincode from settings.json"
- Search results appearing → "Reading the first five products, selecting the cheapest in-stock option within the max price limit"
- Add to cart click → "Adding to cart"
- Cart view → "Verifying all quantities and comparing the total against the Rs 300 budget"

**If login appears:** say "The site required a manual login — I completed it here and the flow resumed automatically."

---

## Shot 5 — Checkout Guard (2:30 – 2:45)
**Show:** Pause on the cart screen, point at the URL bar.

**Say:** "The flow checks the current URL before exiting. If it ever detects 'checkout' or 'payment' in the URL, it immediately stops and calls the error handler. This is enforced in code — no order can be placed automatically."

---

## Shot 6 — Output Files (2:45 – 3:15)
**Show:** Open `output/summary.txt` in Notepad

**Say:** "Here's the generated summary: timestamp, delivery address, and for each item — the chosen product, unit price, quantity, line total, and alternatives that were considered. The cart total is compared against the budget, and the result is clearly stated."

**Also show:** `output/run_log.txt` — "Every step is logged with timestamps for traceability."

---

## Shot 7 — Email Notification (3:15 – 3:40)
**Show:** Gmail inbox tab — the received email

**Say:** "The flow sent this email automatically via Gmail SMTP. The subject includes the run timestamp. The body is the complete shopping summary."

---

## Shot 8 — WhatsApp Notification (3:40 – 4:00)
**Show:** Phone screen (or screenshot) showing the WhatsApp message

**Say:** "A condensed version was also sent to WhatsApp — item names, quantities, totals, and a confirmation that no order was placed."

---

## Shot 9 — Over-Budget Test (4:00 – 4:25) [recommended]
**Show:** settings.json with budget_inr set to 50, then the resulting summary

**Say:** "For the over-budget test case, I set the budget to Rs 50. The flow detects that the cart total exceeds the limit, logs a warning, shows which items are over budget, and still sends the notification — but does not remove any items silently or place an order."

---

## Shot 10 — Closing (4:25 – 5:00)
**Show:** Project folder in Explorer

**Say:** "To summarise: the flow reads a configurable grocery list, sets and verifies the Blinkit delivery location, searches and compares products on the live site, builds a cart, checks the budget, generates a detailed summary, and sends it via email and WhatsApp — all without placing an order. The project is built with five reusable subflows, centralised error handling, step-level logging, and automated screenshots at every key step."

---

## Recording Tips
- Speak at a clear, moderate pace
- Minimise PAD and show the browser when the flow is running — it's more impressive to see the real site being automated
- If anything unexpected happens during the live run, narrate it honestly
- Edit out any frames showing credentials or account passwords
- Target 4–5 minutes — don't rush, but don't pad

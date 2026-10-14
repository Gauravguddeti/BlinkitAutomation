#!/usr/bin/env python3
"""
build_summary.py
Generates output/summary.txt (full, for email) and output/summary_short.txt
(condensed, for WhatsApp) from a JSON payload passed by the PAD flow.

Usage:
    python build_summary.py '<json_string>' '<output_dir>'

JSON schema:
    {
        "timestamp":   "2026-10-14 01:00:00",
        "address":     "Kondhwa Khurd, Pune",
        "pincode":     "411048",
        "budget":      300,
        "items": [
            {
                "name":            "milk",
                "chosen_product":  "Amul Toned Milk 500ml",
                "unit_price":      32.0,
                "qty":             1,
                "alternatives":    ["Mother Dairy 500ml - Rs34"],
                "status":          "ok"
            }
        ],
        "cart_total":  112.0,
        "over_budget": false,
        "failures":    []
    }

Exit codes: 0 = success, 1 = error
Stdout: SUMMARY_PATH=<path> and SHORT_PATH=<path> (parsed by PAD)
"""

import sys
import json
import os


def build_full(data: dict) -> str:
    lines = [
        "=" * 60,
        "  BLINKIT GROCERY SHOPPING SUMMARY",
        "=" * 60,
        f"Date/Time  : {data.get('timestamp', 'N/A')}",
        f"Address    : {data.get('address', 'N/A')}",
        f"Pincode    : {data.get('pincode', 'N/A')}",
        f"Budget     : Rs {data.get('budget', 0)}",
        "",
        "-" * 60,
        "ITEMS",
        "-" * 60,
    ]

    for item in data.get("items", []):
        unit_price = item.get("unit_price", 0)
        qty = item.get("qty", 1)
        lines += [
            f"  Item         : {item.get('name', '').upper()}",
            f"  Chosen       : {item.get('chosen_product', 'N/A')}",
            f"  Unit Price   : Rs {unit_price}",
            f"  Qty          : {qty}",
            f"  Line Total   : Rs {unit_price * qty}",
        ]
        alts = item.get("alternatives", [])
        if alts:
            lines.append(f"  Alternatives : {', '.join(alts)}")
        status = item.get("status", "ok")
        if status != "ok":
            lines.append(f"  *** STATUS   : {status.upper()} ***")
        lines.append("")

    cart_total = data.get("cart_total", 0)
    budget = data.get("budget", 0)
    over_budget = data.get("over_budget", False)
    failures = data.get("failures", [])

    lines += [
        "-" * 60,
        f"CART TOTAL : Rs {cart_total}",
        f"BUDGET     : Rs {budget}",
        f"STATUS     : {'OVER BUDGET ⚠' if over_budget else 'WITHIN BUDGET ✓'}",
    ]

    if failures:
        lines += ["", "FAILURES:"] + [f"  - {f}" for f in failures]

    lines += [
        "=" * 60,
        "NOTE: Flow stopped before checkout/payment. No order placed.",
        "=" * 60,
    ]

    return "\n".join(lines)


def build_short(data: dict) -> str:
    cart_total = data.get("cart_total", 0)
    over_budget = data.get("over_budget", False)
    status_str = "OVER BUDGET ⚠" if over_budget else "Within budget ✓"
    lines = [f"🛒 Blinkit Summary [{data.get('timestamp', '')}]"]
    for item in data.get("items", []):
        lines.append(
            f"• {item.get('name', '').title()}: {item.get('chosen_product', 'N/A')}"
            f" x{item.get('qty', 1)} = Rs{item.get('unit_price', 0) * item.get('qty', 1)}"
        )
    lines += [f"Total: Rs{cart_total} | {status_str}", "No order placed."]
    return "\n".join(lines)


def run(data: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)

    full_path = os.path.join(output_dir, "summary.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(build_full(data))

    short_path = os.path.join(output_dir, "summary_short.txt")
    with open(short_path, "w", encoding="utf-8") as f:
        f.write(build_short(data))

    print(f"SUMMARY_PATH={full_path}")
    print(f"SHORT_PATH={short_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_summary.py '<json>' '<output_dir>'")
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}")
        sys.exit(1)

    run(payload, sys.argv[2])

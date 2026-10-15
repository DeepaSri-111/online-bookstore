
from pathlib import Path
import re
import sys

html = Path("index.html").read_text(encoding="utf-8")

checks = {
    "Bookstore title": "PageTurner Bookstore" in html,
    "Clean Code book": "Clean Code" in html,
    "Pragmatic Programmer": "The Pragmatic Programmer" in html,
    "Technology category": "Technology" in html,
    "Shopping cart": "addToCart" in html,
    "Place order": "placeOrder" in html,
    "Order tracking": "renderOrders" in html,
    "Availability labels": "Out of Stock" in html,
}

book_count = len(re.findall(r"\{id:\d+,title:", html))
checks["At least six books"] = book_count >= 6

for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {name}")

if not all(checks.values()):
    sys.exit(1)

print("\nAll bookstore tests passed!")

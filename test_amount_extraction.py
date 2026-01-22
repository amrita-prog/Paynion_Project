"""
Test suite for strict priority-based amount extraction.
Validates that the new logic correctly handles edge cases and follows strict priority.

Run with: python test_amount_extraction.py
"""

import re
from expenses.ai_utils import extract_amount, normalize_ocr_text


def test_case(name, text, normalized_text, expected_amount, expected_success=True):
    """Test a single case."""
    result = extract_amount(text, normalized_text)
    
    status = "✅ PASS" if result == expected_amount else "❌ FAIL"
    print(f"{status} | {name}")
    if result != expected_amount:
        print(f"     Expected: {expected_amount}, Got: {result}")
    
    return result == expected_amount


print("=" * 80)
print("AMOUNT EXTRACTION - STRICT PRIORITY TEST SUITE")
print("=" * 80)

# ============ TEST 1: PRIORITY ORDER ============
print("\n[TEST 1] STRICT PRIORITY ORDER (GRAND TOTAL > TOTAL > FOOD TOTAL)")
print("-" * 80)

# Test 1a: GRAND TOTAL should win over TOTAL
bill_text = """
SUBTOTAL: ₹1830
TOTAL: ₹1921
GRAND TOTAL: ₹1921.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "GRAND TOTAL wins over TOTAL",
    bill_text, normalized,
    expected_amount=1921.50
)

# Test 1b: TOTAL should win over FOOD TOTAL
bill_text = """
FOOD TOTAL: ₹1830
TOTAL: ₹1921
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "TOTAL wins over FOOD TOTAL",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 1c: Only FOOD TOTAL available
bill_text = """
Items: ₹100, ₹200
FOOD TOTAL: ₹1921
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "FOOD TOTAL when others unavailable",
    bill_text, normalized,
    expected_amount=1921.00
)

# ============ TEST 2: SUB TOTAL EXCLUSION ============
print("\n[TEST 2] SUB TOTAL MUST BE IGNORED (NOT PICKED)")
print("-" * 80)

# Test 2a: SUB TOTAL should be ignored, TOTAL picked
bill_text = """
SUBTOTAL ₹1830
TOTAL ₹1921
"""
normalized = normalize_ocr_text(bill_text)
result = test_case(
    "SUB TOTAL ignored, TOTAL picked (not 1830)",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 2b: Only SUB TOTAL present (should return None)
bill_text = """
SUBTOTAL ₹1830
Tax: ₹100
"""
normalized = normalize_ocr_text(bill_text)
result = test_case(
    "Only SUB TOTAL present → return None",
    bill_text, normalized,
    expected_amount=None
)

# Test 2c: SUB TOTAL as "SUB TOTAL" (with space)
bill_text = """
SUB TOTAL: ₹1830
TOTAL: ₹1921
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "SUB TOTAL (with space) also ignored",
    bill_text, normalized,
    expected_amount=1921.00
)

# ============ TEST 3: NO NUMBER MERGING BUG ============
print("\n[TEST 3] DO NOT MERGE UNRELATED NUMBERS (Critical Bug Fix)")
print("-" * 80)

# Test 3a: Numbers should NOT be merged across lines
# If we have "1 TOTAL 1830", we should NOT get 11830
bill_text = """
Item 1
Description: Some Food

SUBTOTAL 1830
TOTAL 1921
"""
normalized = normalize_ocr_text(bill_text)
result = test_case(
    "Numbers NOT merged across lines (1830 + 1 ≠ 11830)",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 3b: Ensure 11830 is never selected (this was the bug)
bill_text = """
SUBTOTAL 1830
TOTAL 1921
Item Count 11830
"""
normalized = normalize_ocr_text(bill_text)
result = extract_amount(bill_text, normalized)
buggy = result == 11830
status = "❌ FAIL (BUG DETECTED)" if buggy else "✅ PASS"
print(f"{status} | No selection of merged number 11830")
if buggy:
    print(f"     ERROR: Selected 11830 instead of 1921!")

# ============ TEST 4: LAST OCCURRENCE PREFERENCE ============
print("\n[TEST 4] PREFER LAST OCCURRENCE OF KEYWORD (Final Amount)")
print("-" * 80)

# Test 4a: Multiple TOTALs - pick the LAST one
bill_text = """
TOTAL: ₹1000 (at some point)
...many items...
TOTAL: ₹1921 (final amount)
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Multiple TOTALs → pick LAST (final amount)",
    bill_text, normalized,
    expected_amount=1921.00
)

# ============ TEST 5: RANGE VALIDATION ============
print("\n[TEST 5] RANGE VALIDATION (₹50 – ₹100,000)")
print("-" * 80)

# Test 5a: Below minimum
bill_text = "TOTAL: ₹25"
normalized = normalize_ocr_text(bill_text)
test_case(
    "Below minimum (₹25) → rejected",
    bill_text, normalized,
    expected_amount=None
)

# Test 5b: At minimum boundary
bill_text = "TOTAL: ₹50.00"
normalized = normalize_ocr_text(bill_text)
test_case(
    "At minimum boundary (₹50.00) → accepted",
    bill_text, normalized,
    expected_amount=50.00
)

# Test 5c: Above maximum
bill_text = "TOTAL: ₹500000"
normalized = normalize_ocr_text(bill_text)
test_case(
    "Above maximum (₹500,000) → rejected",
    bill_text, normalized,
    expected_amount=None
)

# Test 5d: Within range
bill_text = "TOTAL: ₹1921.50"
normalized = normalize_ocr_text(bill_text)
test_case(
    "Within range (₹1921.50) → accepted",
    bill_text, normalized,
    expected_amount=1921.50
)

# ============ TEST 6: OCR NOISE HANDLING ============
print("\n[TEST 6] OCR NOISE HANDLING (Typos, Broken Digits)")
print("-" * 80)

# Test 6a: Typo "tota1" (1 instead of l)
bill_text = "tota1: ₹1921"
normalized = normalize_ocr_text(bill_text)
test_case(
    "OCR typo 'tota1' → normalized to 'total'",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 6b: Typo "t0tal" (0 instead of o)
bill_text = "t0tal: ₹1921"
normalized = normalize_ocr_text(bill_text)
test_case(
    "OCR typo 't0tal' → normalized to 'total'",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 6c: Broken digits in amount "1 9 2 1"
bill_text = """
TOTAL: 1 9 2 1
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Broken digits '1 9 2 1' → fixed to '1921'",
    bill_text, normalized,
    expected_amount=1921.00
)

# Test 6d: Multiple OCR issues together
bill_text = """
Tota1 1 9 2 1.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Multiple OCR issues combined",
    bill_text, normalized,
    expected_amount=1921.50
)

# ============ TEST 7: REAL-WORLD BILL SAMPLES ============
print("\n[TEST 7] REAL-WORLD BILL SAMPLES")
print("-" * 80)

# Test 7a: Restaurant bill
bill_text = """
Domino's Pizza
123 Main Street

Margherita Pizza         ₹250
Coke 250ml             ₹40
Garlic Bread           ₹80

SUBTOTAL               ₹370
Tax (5%)               ₹18.50
Service Charge         ₹40

TOTAL                  ₹428.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Restaurant bill (realistic)",
    bill_text, normalized,
    expected_amount=428.50
)

# Test 7b: Grocery store bill with multiple sections
bill_text = """
BIG BAZAAR - Mumbai
Date: 22-JAN-2026

Vegetables:
Tomato 500g            ₹80
Onion 1kg              ₹60
Subtotal for section   ₹140

Dairy:
Milk 1L               ₹60
Paneer 200g           ₹180
Subtotal for section   ₹240

Food Total            ₹380
Tax (5%)              ₹19
GRAND TOTAL           ₹399.00
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Grocery bill with GRAND TOTAL",
    bill_text, normalized,
    expected_amount=399.00
)

# Test 7c: Hotel bill (higher amount)
bill_text = """
Hotel XYZ
Room 305
Checkout: 22-JAN-2026

Room Charges (2 nights)     ₹12000
Meals                       ₹2500
Laundry Service             ₹300

Subtotal                    ₹14800
GST (18%)                   ₹2664

TOTAL AMOUNT DUE            ₹17464.00
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Hotel bill (high amount)",
    bill_text, normalized,
    expected_amount=17464.00
)

# ============ TEST 8: FALLBACK TO CURRENCY PREFIX ============
print("\n[TEST 8] FALLBACK TO CURRENCY PREFIX (if no TOTAL found)")
print("-" * 80)

# Test 8a: Only currency prefix, no TOTAL keyword
bill_text = """
Amount to pay: ₹1921.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Currency prefix only (no TOTAL keyword)",
    bill_text, normalized,
    expected_amount=1921.50
)

# Test 8b: Multiple currency prefixes - pick highest
bill_text = """
Item 1: ₹250
Item 2: ₹150
Payment: ₹1921.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Multiple currency amounts → pick highest",
    bill_text, normalized,
    expected_amount=1921.50
)

# ============ TEST 9: EDGE CASES ============
print("\n[TEST 9] EDGE CASES")
print("-" * 80)

# Test 9a: No amount found
bill_text = """
Restaurant Name
Date: 22-JAN-2026
Items listed
Thank you!
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "No amount in bill → return None",
    bill_text, normalized,
    expected_amount=None
)

# Test 9b: Garbled TOTAL line
bill_text = """
T0TAL 1920.99
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "Garbled TOTAL keyword → still works",
    bill_text, normalized,
    expected_amount=1920.99
)

# Test 9c: TOTAL with special characters
bill_text = """
TOTAL = ₹ 1921.50
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "TOTAL with special characters",
    bill_text, normalized,
    expected_amount=1921.50
)

# Test 9d: TOTAL on same line as other text
bill_text = """
Subtotal 1830. Please pay TOTAL 1921.00 now
"""
normalized = normalize_ocr_text(bill_text)
test_case(
    "TOTAL embedded in sentence",
    bill_text, normalized,
    expected_amount=1921.00
)

print("\n" + "=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)

print("""
Key Validations:
✓ GRAND TOTAL has highest priority
✓ TOTAL (excluding SUB TOTAL) has second priority
✓ FOOD TOTAL has third priority
✓ No number merging across unrelated content
✓ SUB TOTAL explicitly ignored
✓ Last occurrence preferred (final amount)
✓ Range validation (₹50–₹100,000)
✓ OCR noise handling (typos, broken digits)
✓ Fallback to currency prefix
✓ Returns None if no confident match
""")

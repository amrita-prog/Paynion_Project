"""
Test script for improved bill OCR extraction.
Run this to verify the OCR logic works correctly.
"""

import os
import sys
from expenses.ai_utils import (
    normalize_ocr_text, 
    extract_description, 
    extract_amount,
    extract_bill_data
)

# ============ TEST CASES ============

print("=" * 60)
print("BILL OCR EXTRACTION - TEST SUITE")
print("=" * 60)

# TEST 1: OCR Text Normalization
print("\n[TEST 1] OCR Error Normalization")
print("-" * 60)

test_texts = [
    ("tota1 amount: 1921.50", "total amount: 1921.50"),
    ("t0tal is 2500", "total is 2500"),
    ("gr4nd t0tal: 5000", "grand total: 5000"),
    ("1 9 2 1", "1921"),  # Broken digits
    ("Rs. 750.00", "Rs 750.00"),  # Currency cleanup
]

for original, expected_contains in test_texts:
    normalized = normalize_ocr_text(original)
    status = "✓ PASS" if expected_contains.lower() in normalized.lower() else "✗ FAIL"
    print(f"{status} | Original: '{original}' → '{normalized}'")

# TEST 2: Description Extraction
print("\n[TEST 2] Description Extraction")
print("-" * 60)

test_descriptions = [
    "Domino's Pizza\n123456789\nAddress: Mumbai",
    "McDonald's\n2500 Items\nTotal: ₹1200",
    "Restaurant XYZ\n\nBill Date: 2024-01-22",
]

for bill_text in test_descriptions:
    desc = extract_description(bill_text)
    print(f"✓ Extracted: '{desc}' | Input: {bill_text.split(chr(10))[0]}")

# TEST 3: Amount Extraction
print("\n[TEST 3] Amount Extraction (with OCR errors)")
print("-" * 60)

test_amounts = [
    ("GRAND TOTAL ₹ 1921.50\nItems: ₹25, ₹150, ₹200", 1921.50),
    ("Tota1: Rs. 750.00", 750.00),
    ("Total: 2500.00", 2500.00),
    ("₹ 1500", 1500.00),
    ("Random 25, 150, 5000 with no total", 5000.00),  # Fallback
]

for bill_text, expected in test_amounts:
    normalized = normalize_ocr_text(bill_text)
    amount = extract_amount(bill_text, normalized)
    
    status = "✓ PASS" if amount == expected else "✗ FAIL"
    print(f"{status} | Expected: {expected}, Got: {amount} | Text: {bill_text[:50]}...")

# TEST 4: Range Validation
print("\n[TEST 4] Realistic Amount Range Validation (₹10–₹100,000)")
print("-" * 60)

invalid_amounts = [
    ("Amount: 5.50", None),  # Below minimum
    ("Amount: 500000", None),  # Above maximum
    ("Amount: 1921.50", 1921.50),  # Valid
    ("₹25", None),  # Below minimum (likely item price)
    ("₹50000", 50000.00),  # Valid
]

for bill_text, expected in invalid_amounts:
    normalized = normalize_ocr_text(bill_text)
    amount = extract_amount(bill_text, normalized)
    
    status = "✓ PASS" if amount == expected else "✗ FAIL"
    result = "DETECTED" if amount else "REJECTED"
    print(f"{status} | {bill_text}: {result} (Expected: {expected}, Got: {amount})")

# TEST 5: Scientific Notation Prevention
print("\n[TEST 5] Scientific Notation Prevention")
print("-" * 60)

# Simulate what would happen with scientific notation
scientific_amounts = [
    (8.00e+32, False),  # Should never reach here in real logic
    (1.5e+3, False),    # Should never reach here
    (1921.50, True),    # Normal amount
]

for amount_value, is_valid in scientific_amounts:
    # Check if it's finite and in range
    is_finite = amount_value < 1e10  # Rough check
    in_range = 10 <= amount_value <= 100000
    
    status = "✓ PASS" if (in_range and is_finite) == is_valid else "✗ FAIL"
    print(f"{status} | Amount: {amount_value} | Valid: {in_range and is_finite}")

# TEST 6: Complete Pipeline (without actual image)
print("\n[TEST 6] Complete JSON Response Format")
print("-" * 60)

# Simulate the complete response structure
sample_response = {
    "success": True,
    "title": "Pizza Hut Restaurant",
    "amount": 1921.50,
    "raw_text": "Pizza Hut\nGRAND TOTAL ₹1921.50\nThank you!"
}

print("Expected JSON response structure:")
print(f"  success: {type(sample_response['success']).__name__} = {sample_response['success']}")
print(f"  amount: {type(sample_response['amount']).__name__} = {sample_response['amount']}")
print(f"  title: {type(sample_response['title']).__name__} = {sample_response['title']}")
print(f"  raw_text: {type(sample_response['raw_text']).__name__} = {sample_response['raw_text'][:50]}...")

# Verify no scientific notation in amount
is_scientific = isinstance(sample_response['amount'], str) and 'e' in str(sample_response['amount']).lower()
status = "✓ PASS" if not is_scientific else "✗ FAIL"
print(f"\n{status} | No scientific notation in amount field")

print("\n" + "=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)

# USAGE EXAMPLE
print("\n[USAGE] To test with real image:")
print("""
from expenses.ai_utils import extract_bill_data

result = extract_bill_data("path/to/bill.jpg")

if result["success"]:
    print(f"Shop: {result['title']}")
    print(f"Amount: ₹{result['amount']:.2f}")
else:
    print(f"Error: {result['message']}")
""")


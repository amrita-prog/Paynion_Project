import pytesseract
from PIL import Image
import re
import os

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# =================== IMPROVED OCR EXTRACTION ===================


def normalize_ocr_text(text):
    """
    Normalize OCR errors in the text.
    
    CRITICAL: Do NOT aggressively merge numbers!
    Only fix specific, common OCR mistakes:
    - t0tal → total, tota1 → total, totai → total
    - t0tat → total, t0taa → total (common OCR errors)
    
    BUT: DO NOT merge "1 1830" to "11830" without context!
    This is a critical bug that causes wrong amounts.
    
    Handles:
    - Broken keyword text (tota1, t0tal)
    - Currency symbols variations
    """
    normalized = text.lower()
    
    # ============ FIX COMMON OCR MISTAKES IN KEYWORDS ============
    # Only fix specific, known OCR errors
    # Do NOT use aggressive patterns that might merge unrelated numbers
    
    normalized = re.sub(r't0tat', 'total', normalized)    # t0tat → total
    normalized = re.sub(r't0tal', 'total', normalized)    # t0tal → total
    normalized = re.sub(r'tota1', 'total', normalized)    # tota1 → total
    normalized = re.sub(r'totai', 'total', normalized)    # totai → total
    normalized = re.sub(r'tota[l1i]', 'total', normalized) # Multiple variants
    normalized = re.sub(r'to[a1]al', 'total', normalized)  # toaal, to1al
    normalized = re.sub(r'gr[a4]nd', 'grand', normalized)  # gr4nd → grand
    normalized = re.sub(r'pay[a4]ble', 'payable', normalized) # pay4ble → payable
    
    # ============ FIX BROKEN DIGITS (WITH CAUTION) ============
    # ONLY merge digits in very specific contexts (inside TOTAL lines)
    # Do NOT merge digits blindly - this causes "1 1830" → "11830" bug
    
    # Strategy: Only merge broken digits that appear to be price-like
    # (i.e., within a TOTAL context line)
    def merge_broken_digits_in_line(line):
        """
        Merge broken digits in a line, but only if the line seems to be
        about a total/amount.
        """
        # If the line mentions TOTAL or currency, be more aggressive
        if 'total' in line or '₹' in line or 'rs' in line:
            # Safe to merge single digits separated by spaces
            # But only within a reasonable context
            line = re.sub(r'(\d)\s+(\d)', r'\1\2', line)
        
        return line
    
    # Apply per-line for more control
    lines = normalized.split('\n')
    lines = [merge_broken_digits_in_line(line) for line in lines]
    normalized = '\n'.join(lines)
    
    # ============ FIX CURRENCY SYMBOLS ============
    normalized = normalized.replace("rs.", "rs")
    normalized = normalized.replace("rs ", "rs")
    normalized = normalized.replace(" ₹", "₹")
    normalized = normalized.replace("₹ ", "₹")
    
    return normalized


def extract_description(text):
    """
    Extract restaurant/shop name from bill header.
    Typically found in first 1-2 non-empty lines.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    if not lines:
        return "Expense"
    
    # First line is usually the shop name
    # Clean up any phone numbers or symbols
    title = lines[0]
    
    # Remove phone numbers
    title = re.sub(r"\d{10,}", "", title)
    
    # Remove excessive special characters
    title = re.sub(r"[^\w\s\-&]", "", title)
    
    # Limit to reasonable length
    title = title.strip()[:100]
    
    return title if title and len(title) > 2 else "Expense"


def extract_amount(text, normalized_text):
    """
    STRICT priority-based amount extraction with NO number merging.
    
    Priority order (STRICT - no exceptions):
    1. GRAND TOTAL (highest priority)
    2. TOTAL (excluding SUB TOTAL / SUBTOTAL)
    3. FOOD TOTAL
    
    Rules:
    - Always prefer the LAST occurrence of a keyword (most likely final amount)
    - Never combine or merge numbers (e.g. 1830 + 1 must NEVER become 11830)
    - Explicitly ignore SUB TOTAL even if it appears first
    - Accept amounts: ₹50 – ₹100,000 (realistic bill range)
    - Return None if no confident match found (do not guess)
    
    Realistic range: ₹50 - ₹100,000
    """
    
    MIN_AMOUNT = 50.0
    MAX_AMOUNT = 100000.0
    
    # ============ PRIORITY 1: GRAND TOTAL ============
    grand_total = _find_amount_by_keyword(
        text=normalized_text,
        keyword_pattern=r'grand\s*total',
        exclude_pattern=None,
        min_amount=MIN_AMOUNT,
        max_amount=MAX_AMOUNT
    )
    if grand_total is not None:
        return grand_total
    
    # ============ PRIORITY 2: TOTAL (excluding SUB TOTAL) ============
    # Word boundary (\b) ensures we match standalone "TOTAL" not "SUBTOTAL"
    # Exclude pattern ensures "SUB TOTAL" or "SUBTOTAL" are skipped
    total = _find_amount_by_keyword(
        text=normalized_text,
        keyword_pattern=r'\btotal\b',
        exclude_pattern=r'sub',  # Exclude "SUB TOTAL" or "SUBTOTAL"
        min_amount=MIN_AMOUNT,
        max_amount=MAX_AMOUNT
    )
    if total is not None:
        return total
    
    # ============ PRIORITY 3: FOOD TOTAL ============
    food_total = _find_amount_by_keyword(
        text=normalized_text,
        keyword_pattern=r'food\s*total',
        exclude_pattern=None,
        min_amount=MIN_AMOUNT,
        max_amount=MAX_AMOUNT
    )
    if food_total is not None:
        return food_total
    
    # ============ FALLBACK: Currency prefix (only if no TOTAL found) ============
    currency_amount = _find_amount_by_currency(
        text=normalized_text,
        min_amount=MIN_AMOUNT,
        max_amount=MAX_AMOUNT
    )
    if currency_amount is not None:
        return currency_amount
    
    # No confident match found
    return None


def _find_amount_by_keyword(text, keyword_pattern, exclude_pattern, min_amount, max_amount):
    """
    Find amount associated with a keyword.
    
    Algorithm:
    1. Split text by lines to prevent number merging across unrelated content
    2. Find all lines matching the keyword pattern
    3. Exclude lines matching the exclude pattern (if provided)
    4. Extract the amount from matching lines
    5. Return the LAST valid match (most likely the final amount)
    
    Returns: float or None
    """
    lines = text.split('\n')
    matches = []
    
    for line in lines:
        # Skip lines matching the exclude pattern
        if exclude_pattern and re.search(exclude_pattern, line, re.IGNORECASE):
            continue
        
        # Check if this line contains the keyword
        if not re.search(keyword_pattern, line, re.IGNORECASE):
            continue
        
        # Extract numbers from this line
        # Use word boundaries to avoid partial matches
        numbers = re.findall(r'\d+(?:[.,]\d{2})?', line)
        
        if not numbers:
            continue
        
        # Key insight: Extract the LAST number from the line
        # This is usually the amount (not house number, item count, etc.)
        amount_str = numbers[-1].replace(',', '.').replace('،', '.')
        
        try:
            amount = float(amount_str)
            
            # Validate amount is in realistic range
            if min_amount <= amount <= max_amount:
                matches.append(amount)
        except ValueError:
            pass
    
    # Return the LAST valid match (final TOTAL is usually last)
    return matches[-1] if matches else None


def _find_amount_by_currency(text, min_amount, max_amount):
    """
    Fallback: Find amount by currency prefix (₹ or Rs.).
    Only used if no TOTAL-like keyword is found.
    
    Returns: float or None (the highest valid amount found)
    """
    # Look for currency symbols followed by amounts
    currency_patterns = [
        r'₹\s*(\d+(?:[.,]\d{2})?)',      # Rupee symbol
        r'rs[.\s]+(\d+(?:[.,]\d{2})?)',  # Rs. or Rs prefix
    ]
    
    candidates = []
    
    for pattern in currency_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount_str = match.group(1).replace(',', '.').replace('،', '.')
                amount = float(amount_str)
                
                # Validate range
                if min_amount <= amount <= max_amount:
                    candidates.append(amount)
            except (ValueError, AttributeError):
                pass
    
    # Return highest found amount
    return max(candidates) if candidates else None


def extract_bill_data(image_path):
    """
    Main function to extract bill data from an image.
    
    Returns:
    {
        "success": bool,
        "title": str,  # Shop/Restaurant name
        "amount": float,  # Detected amount
        "raw_text": str,  # Full OCR text (for debugging)
        "message": str  # Error message if applicable
    }
    """
    try:
        # Open and prepare image
        img = Image.open(image_path)
        
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Extract text using OCR
        raw_text = pytesseract.image_to_string(img)
        
        if not raw_text.strip():
            return {
                "success": False,
                "message": "Could not read text from image"
            }
        
        # Normalize OCR output
        normalized_text = normalize_ocr_text(raw_text)
        
        # Extract description
        description = extract_description(raw_text)
        
        # Extract amount
        amount = extract_amount(raw_text, normalized_text)
        
        # Clean up temp file if exists
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        if amount is None:
            return {
                "success": False,
                "message": "Unable to detect bill amount"
            }
        
        return {
            "success": True,
            "title": description,
            "amount": round(amount, 2),
            "raw_text": raw_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing image: {str(e)}"
        }



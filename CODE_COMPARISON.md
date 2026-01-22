# Code Comparison: Before vs After

## File 1: expenses/ai_utils.py

### BEFORE (Old Logic)
```python
import pytesseract
from PIL import Image
import re

# Simple regex patterns - often fails on:
# - OCR typos (tota1, t0tal)
# - Broken digits (1 9 2 1)
# - Multiple prices (picks any, not always the TOTAL)

def extract_bill_data(image_path):
    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    text = pytesseract.image_to_string(img)
    clean_text = re.sub(r"\s+", " ", text)
    
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0] if lines else "Expense"
    
    amounts = []
    patterns = [
        r"(?:grand total|food total|total)\s*[:\-]?\s*₹?\s*(\d+(?:\.\d{1,2})?)",
        r"₹\s*(\d+(?:\.\d{1,2})?)",
        r"rs\.?\s*(\d+(?:\.\d{1,2})?)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            try:
                amounts.append(float(match))
            except ValueError:
                pass
    
    amount = max(amounts) if amounts else None  # ❌ Can be None, can be scientific notation
    
    return {
        "raw_text": clean_text,
        "title": title,
        "amount": amount  # ❌ No range validation
    }
```

### AFTER (New Logic)
```python
import pytesseract
from PIL import Image
import re
import os

# ✅ Modular functions with clear responsibilities
# ✅ Handles OCR errors
# ✅ 4-tier fallback strategy
# ✅ Range validation (₹10–₹100,000)

def normalize_ocr_text(text):
    """Fix OCR mistakes: tota1→total, 1 9 2 1→1921"""
    normalized = text.lower()
    
    # Common OCR mistakes for keywords
    normalized = re.sub(r"t[0o]tal", "total", normalized)
    normalized = re.sub(r"tota[l1]", "total", normalized)
    normalized = re.sub(r"to[a1]al", "total", normalized)
    
    # Rejoin broken numbers
    normalized = re.sub(r"(\d)\s+(\d)", r"\1\2", normalized)
    
    return normalized

def extract_description(text):
    """Extract shop name from bill header"""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return "Expense"
    
    title = lines[0]
    title = re.sub(r"\d{10,}", "", title)  # Remove phone numbers
    title = re.sub(r"[^\w\s\-&]", "", title)  # Clean symbols
    title = title.strip()[:100]  # Limit length
    
    return title if title and len(title) > 2 else "Expense"

def extract_amount(text, normalized_text):
    """
    4-tier smart extraction with realistic validation
    Tier 1: TOTAL keywords (highest priority)
    Tier 2: ₹/Rs. prefixed amounts
    Tier 3: Largest 3+ digit numbers
    Tier 4: Any amount in range ₹10–₹100,000
    """
    MIN_AMOUNT = 10.0
    MAX_AMOUNT = 100000.0
    
    candidates = []
    
    # Tier 1: Keyword matching
    total_patterns = [
        r"(?:grand\s*total|food\s*total|bill\s*total|payable|net\s*total)\s*[:\-=]?\s*(?:₹|rs[.\s]?)?\s*(\d+(?:[.,]\d{2})?)",
        r"(?<![\w])\btotal\b\s*[:\-=]?\s*(?:₹|rs[.\s]?)?\s*(\d+(?:[.,]\d{2})?)",
    ]
    
    for pattern in total_patterns:
        matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
        for match in matches:
            try:
                amount_str = match.group(1).replace(",", ".").replace("،", ".")
                amount = float(amount_str)
                
                if MIN_AMOUNT <= amount <= MAX_AMOUNT:
                    candidates.append(amount)
            except (ValueError, AttributeError):
                pass
    
    if candidates:
        return max(candidates)
    
    # Tier 2: Currency prefix
    currency_patterns = [
        r"₹\s*(\d+(?:[.,]\d{2})?)",
        r"rs[.\s]+(\d+(?:[.,]\d{2})?)",
    ]
    
    currency_candidates = []
    for pattern in currency_patterns:
        matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
        for match in matches:
            try:
                amount_str = match.group(1).replace(",", ".").replace("،", ".")
                amount = float(amount_str)
                
                if MIN_AMOUNT <= amount <= MAX_AMOUNT:
                    currency_candidates.append(amount)
            except (ValueError, AttributeError):
                pass
    
    if currency_candidates:
        return max(currency_candidates)
    
    # Tier 3: Largest 3+ digit numbers
    all_numbers = re.findall(r"\d+(?:[.,]\d{2})?", normalized_text)
    valid_amounts = []
    for num_str in all_numbers:
        try:
            amount = float(num_str.replace(",", ".").replace("،", "."))
            if amount >= 100 and amount <= MAX_AMOUNT:
                valid_amounts.append(amount)
        except ValueError:
            pass
    
    if valid_amounts:
        return max(valid_amounts)
    
    # Tier 4: Lenient fallback
    lenient_amounts = []
    for num_str in all_numbers:
        try:
            amount = float(num_str.replace(",", ".").replace("،", "."))
            if MIN_AMOUNT <= amount <= MAX_AMOUNT:
                lenient_amounts.append(amount)
        except ValueError:
            pass
    
    return max(lenient_amounts) if lenient_amounts else None

def extract_bill_data(image_path):
    """Main entry point"""
    try:
        img = Image.open(image_path)
        
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        raw_text = pytesseract.image_to_string(img)
        
        if not raw_text.strip():
            return {
                "success": False,
                "message": "Could not read text from image"
            }
        
        normalized_text = normalize_ocr_text(raw_text)
        description = extract_description(raw_text)
        amount = extract_amount(raw_text, normalized_text)
        
        # Clean up temp file
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
            "amount": round(amount, 2),  # ✅ Always numeric, never scientific
            "raw_text": raw_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing image: {str(e)}"
        }
```

**Key Differences:**
| Aspect | Before | After |
|--------|--------|-------|
| Functions | 1 large function | 4 focused functions |
| OCR errors | Not handled | Automatically fixed |
| Amount detection | Basic regex | 4-tier strategy |
| Range validation | None | ₹10–₹100,000 |
| Error handling | Generic | Specific messages |
| Response | May be None | Always success/failure |
| Return type | Unstructured dict | Consistent structure |

---

## File 2: expenses/views.py

### BEFORE (Old scan_bill)
```python
@login_required
def scan_bill(request):
    if request.method == "POST" and request.FILES.get("bill"):
        bill = request.FILES["bill"]

        temp_path = f"media/temp/{bill.name}"  # ❌ No directory check
        with open(temp_path, "wb+") as f:      # ❌ May fail if dir doesn't exist
            for chunk in bill.chunks():
                f.write(chunk)

        data = extract_bill_data(temp_path)

        if not data["amount"]:  # ❌ Could fail if amount is 0
            return JsonResponse({
                "success": False,
                "message": "Unable to detect amount"
            })

        return JsonResponse({
            "success": True,
            "amount": data["amount"],    # ❌ Could be string or None
            "description": data["title"]
        })

    return JsonResponse({"success": False})  # ❌ No error message
```

### AFTER (New scan_bill)
```python
@login_required
def scan_bill(request):
    """
    AJAX endpoint for bill image scanning and OCR extraction.
    
    Expects: POST request with "bill" file field
    Returns: JSON with success status, extracted amount & description
    """
    if request.method != "POST":  # ✅ Explicit method check
        return JsonResponse({
            "success": False,
            "message": "Only POST requests allowed"
        })
    
    if not request.FILES.get("bill"):  # ✅ File validation
        return JsonResponse({
            "success": False,
            "message": "No bill image provided"
        })
    
    try:
        bill = request.FILES["bill"]
        
        # ✅ Safe directory creation
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # ✅ UUID prevents filename collisions
        import uuid
        temp_filename = f"{uuid.uuid4()}_{bill.name}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # ✅ Safe file writing
        with open(temp_path, "wb+") as f:
            for chunk in bill.chunks():
                f.write(chunk)
        
        # Extract bill data
        result = extract_bill_data(temp_path)
        
        # ✅ Cleanup (extra safety check)
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        # ✅ Check success flag, not amount value
        if not result["success"]:
            return JsonResponse({
                "success": False,
                "message": result.get("message", "Failed to extract bill data")
            })
        
        # ✅ Return clean, consistent response
        return JsonResponse({
            "success": True,
            "amount": result["amount"],      # ✅ Numeric, validated
            "description": result["title"]
        })
        
    except Exception as e:  # ✅ Comprehensive error handling
        return JsonResponse({
            "success": False,
            "message": f"Error processing bill: {str(e)}"
        })
```

**Key Differences:**
| Aspect | Before | After |
|--------|--------|-------|
| Method validation | Simple | Explicit |
| Directory handling | Assumes exists | Creates if needed |
| Filename safety | Uses original name | UUID prefix |
| Error handling | Minimal | Comprehensive |
| Response messages | Generic | Specific |
| Cleanup | No | Guaranteed |
| Exception handling | None | Full try-except |

---

## File 3: expense_form.html JavaScript

### BEFORE (Old bill upload handler)
```javascript
const billInput = document.getElementById("billImage");

if (billInput) {
    billInput.addEventListener("change", function () {

        if (!this.files.length) return;

        const formData = new FormData();
        formData.append("bill_image", this.files[0]);  // ❌ Wrong field name

        msgBox.innerHTML = `<span class="text-info">Scanning bill…</span>`;
        saveBtn.disabled = true;

        fetch("{% url 'expenses:scan_bill' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {

            if (data.amount) {  // ❌ Loose check
                amountInput.value = data.amount;  // ❌ Could be string or scientific notation
            }

            if (data.description) {
                descInput.value = data.description;
            }

            msgBox.innerHTML =
                `<span class="text-success">
                    Bill scanned. Please verify details.
                </span>`;

            saveBtn.disabled = false;

            // ❌ No re-validation of splits
            if (splitType() === "custom") validateCustom();
            if (splitType() === "percentage") validatePercentage();
        })
        .catch(() => {  // ❌ Silent error
            msgBox.innerHTML =
                `<span class="text-danger">Failed to scan bill</span>`;
            saveBtn.disabled = false;
        });
    });
}
```

### AFTER (New bill upload handler)
```javascript
/* ================= AI BILL SCAN ================= */

const billInput = document.getElementById("billImage");

if (billInput) {
    billInput.addEventListener("change", function () {

        if (!this.files.length) return;

        const formData = new FormData();
        formData.append("bill", this.files[0]);  // ✅ Correct field name

        msgBox.innerHTML =
            `<span class="text-info">🔄 Scanning bill…</span>`;  // ✅ Visual feedback
        saveBtn.disabled = true;

        fetch("{% url 'expenses:scan_bill' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {  // ✅ Strict success check

                // ✅ SAFETY: Ensure numeric value, never scientific notation
                if (data.amount !== null && data.amount !== undefined) {
                    const numAmount = Number(data.amount);
                    
                    // ✅ Validate range: ₹10 - ₹100,000
                    if (numAmount >= 10 && numAmount <= 100000 && isFinite(numAmount)) {
                        amountInput.value = numAmount.toFixed(2);  // ✅ Safe format
                    } else {
                        throw new Error("Amount out of realistic range");
                    }
                }

                if (data.description && data.description.trim()) {  // ✅ Trim whitespace
                    descInput.value = data.description.trim();
                }

                msgBox.innerHTML =
                    `<span class="text-success">
                        ✅ Bill scanned successfully. Please verify details.
                    </span>`;  // ✅ Better feedback

                // ✅ Always re-validate splits
                if (splitType() === "custom") validateCustom();
                if (splitType() === "percentage") validatePercentage();

            } else {
                msgBox.innerHTML =
                    `<span class="text-danger">
                        ❌ ${data.message || "Failed to scan bill"}  <!-- ✅ Show error message -->
                    </span>`;
            }

            saveBtn.disabled = false;
        })
        .catch(err => {  // ✅ Proper error logging
            console.error("Bill scan error:", err);  // ✅ Debug info
            msgBox.innerHTML =
                `<span class="text-danger">❌ Failed to scan bill</span>`;
            saveBtn.disabled = false;
        });
    });
}
```

**Key Differences:**
| Aspect | Before | After |
|--------|--------|-------|
| Field name | "bill_image" | "bill" ✓ |
| Success check | Loose (data.amount) | Strict (data.success) |
| Amount handling | Direct assignment | Validation + formatting |
| Scientific notation | Not prevented | Prevented |
| Range validation | None | ₹10–₹100,000 |
| User feedback | Generic | Emojis + specific |
| Error messages | Generic | From backend |
| Split validation | Maybe | Always |
| Error logging | Silent | To console |

---

## Summary Table

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| **ai_utils.py** | 1 function | 4 functions | Modular, maintainable |
| **OCR errors** | Not handled | Auto-fixed | Handles real-world images |
| **Amount detection** | Basic regex | 4-tier strategy | Much more reliable |
| **Range validation** | None | ₹10–₹100,000 | Prevents unrealistic values |
| **Scientific notation** | Possible | Prevented | Safe for all inputs |
| **views.py** | Basic | Production-ready | Safe, robust |
| **Error messages** | Generic | Specific | Better debugging |
| **Frontend safety** | Loose | Strict | No scientific notation |
| **UX feedback** | Minimal | Rich | Emojis, clear messages |
| **Documentation** | None | Comprehensive | Easy to maintain |


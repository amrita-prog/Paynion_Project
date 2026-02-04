# PAYNION - Screens & Components Guide (Detailed)

**Project**: Expense Splitting & Settlement Application | **Framework**: Django + Bootstrap 5 | **Target**: <500 Lines

---

## 📱 ACCOUNT MODULE (6 Screens)

### 1. LOGIN
**Route**: `/accounts/login/` | **Auth**: Email/Password
- **Components**: Email input, Password field, Login button, Signup link, Error/Success messages
- **Functionality**: User authentication, "Next" parameter redirect support, Form validation
- **UX**: Centered form, Remember me option (optional), Forgot password link

### 2. SIGNUP
**Route**: `/accounts/signup/` | **New User Registration**
- **Components**: Full name, Email, Password, Confirm password, Profile image upload, Form validation
- **Functionality**: Unique email validation, File upload with preview, Auto-redirect after signup
- **UX**: Progress indicator (optional), Password strength meter, Image preview

### 3. DASHBOARD (Main Hub)
**Route**: `/accounts/dashboard/` | **Core Entry Point**
- **Components**:
  - Welcome greeting header with user name
  - 4 Summary cards: Groups count, Expenses count, Balance amount, Quick actions buttons
  - Time range filter (This Week, Last Week, All Time dropdown)
  - 3 Line charts: "Paid by me", "Need to pay", "Will get back"
  - Recent expenses list (last 5 with group name, amount, date)
  - Pending group invitation alert (if exists)
- **Functionality**: Real-time data aggregation, Multi-time period analytics, Quick navigation CTAs
- **Charts**: Chart.js with date labels, legends, grid lines

### 4. PROFILE
**Route**: `/accounts/profile/` | **View Only**
- **Components**: Circular profile picture, User info display (name, email, phone, bio, UPI), Edit button
- **Functionality**: Display all user details, Link to edit page
- **UX**: Clean layout, Copy-able fields, Account age display

### 5. EDIT PROFILE
**Route**: `/accounts/edit-profile/` | **Update Details**
- **Components**: Image upload (with current preview), Full name input, Phone input, Bio textarea, UPI ID input
- **Functionality**: File upload with validation, Form submission, Success message
- **Validation**: Email unique check, Phone format, UPI format validation

### 6. ANALYTICS/REPORT
**Route**: `/accounts/report/` | **Monthly Analytics**
- **Components**: Month/Year dropdown filters, Summary stats box (4 metrics), Bar chart, Expense table
- **Functionality**: Monthly breakdown, PDF export, Filtering, Pagination
- **Table Columns**: Date, Description, Amount, Group name, Actions
- **Export**: PDF with signature space, Logo, Monthly summary

---

## 👥 GROUPS MODULE (5 Screens)

### 1. ALL GROUPS
**Route**: `/groups/all-groups/` | **Group Listing**
- **Components**: Create new group button, Search/filter input, Group cards in grid (2-3 columns per row)
- **Card Details**: Group name (title), Description (truncated), Member count with icon, View button
- **Functionality**: Create new group, Search groups, Filter by creation date, Pagination
- **Empty State**: "No groups yet" message with create button

### 2. CREATE GROUP
**Route**: `/groups/create/` | **New Group**
- **Components**: Group name input (required), Description textarea, Member email input with add button, Members list with remove option
- **Functionality**: Add/Remove members before creation, Form validation, Redirect to group detail
- **Validation**: Group name required, Email format check, Duplicate member prevention

### 3. GROUP DETAIL (⭐ CORE SCREEN)
**Route**: `/groups/<id>/` | **Everything about Group**

**Header Section**:
- Group name (h2), Description, Edit/Delete buttons (if creator)

**Members Section**:
- Member count badge, Add member form (if creator): email input + button
- Members list: Avatar/Icon, Name, Remove button (if creator)

**Balances Section**:
- "Will Receive" amounts (green, +₹X)
- "Needs to Pay" amounts (red, -₹X)
- "No Dues" (gray, ₹0)
- Settlement button for each user

**Settlements Section**:
- Settlement cards showing:
  - From user → To user (clear direction)
  - Amount (bold, ₹X.XX)
  - Status badge (PENDING, PAID_REQUESTED, SETTLED)
  - Action buttons: [MARK AS PAID], [PAY VIA UPI], [ACCEPT], [REJECT]
  - Payment mode display if paid

**Expenses Section**:
- [+ ADD EXPENSE] button (CTA)
- Expense cards with:
  - Description, Payer name, Amount, Date
  - Split type label (Equal/Percentage/Custom)
  - Split breakdown per member (who owes what)
  - Edit/Delete buttons
- Sort by date descending

### 4. EDIT GROUP
**Route**: `/groups/<id>/edit/` | **Edit Details**
- **Components**: Group name input (pre-filled), Description textarea (pre-filled), Save/Cancel buttons
- **Permissions**: Creator only
- **Functionality**: Update group info, Validation, Success message

### 5. ACCEPT INVITE
**Route**: `/groups/invite/accept/<token>/` | **Invitation Link**
- **Components**: Invitation header, Group name/description, Invited by user info, Member count
- **Buttons**: Accept (primary), Decline (secondary)
- **Functionality**: Auto-join on accept, Token validation, Email sender name display

---

## 💰 EXPENSES MODULE (2 Screens)

### 1. ADD EXPENSE
**Route**: `/expenses/add/<group-id>/` | **Create Expense with Bill Scanning**

**Header**: "ADD EXPENSE - Group Name" | "Expense will be added to this group"

**Bill Scanning Section** (AI OCR):
- File upload input (drag & drop enabled)
- Loading spinner during processing
- Auto-fill result: Amount + Description extracted from bill image
- Error handling for invalid bills

**Expense Form**:
- Amount input (currency formatted, ₹)
- Description textarea (required)
- Split type selection (radio buttons):
  - Equal (auto-calculated, ₹X per person)
  - Percentage (custom % per member, shows calculated amount)
  - Custom (explicit amount per member, validation of total)

**Member Selection**:
- Checkboxes for each group member
- At least one member required (excluding payer)

**Dynamic Split Display** (changes based on selection):
- **Equal**: Shows "Each person pays: ₹X"
- **Percentage**: Shows percentage input + calculated amount for each member, Total validation (100%)
- **Custom**: Shows amount input per member, Total validation (matches expense amount)

**Validation Message**: Shows real-time errors (red) or success (green)
**Submit**: [ADD EXPENSE] primary button, [CANCEL] secondary button

### 2. EDIT EXPENSE
**Route**: `/expenses/edit/<id>/` | **Modify Expense**
- **Same as Add Expense** but:
  - Pre-filled form values
  - Title: "EDIT EXPENSE"
  - Button: [UPDATE EXPENSE] instead of Add
  - Can change split members and amounts

---

## 💳 PAYMENTS MODULE (3 Screens)

### 1. UPI PAYMENT
**Route**: `/payments/upi-pay/` | **Payment Gateway**
- **Components**:
  - Receiver name (bold), Amount (large, ₹X.XX)
  - UPI Link display (copiable)
  - QR code image (centered, scannable)
  - [COPY UPI LINK] button
  - [OPEN IN UPI APP] button (mobile-aware)
  - Instructions for payment
  - Payment status tracker

### 2. MARK AS PAID / ACCEPT PAYMENT
**Settlement Flow**:
- **Mark as Paid** (Payer action):
  - Payment mode selection: Cash / UPI (radio)
  - [MARK AS PAID] button → Status changes to "PAID_REQUESTED"
  
- **Accept Payment** (Receiver action):
  - Shows "Waiting for your confirmation..."
  - Display payment mode used
  - [ACCEPT PAYMENT] button → Status changes to "SETTLED"
  - [REJECT] button → Returns to "PENDING"

### 3. PAYMENT HISTORY
**Route**: `/payments/history/` | **All Transactions**
- **Filters**: Group dropdown, Status dropdown, Date range picker
- **Transaction Table**:
  - Columns: Date, From (payer), To (receiver), Amount, Mode (UPI/Cash), Status badge
  - Sortable: By date, amount
  - Pagination: 20 items per page
- **Summary**: Total paid, Total pending (above/below table)
- **Export**: [EXPORT TO CSV], [PRINT] buttons

---

## 🎨 GLOBAL COMPONENTS

**Navbar** (Sticky):
- Logo + Paynion text, Nav links (Dashboard, Groups, Analytics, History, Settings)
- Notification bell with unread badge (if count > 0)
- Profile dropdown (My Profile, Edit Profile, Logout)
- Dark bg (#1a1a1a), Cyan accent (#00d4ff)

**Buttons**:
- Primary (green/cyan): Save, Submit, Create, Pay
- Secondary (gray): Cancel, Back, Reset
- Danger (red): Delete, Remove, Decline
- Small action: [+ ADD], [SCAN], [EDIT], [DELETE]

**Form Inputs** (10 types): Text, Email, Number, Textarea, Select, Checkbox, Radio, File upload, Date picker, Percentage

**Status Badges**:
- PENDING: Gray/Orange bg
- PAID: Green bg
- SETTLED: Green bg
- PAID_REQUESTED: Blue bg
- ERROR: Red bg

**Cards**: Semi-transparent white, Glassmorphism effect, Border 12-20px, Soft shadows, 0.3s ease transitions

**Alerts**: Success (green ✓), Error (red ✗), Warning (yellow ⚠), Info (blue ℹ) - all dismissible

**Modals**: Delete confirmation, Dialogs for important actions

---

## 🎨 COLOR & STYLING

| Element | Color | Usage |
|---------|-------|-------|
| Background | #f5f1e8 (Cream) | With grid pattern |
| Navbar | #1a1a1a (Dark) | Sticky header |
| Primary | #00d4ff (Cyan) | Links, active states |
| Success | #28a745 (Green) | Confirmations, positive |
| Danger | #dc3545 (Red) | Delete, destructive |
| Warning | #ffc107 (Yellow) | Warnings, alerts |
| Info | #0d6efd (Blue) | Information |

**Typography**: Bootstrap default | **Transitions**: 0.3s ease | **Border-radius**: 6px (input), 12px (btn), 20px (cards)

---

## ✨ KEY FEATURES

✅ Bill OCR Scanning with AI extraction  
✅ Real-time expense splitting (Equal/Percentage/Custom)  
✅ Automatic settlement calculation  
✅ UPI payment integration with QR code  
✅ Detailed expense analytics & reports  
✅ Email group invitations  
✅ Multi-time period dashboard charts  
✅ PDF report export  
✅ Payment history tracking  
✅ Role-based actions (creator vs member)

---

## 📊 QUICK SUMMARY

| Category | Count | Details |
|----------|-------|---------|
| **Screens** | 14 | 6 Accounts + 5 Groups + 2 Expenses + 3 Payments |
| **Form Types** | 10 | Input, Email, Number, Textarea, Select, Checkbox, Radio, File, Date, Percentage |
| **Button Types** | 5 | Primary, Secondary, Danger, Success, Small action |
| **Components** | 25+ | Navbar, Cards, Alerts, Badges, Modals, Charts, Tables |
| **Status Types** | 6 | Pending, Paid, Settled, Paid_Requested, Error, Warning |

---

**Document Version**: 1.5 | **Lines**: ~450 | **Updated**: Feb 4, 2026 | **For**: UI/UX Designer

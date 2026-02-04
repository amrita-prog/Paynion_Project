# PAYNION - Screens & Components Guide (Quick)

**Project**: Expense Splitting & Settlement Application | **Framework**: Django + Bootstrap 5

---

## ACCOUNT MODULE (6 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **Login** | `/accounts/login/` | Email/password authentication | Email input, Password input, Submit button, Signup link |
| **Signup** | `/accounts/signup/` | User registration with profile pic | Full name, Email, Password, Confirm password, Image upload, Signup button |
| **Dashboard** | `/accounts/dashboard/` | Main hub - stats, charts, recent expenses | Welcome header, 4 summary cards, Time range selector, 3 line charts, Recent expenses list |
| **Profile** | `/accounts/profile/` | View user info | Profile picture, Full name, Email, Phone, Bio, UPI ID, Edit button |
| **Edit Profile** | `/accounts/edit-profile/` | Update user details | Image upload, Full name input, Phone input, Bio textarea, UPI ID input, Save button |
| **Analytics** | `/accounts/report/` | Monthly expense analytics | Month/Year filters, Summary stats box, Bar chart, Expense table, PDF export |

---

## GROUPS MODULE (5 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **All Groups** | `/groups/all-groups/` | List user's groups | Create button, Search field, Group cards (name, desc, member count, view button) |
| **Create Group** | `/groups/create/` | Create new group | Group name input, Description textarea, Member email input, Members list, Create button |
| **Group Detail** | `/groups/<id>/` | Core screen - members, expenses, balances, settlements | Group header, Add member form, Members list, Balances section, Settlement cards, Expenses list with split details, Add expense button |
| **Edit Group** | `/groups/<id>/edit/` | Edit group details | Group name input (pre-filled), Description textarea (pre-filled), Save button |
| **Accept Invite** | `/groups/invite/accept/<token>/` | Accept group invitation | Invitation header, Group details, Invited by info, Accept/Decline buttons |

---

## EXPENSES MODULE (2 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **Add Expense** | `/expenses/add/<group-id>/` | Create expense with bill scanning | Bill image upload, Amount input, Description textarea, Split type radio buttons (Equal/Percentage/Custom), Member checkboxes, Dynamic split section, Submit button |
| **Edit Expense** | `/expenses/edit/<id>/` | Edit expense details | Same as Add Expense but pre-filled, Update button instead of Add |

---

## PAYMENTS MODULE (3 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **UPI Payment** | `/payments/upi-pay/` | Generate UPI link & QR code | Receiver name, Amount display, QR code image, Copy link button, Open in UPI app button |
| **Mark as Paid** | Settlement action | Confirm payment sent | Settlement card, Payment mode radio (Cash/UPI), Mark as paid button |
| **Payment History** | `/payments/history/` | View all transactions | Filter dropdowns (Group, Status, Date), Transaction table (Date, From, To, Amount, Mode, Status), Export/Print buttons |

---

## GLOBAL COMPONENTS

### Navbar
- Logo + Brand name, Navigation links (Dashboard, Groups, Analytics, History, Settings)
- Notification bell (with badge count), Profile dropdown (My Profile, Edit Profile, Logout)
- Dark background (#1a1a1a), Cyan accent (#00d4ff), Sticky positioning

### Message Alerts
- Success/Error/Warning/Info messages with dismiss button

### Forms
- Input types: Text, Email, Number, Textarea, Select, Checkbox, Radio, File upload, Date picker
- Features: Required field asterisk, Placeholder text, Help text, Error messages, Validation feedback

### Buttons
- Primary (Save, Submit, Create), Secondary (Cancel, Back), Danger (Delete, Remove), Success (Confirm, Accept)
- Small action buttons: [+ ADD], [SCAN], [EDIT], [DELETE]

### Status Badges
- PENDING (gray), PAID/SETTLED (green), PAID_REQUESTED (blue), ERROR (red), WARNING (yellow)

### Cards
- Semi-transparent white with glassmorphism, Border-radius 12px-20px, Soft shadows, 0.3s ease transitions

### Other
- Modal/Confirm dialogs, Empty states with CTA, Loading spinners/skeleton loaders, Modals for confirmations

---

## STYLING GUIDE

**Background**: Cream (#f5f1e8) with subtle grid pattern  
**Primary Color**: Cyan (#00d4ff)  
**Success**: Green (#28a745) | **Danger**: Red (#dc3545) | **Warning**: Yellow (#ffc107)  
**Dark**: #1a1a1a | **Light**: #f5f1e8  
**Font**: Bootstrap default (Segoe UI, system fonts)

---

## QUICK SUMMARY

✅ **14 Screens** | ✅ **Responsive Design** | ✅ **Glassmorphism Cards** | ✅ **Dark Navbar**  
✅ **Charts & Analytics** | ✅ **Bill OCR Scanning** | ✅ **UPI Integration** | ✅ **Real-time Settlements**

**Total Components**: Inputs (10 types), Buttons (5 types), Cards, Badges, Alerts, Modals, Navbar  
**Color Scheme**: Dark + Cyan accent + Cream background with grid pattern

---

## GROUPS MODULE

### 1. ALL GROUPS SCREEN
**Route**: `/groups/all-groups/`

**Functionality**:
- Display all groups user is member of
- Quick navigation to group details
- Show member count for each group
- Option to create new group
- Search/Filter functionality

**Components**:
```
┌──────────────────────────────────────────────────┐
│ MY GROUPS                                        │
├──────────────────────────────────────────────────┤
│                                                  │
│ [+ CREATE NEW GROUP]                            │
│                                                  │
│ Search: [________________] [Search Button]      │
│                                                  │
├──────────────────────────────────────────────────┤
│ GROUP CARDS (Grid/List Layout)                  │
│                                                  │
│ ┌────────────────────┐  ┌────────────────────┐ │
│ │ Group Name 1       │  │ Group Name 2       │ │
│ │                    │  │                    │ │
│ │ Description...     │  │ Description...     │ │
│ │                    │  │                    │ │
│ │ 👥 5 Members       │  │ 👥 3 Members       │ │
│ │ [VIEW GROUP]       │  │ [VIEW GROUP]       │ │
│ └────────────────────┘  └────────────────────┘ │
│                                                  │
│ ┌────────────────────┐  ┌────────────────────┐ │
│ │ Group Name 3       │  │ Group Name 4       │ │
│ │ ...                │  │ ...                │ │
│ └────────────────────┘  └────────────────────┘ │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Components Detail**:
- Create new group button (CTA)
- Search/filter input field
- Group cards in grid layout (2-3 columns)
  - Group name (title)
  - Group description (truncated)
  - Member count with icon
  - "View Group" button
  - Edit/Delete options (if creator)
- Empty state message (if no groups)
- Pagination (if many groups)

---

### 2. CREATE GROUP SCREEN
**Route**: `/groups/create/`

**Functionality**:
- Create new expense splitting group
- Set group name and description
- Add initial members (optional)
- Form validation
- Redirect to group detail after creation

**Components**:
```
┌──────────────────────────────────────────┐
│ CREATE NEW GROUP                         │
├──────────────────────────────────────────┤
│                                          │
│ Group Name *                            │
│ [________________]                      │
│                                          │
│ Description                             │
│ [_____________________________]          │
│ (Optional - describe group purpose)    │
│                                          │
│ Add Members (Optional)                  │
│ [________________] [+ Add]               │
│ ✓ Member 1                              │
│ ✓ Member 2                              │
│ ✗ Remove                                │
│                                          │
│ [CREATE GROUP] [CANCEL]                 │
│                                          │
└──────────────────────────────────────────┘
```

**Components Detail**:
- Group name input field (required)
- Description textarea (optional)
- Member email input with add button
- List of added members with remove option
- Create button (primary action)
- Cancel button (secondary action)
- Error/validation messages
- Success message on creation

---

### 3. GROUP DETAIL SCREEN
**Route**: `/groups/<group-id>/`

**Functionality**:
- Core screen showing all group information
- Display group name, description, members
- Show all expenses in the group with split details
- Display settlement balances (who owes whom)
- Show pending settlements/payments
- Option to add/remove members
- Invite new members via email
- Edit/Delete group (if creator)
- Quick add expense button

**Components**:

#### Header Section:
```
┌──────────────────────────────────────────────────────┐
│ GROUP TITLE                                          │
│ Group Description...                                │
│                             [EDIT] [DELETE]         │
└──────────────────────────────────────────────────────┘
```

#### Member Management Section:
```
┌──────────────────────────────────────────────────────┐
│ MEMBERS (Count: X)                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Add Member (if creator):                            │
│ [user@email.com] [+ ADD]                            │
│                                                      │
│ Current Members:                                    │
│ ┌────────────────────────────────────────────────┐ │
│ │ 👤 Member Name 1              [Remove]         │ │
│ │ 👤 Member Name 2              [Remove]         │ │
│ │ 👤 Member Name 3              [Remove]         │ │
│ └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### Balances Section:
```
┌──────────────────────────────────────────────────────┐
│ BALANCES                                             │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ┌────────────────────────────────────────────────┐ │
│ │ User A  ────→  Will Receive: ₹1500            │ │
│ │ User B  ←────  Needs to Pay: ₹2300            │ │
│ │ User C  ────→  Will Receive: ₹800             │ │
│ │ User D         No Dues                         │ │
│ └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### Settlements Section:
```
┌──────────────────────────────────────────────────────┐
│ SETTLEMENTS (Pending)                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │ User A  →  User B                               ││
│ │ Amount: ₹500                                     ││
│ │ Status: PENDING                                  ││
│ │            [MARK AS PAID]  [PAY VIA UPI]        ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │ User C  →  User A                               ││
│ │ Amount: ₹300                                     ││
│ │ Status: PAID_REQUESTED (waiting acceptance)     ││
│ │            [ACCEPT] [REJECT]                    ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### Expenses Section:
```
┌──────────────────────────────────────────────────────┐
│ [+ ADD EXPENSE]                                      │
│                                                      │
│ EXPENSES (Total: X)                                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │ Restaurant Bill                                  ││
│ │ Paid By: User A  |  Amount: ₹1200              ││
│ │ Date: Feb 01, 2026                             ││
│ │ Split: Equal among 4 members                   ││
│ │                             [EDIT]  [DELETE]   ││
│ │ Split Details:                                 ││
│ │  → User A (paid): ₹0                           ││
│ │  → User B (owes): ₹300                         ││
│ │  → User C (owes): ₹300                         ││
│ │  → User D (owes): ₹300                         ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │ [More Expenses...]                              ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Key Components**:
- Group header (name, description, edit/delete buttons)
- Invite member form section
- Members list with remove options
- Balance sheet (who owes whom and amounts)
- Settlement cards showing:
  - Payer name
  - Receiver name
  - Amount
  - Status badge (PENDING, PAID_REQUESTED, SETTLED)
  - Action buttons (Mark as Paid, Pay UPI, Accept, Reject)
- Expenses section with:
  - Expense cards showing description, payer, amount, date
  - Split details (who owes what)
  - Edit and delete buttons
- Add expense button (CTA)
- Alert for pending invitations

---

### 4. EDIT GROUP SCREEN
**Route**: `/groups/<group-id>/edit/`

**Functionality**:
- Allow group creator to edit group details
- Update group name and description
- Member management
- Form validation

**Components**:
```
┌──────────────────────────────────────────┐
│ EDIT GROUP                               │
├──────────────────────────────────────────┤
│                                          │
│ Group Name *                            │
│ [________________]                      │
│                                          │
│ Description                             │
│ [_____________________________]          │
│                                          │
│ [SAVE CHANGES] [CANCEL]                 │
│                                          │
└──────────────────────────────────────────┘
```

**Components Detail**:
- Group name input (pre-filled)
- Description textarea (pre-filled)
- Save button (primary action)
- Cancel button (secondary action)
- Validation errors

---

### 5. ACCEPT INVITE SCREEN
**Route**: `/groups/invite/accept/<token>/`

**Functionality**:
- Accept group invitation via token link
- Show group details before accepting
- Confirm acceptance
- Auto-join group after acceptance

**Components**:
```
┌──────────────────────────────────────────┐
│ GROUP INVITATION                         │
├──────────────────────────────────────────┤
│                                          │
│ You've been invited to join:            │
│                                          │
│ Group Name                              │
│ Description of the group...             │
│                                          │
│ Invited By: User Name                  │
│ Current Members: 5                      │
│                                          │
│ [ACCEPT INVITATION] [DECLINE]           │
│                                          │
└──────────────────────────────────────────┘
```

**Components Detail**:
- Invitation header
- Group name and description
- Invited by information
- Member count
- Accept button (primary action)
- Decline button (secondary action)

---

## EXPENSES MODULE

### 1. ADD EXPENSE SCREEN
**Route**: `/expenses/add/<group-id>/`

**Functionality**:
- Create new expense in a group
- Upload bill image for AI-powered OCR extraction
- Auto-fill amount and description from bill
- Choose split type (Equal, Percentage, Custom)
- Select which members to split with
- Form validation
- Redirect to group detail on success

**Components**:

#### Header:
```
┌──────────────────────────────────────────┐
│ ADD EXPENSE - Group Name                │
│ Expense will be added to this group      │
└──────────────────────────────────────────┘
```

#### Bill Upload Section:
```
┌──────────────────────────────────────────┐
│ BILL SCANNING (AI)                      │
├──────────────────────────────────────────┤
│                                          │
│ Upload Bill Image                       │
│ [Choose File]                           │
│ └─ Auto-fill Amount & Description       │
│                                          │
│ [📷 Drag & Drop or Click]               │
│                                          │
│ Processing... (if uploading)            │
│                                          │
└──────────────────────────────────────────┘
```

#### Expense Form Section:
```
┌──────────────────────────────────────────┐
│ EXPENSE DETAILS                         │
├──────────────────────────────────────────┤
│                                          │
│ Amount * (₹)                            │
│ [________________]                      │
│                                          │
│ Description *                           │
│ [_____________________________]          │
│                                          │
│ Split Type *                            │
│ ⦿ Equal Split                           │
│ ○ Percentage Split                      │
│ ○ Custom Amount Split                   │
│                                          │
└──────────────────────────────────────────┘
```

#### Members Selection:
```
┌──────────────────────────────────────────┐
│ SPLIT BETWEEN *                         │
├──────────────────────────────────────────┤
│                                          │
│ ☑ Member 1                              │
│ ☑ Member 2                              │
│ ☐ Member 3                              │
│ ☑ Member 4                              │
│                                          │
└──────────────────────────────────────────┘
```

#### Dynamic Split Section (shows based on selection):
```
[IF EQUAL SPLIT SELECTED]
┌──────────────────────────────────────────┐
│ EQUAL SPLIT (Auto-calculated)           │
├──────────────────────────────────────────┤
│ Each member pays: ₹300                  │
└──────────────────────────────────────────┘

[IF PERCENTAGE SPLIT SELECTED]
┌──────────────────────────────────────────┐
│ PERCENTAGE SPLIT                        │
├──────────────────────────────────────────┤
│ Member 1:  [___] % (₹_____)             │
│ Member 2:  [___] % (₹_____)             │
│ Member 3:  [___] % (₹_____)             │
│ Member 4:  [___] % (₹_____)             │
│                                          │
│ Total: 100% ✓                           │
└──────────────────────────────────────────┘

[IF CUSTOM AMOUNT SELECTED]
┌──────────────────────────────────────────┐
│ CUSTOM AMOUNT SPLIT                     │
├──────────────────────────────────────────┤
│ Member 1: [_____] (₹100)                │
│ Member 2: [_____] (₹150)                │
│ Member 3: [_____] (₹200)                │
│ Member 4: [_____] (₹350)                │
│                                          │
│ Total: ₹800 ✓                           │
└──────────────────────────────────────────┘
```

#### Submit Section:
```
┌──────────────────────────────────────────┐
│ Validation Message (if errors)          │
│                                          │
│ [ADD EXPENSE] [CANCEL]                  │
│                                          │
└──────────────────────────────────────────┘
```

**Key Components**:
- Bill image upload input (with drag & drop)
- Loading indicator during bill processing
- Amount input field (currency formatted)
- Description textarea
- Split type radio buttons
- Member checkboxes
- Dynamic split details section
  - Shows different layout based on split type
  - Percentage: percentage inputs + amount display
  - Custom: amount inputs per member
  - Equal: summary display
- Validation message area
- Submit button (primary action)
- Cancel button (secondary action)

---

### 2. EDIT EXPENSE SCREEN
**Route**: `/expenses/edit/<expense-id>/`

**Functionality**:
- Edit existing expense details
- Update amount, description, split type
- Modify split distribution
- Form validation
- Redirect to group detail on save

**Components**:
```
[Same as ADD EXPENSE SCREEN, but with:]
- Title: "EDIT EXPENSE"
- Pre-filled form values
- Save button instead of "Add Expense"
```

**Components Detail**:
- Same as Add Expense but pre-populated with existing data
- Submit button text: "UPDATE EXPENSE"

---

## PAYMENTS MODULE

### 1. UPI PAYMENT SCREEN
**Route**: `/payments/upi-pay/`

**Functionality**:
- Generate UPI payment link for settlement
- Display QR code for mobile scanning
- Copy UPI link option
- Status tracking for payment
- Redirect after payment confirmation

**Components**:
```
┌──────────────────────────────────────────┐
│ UPI PAYMENT                              │
├──────────────────────────────────────────┤
│                                          │
│ Pay To: Receiver Name                   │
│ Amount: ₹500                            │
│                                          │
│ Your UPI: upi://pay?pa=...              │
│                                          │
├──────────────────────────────────────────┤
│ SCAN QR CODE (Desktop Users)            │
│                                          │
│  ┌────────────────────┐                 │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │                 │
│  │  ▓      ▓  ▓      │                 │
│  │  ▓  ▓▓▓▓  ▓  ▓▓▓  │                 │
│  │  ▓  ▓  ▓  ▓  ▓    │                 │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │                 │
│  └────────────────────┘                 │
│                                          │
├──────────────────────────────────────────┤
│ [COPY UPI LINK]                         │
│                                          │
│ — OR —                                  │
│                                          │
│ [OPEN IN UPI APP]                       │
│                                          │
└──────────────────────────────────────────┘
```

**Components Detail**:
- Receiver name and UPI ID display
- Amount to pay (prominent)
- QR code image (large, centered)
- Copy UPI link button
- Open in UPI app button
- Payment status indicator
- Instructions for payment

---

### 2. SETTLEMENT PAYMENT FLOW

#### Mark as Paid:
```
┌──────────────────────────────────────────┐
│ Settlement Card                          │
├──────────────────────────────────────────┤
│ User A  →  User B                       │
│ Amount: ₹500                            │
│ Status: PENDING                         │
│                                          │
│ Payment Mode:                           │
│ ⦿ Cash                                  │
│ ○ UPI                                   │
│                                          │
│ [MARK AS PAID]                          │
│                                          │
└──────────────────────────────────────────┘
```

#### Accept Payment:
```
┌──────────────────────────────────────────┐
│ Settlement Card                          │
├──────────────────────────────────────────┤
│ User A  →  User B                       │
│ Amount: ₹500                            │
│ Status: PAID_REQUESTED                  │
│ Payment Mode: [Cash/UPI]                │
│                                          │
│ Waiting for your confirmation...        │
│                                          │
│ [ACCEPT PAYMENT] [REJECT]               │
│                                          │
└──────────────────────────────────────────┘
```

### 3. PAYMENT HISTORY SCREEN
**Route**: `/payments/history/`

**Functionality**:
- Display all payment transactions
- Show payment status (pending, paid, settled)
- Filter by group, date, status
- Display payment method used
- Download transaction report

**Components**:
```
┌──────────────────────────────────────────────────────┐
│ PAYMENT HISTORY                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Filters:                                            │
│ Group: [All Groups ▼]  Status: [All ▼]  Date: [▼]  │
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │ Payment Table                                     ││
│ ├──────────────────────────────────────────────────┤│
│ │ Date     │ From    │ To      │ Amount │ Mode │   ││
│ │----------|---------|---------|--------|------|   ││
│ │ Feb 01   │ User A  │ User B  │ ₹500   │ UPI  │   ││
│ │ Feb 02   │ User C  │ User D  │ ₹300   │CASH  │   ││
│ │ Feb 03   │ User A  │ User C  │ ₹200   │ UPI  │   ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ [EXPORT TO CSV] [PRINT]                            │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Components Detail**:
- Filter controls (Group, Status, Date dropdowns)
- Transaction table with columns:
  - Date
  - From (payer)
  - To (receiver)
  - Amount
  - Payment mode (UPI/Cash)
  - Status badge
  - Action buttons (View, Download receipt)
- Pagination
- Export/Print buttons
- Summary section (total paid, total pending)

---

## GLOBAL COMPONENTS

### 1. NAVBAR (Navigation)
**Used On**: All authenticated pages

**Components**:
```
┌─────────────────────────────────────────────────────┐
│ [P] Paynion  | Dashboard | Groups | Analytics | ... │
│                                        🔔  👤  ▼     │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Logo with brand name
- Navigation links:
  - Dashboard
  - Groups
  - Analytics
  - Payment History
  - Settings
- Notification bell icon (with unread count badge - TO BE ADDED)
- Profile dropdown menu
  - My Profile
  - Edit Profile
  - Logout
- Sticky positioning (stays at top while scrolling)
- Responsive toggle for mobile

**Styling**:
- Dark background (#1a1a1a)
- Cyan accent color (#00d4ff)
- Hover effects on links
- Active state highlighting

---

### 2. NOTIFICATION BADGE
**Location**: Navbar (bell icon)

**Functionality**:
- Display unread notification count
- Show dropdown with notifications list
- Mark as read on click
- Delete notification option

**Components**:
```
Bell Icon
  ├─ Badge: [5]  (unread count)
  └─ Dropdown Menu (on click)
     ├─ Notification 1 (unread)
     ├─ Notification 2 (read)
     ├─ Notification 3 (unread)
     └─ [VIEW ALL NOTIFICATIONS]
```

---

### 3. MESSAGE ALERTS
**Used On**: All pages (top of content area)

**Components**:
```
Success Message:
┌────────────────────────────────────────┐
│ ✓ Action completed successfully!       │ ✕
└────────────────────────────────────────┘

Error Message:
┌────────────────────────────────────────┐
│ ✗ Error: Something went wrong!         │ ✕
└────────────────────────────────────────┘

Warning Message:
┌────────────────────────────────────────┐
│ ⚠ Please review before proceeding      │ ✕
└────────────────────────────────────────┘

Info Message:
┌────────────────────────────────────────┐
│ ℹ Information message                  │ ✕
└────────────────────────────────────────┘
```

---

### 4. MODAL/CONFIRM DIALOGS
**Used On**: Delete operations, confirmations

**Components**:
```
┌─────────────────────────────────┐
│ CONFIRM ACTION                  │
├─────────────────────────────────┤
│                                 │
│ Are you sure you want to        │
│ delete [Item Name]?             │
│                                 │
│ This action cannot be undone.   │
│                                 │
│ [CONFIRM] [CANCEL]              │
│                                 │
└─────────────────────────────────┘
```

---

### 5. FORM INPUTS (Reusable)
**Variations**:
- Text input
- Email input
- Number input
- Textarea
- Select dropdown
- Checkbox
- Radio button
- File upload
- Date picker
- Percentage input

**Features**:
- Labels with asterisk for required fields
- Placeholder text
- Help text/small descriptions
- Error messages
- Icon support (optional)
- Validation feedback

---

### 6. BUTTONS (Reusable)
**Types**:

Primary Button:
```
[PRIMARY ACTION]
- Usually green or main brand color
- Used for important actions (Save, Submit, Create, Pay)
```

Secondary Button:
```
[SECONDARY ACTION]
- Usually gray or neutral
- Used for less critical actions (Cancel, Back, Reset)
```

Danger Button:
```
[DELETE / DANGER]
- Red color
- Used for destructive actions (Delete, Remove, Decline)
```

Success Button:
```
[SUCCESS / CONFIRM]
- Green color
- Used for confirmations and successful actions
```

Action Buttons:
```
[+ ADD]  [SCAN]  [EDIT]  [DELETE]
- Smaller, icon + text
- Used for inline/card actions
```

---

### 7. STATUS BADGES
**Types**:
```
PENDING      - Gray/Orange background
PAID         - Green background
SETTLED      - Green background
PAID_REQUESTED - Blue background (awaiting confirmation)
ERROR        - Red background
WARNING      - Yellow background
```

---

### 8. EMPTY STATES
**Used When**: No data to display

```
┌──────────────────────────────────────┐
│                                      │
│         📭 No Data Found             │
│                                      │
│   You don't have any [items] yet    │
│                                      │
│   [CREATE NEW / GET STARTED]         │
│                                      │
└──────────────────────────────────────┘
```

---

### 9. LOADING STATES
**Types**:
- Skeleton loaders (card placeholders)
- Spinner animation
- Progress bar
- "Loading..." text with animation

---

### 10. BACKGROUND & STYLING
**Global Styles**:
- Background: Cream (#f5f1e8) with grid pattern
- Cards: Semi-transparent white with glassmorphism effect
- Border-radius: 12px-20px
- Box-shadow: Soft, subtle shadows
- Transitions: 0.3s ease for all interactive elements
- Font: Bootstrap default (Segoe UI, system fonts)
- Colors:
  - Primary: Cyan (#00d4ff)
  - Success: Green (#28a745)
  - Danger: Red (#dc3545)
  - Warning: Yellow (#ffc107)
  - Info: Blue (#0d6efd)
  - Dark: #1a1a1a
  - Light: #f5f1e8

---

## SUMMARY TABLE

| Module | Screen | Route | Key Components |
|--------|--------|-------|-----------------|
| Accounts | Login | `/accounts/login/` | Email, Password, Submit |
| Accounts | Signup | `/accounts/signup/` | Form, Image Upload, Validation |
| Accounts | Dashboard | `/accounts/dashboard/` | Summary Cards, Charts, Expenses List |
| Accounts | Profile | `/accounts/profile/` | User Info Display, Edit Link |
| Accounts | Edit Profile | `/accounts/edit-profile/` | Form, Image Upload |
| Accounts | Analytics | `/accounts/report/` | Charts, Table, PDF Export |
| Groups | All Groups | `/groups/all-groups/` | Group Cards, Search, Create |
| Groups | Create Group | `/groups/create/` | Form, Member Input |
| Groups | Group Detail | `/groups/<id>/` | Members, Balances, Expenses, Settlements |
| Groups | Edit Group | `/groups/<id>/edit/` | Form, Update |
| Groups | Accept Invite | `/groups/invite/accept/<token>/` | Invitation Display, Buttons |
| Expenses | Add Expense | `/expenses/add/<group-id>/` | Form, Bill Upload, Split Options |
| Expenses | Edit Expense | `/expenses/edit/<id>/` | Form, Pre-filled Data |
| Payments | UPI Payment | `/payments/upi-pay/` | QR Code, UPI Link, Instructions |
| Payments | Payment History | `/payments/history/` | Table, Filters, Export |

---

**Document Version**: 1.0  
**Last Updated**: February 4, 2026  
**For**: UI/UX Designer Refinement

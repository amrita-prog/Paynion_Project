# PAYNION - Screens & Components Guide (Short)

**Project**: Expense Splitting & Settlement | **Framework**: Django + Bootstrap 5 | **Lines**: <500

---

## ACCOUNT MODULE (6 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **Login** | `/accounts/login/` | Email/password auth | Email, Password, Submit, Signup link |
| **Signup** | `/accounts/signup/` | User registration | Full name, Email, Password, Image upload |
| **Dashboard** | `/accounts/dashboard/` | Main hub with stats & charts | 4 summary cards, 3 line charts, Recent expenses, Time range filter |
| **Profile** | `/accounts/profile/` | View user info | Profile pic, Name, Email, Phone, Bio, UPI ID |
| **Edit Profile** | `/accounts/edit-profile/` | Update details | Image, Name, Phone, Bio, UPI ID, Save |
| **Analytics** | `/accounts/report/` | Monthly analytics | Month/Year filters, Bar chart, Expense table, PDF export |

---

## GROUPS MODULE (5 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **All Groups** | `/groups/all-groups/` | List user's groups | Create button, Search, Group cards |
| **Create Group** | `/groups/create/` | New group creation | Group name, Description, Add members |
| **Group Detail** | `/groups/<id>/` | **CORE SCREEN** - Expenses, balances, settlements | Group header, Members list, Balances, Settlements, Expenses with splits |
| **Edit Group** | `/groups/<id>/edit/` | Edit group info | Name, Description (pre-filled) |
| **Accept Invite** | `/groups/invite/accept/<token>/` | Accept invitation | Group details, Invited by, Accept/Decline |

---

## EXPENSES MODULE (2 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **Add Expense** | `/expenses/add/<group-id>/` | Create with bill OCR | Bill upload, Amount, Description, Split type (Equal/Percentage/Custom), Members, Dynamic split section |
| **Edit Expense** | `/expenses/edit/<id>/` | Edit expense | Same as Add (pre-filled) |

---

## PAYMENTS MODULE (3 Screens)

| Screen | Route | Functionality | Components |
|--------|-------|---------------|-----------|
| **UPI Payment** | `/payments/upi-pay/` | Generate UPI QR & link | Receiver, Amount, QR code, Copy link, Open UPI app |
| **Mark as Paid** | Settlement | Confirm payment | Payment mode (Cash/UPI), Mark paid button |
| **Payment History** | `/payments/history/` | View transactions | Filters, Table (Date, From, To, Amount, Mode), Export |

---

## GLOBAL COMPONENTS

**Navbar**: Logo, Nav links (Dashboard, Groups, Analytics, History, Settings), Notification bell, Profile dropdown  
**Forms**: Text, Email, Number, Textarea, Select, Checkbox, Radio, File upload, Date picker  
**Buttons**: Primary (Save, Create), Secondary (Cancel), Danger (Delete), Success (Confirm), Small ([+ ADD], [EDIT], [DELETE])  
**Cards**: Semi-transparent white + glassmorphism effect, Border-radius 12-20px, Soft shadows  
**Alerts**: Success, Error, Warning, Info (all dismissible)  
**Badges**: PENDING (gray), PAID/SETTLED (green), PAID_REQUESTED (blue), ERROR (red)  
**Other**: Modals, Empty states, Loading spinners, Confirm dialogs

---

## COLOR & DESIGN SYSTEM

| Element | Color | Notes |
|---------|-------|-------|
| Background | #f5f1e8 (Cream) | Grid pattern overlay |
| Navbar | #1a1a1a (Dark) | Sticky positioning |
| Primary/Accent | #00d4ff (Cyan) | Hover, active states |
| Success | #28a745 (Green) | Confirmations, positive actions |
| Danger | #dc3545 (Red) | Delete, destructive actions |
| Warning | #ffc107 (Yellow) | Warnings, alerts |
| Info | #0d6efd (Blue) | Information messages |
| Text | #333 | Dark gray for readability |

**Typography**: Bootstrap default (Segoe UI, system fonts)  
**Spacing**: 8px, 12px, 16px, 20px increments  
**Transitions**: 0.3s ease for all interactive elements  
**Border Radius**: 6px (inputs), 12px (buttons), 20px (cards)

---

## FEATURE SUMMARY

✅ 14 Screens Total | ✅ Responsive Mobile Design | ✅ Glassmorphism Cards  
✅ Dark Navbar with Cyan Accent | ✅ Real-time Charts & Analytics | ✅ Bill OCR Scanning (AI)  
✅ UPI Payment Integration | ✅ Automatic Settlement Calculation | ✅ PDF Export (Reports)  
✅ Email Invitations | ✅ Notification System | ✅ Time-range Analytics

---

## QUICK ROUTES MAP

**Auth**: Login → Signup → Dashboard  
**Groups**: All Groups → Create/View/Edit → Group Detail  
**Expenses**: Group Detail → Add/Edit Expense → Bill Scanning  
**Payments**: Settlement Card → Mark Paid → UPI/Payment History  
**User**: Dashboard → Profile → Edit Profile

---

**Version**: 1.0 | **Updated**: Feb 4, 2026 | **For**: UI/UX Designer

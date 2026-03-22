"""
seed_demo_data.py
-----------------
Django management command to populate Paynion with realistic Indian dummy data.
SAFE: Only adds new data. Never touches or deletes existing users/groups/expenses.

Usage:
    python manage.py seed_demo_data
    python manage.py seed_demo_data --your-email you@example.com
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

User = get_user_model()


# ── Indian dummy people ──────────────────────────────────────────────────────
PEOPLE = [
    {"full_name": "Priya Sharma",    "email": "priya.sharma@paynion.demo",   "username": "priya_s",   "phone": "9812345671", "upi": "priya@upi"},
    {"full_name": "Rahul Verma",     "email": "rahul.verma@paynion.demo",    "username": "rahul_v",   "phone": "9823456782", "upi": "rahul@upi"},
    {"full_name": "Ananya Iyer",     "email": "ananya.iyer@paynion.demo",    "username": "ananya_i",  "phone": "9834567893", "upi": "ananya@upi"},
    {"full_name": "Arjun Nair",      "email": "arjun.nair@paynion.demo",     "username": "arjun_n",   "phone": "9845678904", "upi": "arjun@upi"},
    {"full_name": "Sneha Kulkarni",  "email": "sneha.kulkarni@paynion.demo", "username": "sneha_k",   "phone": "9856789015", "upi": "sneha@upi"},
    {"full_name": "Karan Mehta",     "email": "karan.mehta@paynion.demo",    "username": "karan_m",   "phone": "9867890126", "upi": "karan@upi"},
]

# ── Group templates ──────────────────────────────────────────────────────────
GROUP_TEMPLATES = [
    {
        "title": "Goa Trip 🌊",
        "description": "2024 New Year Goa trip with college friends",
        "member_indices": [0, 1, 2, 3],
        "expenses": [
            {"desc": "Hotel Taj Baga (3 nights)",         "amount": 14400, "paid_by": 0, "days_ago": 25},
            {"desc": "Flight tickets Mumbai-Goa",          "amount": 9600,  "paid_by": 1, "days_ago": 28},
            {"desc": "Scuba diving at Calangute",          "amount": 4800,  "paid_by": 2, "days_ago": 24},
            {"desc": "Ferry to Divar Island",              "amount": 800,   "paid_by": 3, "days_ago": 24},
            {"desc": "Seafood dinner at Fisherman's Wharf","amount": 3200,  "paid_by": 0, "days_ago": 23},
            {"desc": "Bike rentals for 3 days",            "amount": 2400,  "paid_by": 1, "days_ago": 25},
            {"desc": "Dudhsagar Falls cab",                "amount": 1600,  "paid_by": 2, "days_ago": 22},
        ]
    },
    {
        "title": "Flat Expenses 🏠",
        "description": "Monthly shared expenses for 3BHK in Bandra",
        "member_indices": [0, 1, 4],
        "expenses": [
            {"desc": "Rent - March",         "amount": 42000, "paid_by": 0, "days_ago": 10},
            {"desc": "Electricity Bill",     "amount": 3200,  "paid_by": 1, "days_ago": 8},
            {"desc": "Wi-Fi Jio Fiber",      "amount": 1199,  "paid_by": 4, "days_ago": 12},
            {"desc": "Gas cylinder refill",  "amount": 950,   "paid_by": 0, "days_ago": 15},
            {"desc": "Society maintenance",  "amount": 2500,  "paid_by": 1, "days_ago": 5},
            {"desc": "Water cans (10)",       "amount": 400,   "paid_by": 4, "days_ago": 3},
            {"desc": "House cleaning bai",   "amount": 1800,  "paid_by": 0, "days_ago": 2},
        ]
    },
    {
        "title": "Office Lunch 🍱",
        "description": "Daily lunch pool at Whitefield office",
        "member_indices": [1, 2, 3, 5],
        "expenses": [
            {"desc": "MTR lunch thali x4",     "amount": 680,   "paid_by": 1, "days_ago": 1},
            {"desc": "Swiggy biryani order",   "amount": 1240,  "paid_by": 2, "days_ago": 2},
            {"desc": "Dominos pizza Friday",   "amount": 899,   "paid_by": 3, "days_ago": 4},
            {"desc": "Chai & snacks",          "amount": 280,   "paid_by": 5, "days_ago": 5},
            {"desc": "Barbeque Nation dinner", "amount": 5600,  "paid_by": 1, "days_ago": 7},
            {"desc": "Lunch Meghana Foods",    "amount": 1120,  "paid_by": 2, "days_ago": 9},
        ]
    },
    {
        "title": "Manali Winter Trip ❄️",
        "description": "December ski trip to Manali with cousins",
        "member_indices": [2, 3, 4, 5],
        "expenses": [
            {"desc": "Volvo bus Delhi-Manali (8 seats)", "amount": 12000, "paid_by": 2, "days_ago": 45},
            {"desc": "Snow View Hotel 4 nights",          "amount": 18000, "paid_by": 3, "days_ago": 44},
            {"desc": "Ski equipment rental",              "amount": 5200,  "paid_by": 4, "days_ago": 43},
            {"desc": "Solang Valley cable car",           "amount": 2400,  "paid_by": 5, "days_ago": 43},
            {"desc": "Rohtang Pass permit + cab",         "amount": 4800,  "paid_by": 2, "days_ago": 42},
            {"desc": "Meals & chai (4 days)",             "amount": 6400,  "paid_by": 3, "days_ago": 41},
        ]
    },
    {
        "title": "Birthday Party 🎂",
        "description": "Rahul's 25th birthday celebration at Bombay Brasserie",
        "member_indices": [0, 1, 2, 4, 5],
        "expenses": [
            {"desc": "Restaurant dinner bill",    "amount": 8500,  "paid_by": 0, "days_ago": 14},
            {"desc": "Cake from Theobroma",       "amount": 1200,  "paid_by": 2, "days_ago": 14},
            {"desc": "Decorations & balloons",    "amount": 800,   "paid_by": 4, "days_ago": 15},
            {"desc": "Photobooth rental",         "amount": 1500,  "paid_by": 5, "days_ago": 14},
            {"desc": "Gift for birthday boy",     "amount": 3000,  "paid_by": 0, "days_ago": 13},
        ]
    },
]


class Command(BaseCommand):
    help = "Seeds the database with realistic Indian dummy data for demo/presentation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--your-email",
            type=str,
            default=None,
            help="Your existing account email — will be added to all groups as a member.",
        )

    def handle(self, *args, **options):
        from groups.models import Group
        from expenses.models import Expense, ExpenseSplit
        from payments.models import Settlement

        self.stdout.write(self.style.WARNING("\n🌱 Starting Paynion demo data seed...\n"))

        your_email = options.get("your_email")
        your_user = None
        if your_email:
            try:
                your_user = User.objects.get(email=your_email)
                self.stdout.write(self.style.SUCCESS(f"   ✓ Found your account: {your_user.full_name}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"   ⚠ No user found with email '{your_email}'. Proceeding without linking."))

        # ── Step 1: Create demo users ────────────────────────────────────────
        self.stdout.write("\n👥 Creating demo users...")
        demo_users = []
        for p in PEOPLE:
            if User.objects.filter(email=p["email"]).exists():
                user = User.objects.get(email=p["email"])
                self.stdout.write(f"   → Already exists: {user.full_name}")
            else:
                user = User.objects.create_user(
                    email=p["email"],
                    username=p["username"],
                    full_name=p["full_name"],
                    password="Demo@1234",
                    phone=p["phone"],
                    upi_id=p["upi"],
                    first_name=p["full_name"].split()[0],
                    last_name=p["full_name"].split()[-1],
                )
                self.stdout.write(self.style.SUCCESS(f"   ✓ Created: {user.full_name}"))
            demo_users.append(user)

        # ── Step 2: Create groups and expenses ───────────────────────────────
        self.stdout.write("\n📁 Creating groups + expenses...")
        for tmpl in GROUP_TEMPLATES:
            group_title = tmpl["title"]

            # Skip if this demo group already exists
            if Group.objects.filter(title=group_title).exists():
                self.stdout.write(f"   → Already exists: {group_title}")
                continue

            members = [demo_users[i] for i in tmpl["member_indices"]]
            creator = members[0]

            group = Group.objects.create(
                title=group_title,
                description=tmpl["description"],
                created_by=creator,
            )
            group.members.set(members)
            if your_user:
                group.members.add(your_user)

            self.stdout.write(self.style.SUCCESS(f"   ✓ Group: {group_title} ({len(members)} members)"))

            # Create expenses
            for exp_data in tmpl["expenses"]:
                paid_by_user = demo_users[exp_data["paid_by"]]
                amount = Decimal(str(exp_data["amount"]))
                created_at = timezone.now() - timedelta(days=exp_data["days_ago"])

                expense = Expense.objects.create(
                    group=group,
                    amount=amount,
                    description=exp_data["desc"],
                    paid_by=paid_by_user,
                    split_type="equal",
                    created_at=created_at,
                )

                # Override auto_now_add using queryset update
                Expense.objects.filter(pk=expense.pk).update(created_at=created_at)

                # Create equal splits across all group members
                all_members = list(group.members.all())
                split_count = len(all_members)
                split_amount = (amount / split_count).quantize(Decimal("0.01"))
                remainder = amount - (split_amount * split_count)

                for idx, member in enumerate(all_members):
                    member_share = split_amount + (remainder if idx == 0 else Decimal("0.00"))
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=member,
                        amount=member_share,
                    )

            self.stdout.write(f"      → {len(tmpl['expenses'])} expenses added")

        # ── Step 3: Create some settled payments ────────────────────────────
        self.stdout.write("\n💸 Creating some settled payments...")
        settled_pairs = [
            (0, 1, "Goa Trip 🌊",       2400),
            (3, 2, "Manali Winter Trip ❄️", 3100),
            (4, 0, "Flat Expenses 🏠",   4500),
        ]
        for payer_idx, recv_idx, group_title, amount in settled_pairs:
            try:
                group = Group.objects.get(title=group_title)
                payer = demo_users[payer_idx]
                receiver = demo_users[recv_idx]
                if not Settlement.objects.filter(group=group, payer=payer, receiver=receiver).exists():
                    s = Settlement.objects.create(
                        group=group,
                        payer=payer,
                        receiver=receiver,
                        amount=Decimal(str(amount)),
                        payment_mode="UPI",
                        status="SETTLED",
                        settled_at=timezone.now() - timedelta(days=random.randint(1, 5)),
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"   ✓ Settled ₹{amount}: {payer.full_name} → {receiver.full_name}"
                    ))
            except Group.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS("\n✅ Seed complete! Your dashboard should now look full.\n"))
        self.stdout.write("   Demo user password: Demo@1234")
        self.stdout.write("   Demo emails: priya.sharma@paynion.demo, rahul.verma@paynion.demo, etc.\n")

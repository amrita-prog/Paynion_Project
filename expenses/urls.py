from django.urls import path
from .views import add_expense, delete_expense, edit_expense, scan_bill

app_name = "expenses"

urlpatterns = [
    path("add/<int:group_id>/", add_expense, name="add_expense"),
    path("delete/<int:expense_id>/", delete_expense, name="delete_expense"),    
    path("edit/<int:expense_id>/", edit_expense, name="edit_expense"),
    path("scan-bill/", scan_bill, name="scan_bill"),
]

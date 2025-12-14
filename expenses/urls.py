from django.urls import path
from .views import add_expense_in_group, add_expense_direct

urlpatterns = [
    path("add/<int:group_id>/", add_expense_in_group, name="add_expense_group"),
    path("add/", add_expense_direct, name="add_expense"),
]

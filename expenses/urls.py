from django.urls import path
from .views import add_expense

urlpatterns = [
    path("add/<int:group_id>/", add_expense, name="add_expense"),
]

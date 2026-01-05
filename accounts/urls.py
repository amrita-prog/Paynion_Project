from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path("my-expenses/", views.my_paid_expenses, name="my_expenses"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
]
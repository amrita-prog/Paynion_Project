from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_group, name="create_group"),
    path("edit/<int:group_id>/", views.edit_group, name="edit_group"),
    path("delete/<int:group_id>/", views.delete_group, name="delete_group"),
    path("all/", views.view_all_group, name="view_all_group"),
    path("detail/<int:group_id>/", views.group_detail, name="group_detail"),
]

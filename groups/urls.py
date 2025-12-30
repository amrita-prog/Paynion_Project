from django.urls import path
from . import views
import uuid

app_name = "groups"

urlpatterns = [
    path("create/", views.create_group, name="create_group"),
    path("edit/<int:group_id>/", views.edit_group, name="edit_group"),
    path("delete/<int:group_id>/", views.delete_group, name="delete_group"),
    path("all/", views.view_all_group, name="view_all_group"),
    path("detail/<int:group_id>/", views.group_detail, name="group_detail"),
    path("add_member/<int:group_id>/", views.add_member, name="add_member"),
    path("remove_member/<int:group_id>/<int:user_id>/", views.remove_member, name="remove_member"),
    path("invite/send/<int:group_id>/", views.send_group_invite, name="send_invite"),
    path("invite/accept/<uuid:token>/", views.accept_group_invite, name="accept_invite"),
]

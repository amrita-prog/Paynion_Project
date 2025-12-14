from django import forms
from .models import Group

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["title", "description", "members"]  # बस यही 3
        widgets = {
            "members": forms.CheckboxSelectMultiple()
        }
        labels = {
            "title": "Group Title",
            "description": "Group Description",
            "members": "Select Members"
        }
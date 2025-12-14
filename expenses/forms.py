from django import forms
from .models import Expense
from groups.models import Group   # ✅ YE LINE MISSING THI
from django.contrib.auth import get_user_model

User = get_user_model()


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "group",
            "amount",
            "description",
            "split_type",
            "split_between",
        ]

        widgets = {
            "group": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "split_type": forms.RadioSelect(),
            "split_between": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop("group", None)
        super().__init__(*args, **kwargs)

        # 🔹 Group ke members hi dikhane hain
        if group:
            self.fields["group"].widget = forms.HiddenInput()
            self.fields["group"].initial = group
            self.fields["split_between"].queryset = group.members.all()
        else:
            self.fields["group"].queryset = Group.objects.all()
            self.fields["split_between"].queryset = User.objects.none()

from django import forms
from .models import Expense
from django.contrib.auth import get_user_model

User = get_user_model()


class ExpenseForm(forms.ModelForm):
    # FORM-ONLY field 
    split_between = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Expense
        fields = [
            "amount",
            "description",
            "split_type",
        ]
        widgets = {
            "split_type": forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop("group", None)
        super().__init__(*args, **kwargs)

        if group:
            # sirf group ke members hi dikhenge
            self.fields["split_between"].queryset = group.members.all()
        else:
            self.fields["split_between"].queryset = User.objects.none()

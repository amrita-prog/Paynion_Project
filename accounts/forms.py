from django import forms
from django.contrib.auth.forms import UserCreationForm # username, p1, p2
from .models import CustomUser
import uuid #base64 unique key generator

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['full_name','email','password1','password2','phone','profile_image']

    def save(self, commit=True):
        user = super().save(commit=False) # dont save
        
        # Assigning custom fields
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone')
        user.profile_image = self.cleaned_data.get('profile_image')

         # FIXED split() and removed wrong space
        base_username = user.email.split('@')[0] # amrita@gmail.com --> [amrita,gmail.com]
        user.username = f"{base_username}_{uuid.uuid4().hex[:4]}" # this will generate username with hexadecimal value

        # VERY IMPORTANT: hash password correctly
        password = self.cleaned_data.get("password1")
        user.set_password(password)

        if commit:
            user.save()
        return user
    

class EditProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        "class": "d-none",
        "accept": "image/*"
    }))
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone','upi_id', 'bio', 'profile_image']

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control','rows': 3}),
        }
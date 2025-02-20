from django import forms
from .models import Submission, AnswerKey
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Form Pendaftaran (Register)
class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Daftar sebagai")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password']

# Form Login
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AnswerKeyForm(forms.ModelForm):  # Form untuk dosen
    class Meta:
        model = AnswerKey
        fields = ['uploaded_code', 'uploaded_file']

class CodeUploadForm(forms.ModelForm):  # Form untuk mahasiswa
    class Meta:
        model = Submission
        fields = ['student_name', 'uploaded_code', 'uploaded_file']

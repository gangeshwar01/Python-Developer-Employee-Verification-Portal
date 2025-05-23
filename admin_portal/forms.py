from django import forms
from .models import Employee, Task, Certificate, SiteSettings

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False, help_text='Set or change the password.')
    profile_image = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    join_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), help_text='Select the date in YYYY-MM-DD format')
    left_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False, help_text='Select the date in YYYY-MM-DD format (optional)')

    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'designation', 'join_date', 'left_date', 'phone', 'address', 'profile_image', 'department', 'email']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['employee', 'title', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CertificateVerificationForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['status', 'rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'rejected' and not rejection_reason:
            raise forms.ValidationError("Please provide a reason for rejection.")

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['logo', 'theme', 'custom_theme_color']
        widgets = {
            'theme': forms.Select(choices=[('light', 'Light'), ('dark', 'Dark'), ('custom', 'Custom')]),
            'custom_theme_color': forms.TextInput(attrs={'type': 'color'})
        } 
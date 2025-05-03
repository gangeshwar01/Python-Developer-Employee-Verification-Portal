from django import forms
from admin_portal.models import Certificate

class CertificateUploadForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB')
            
            # Check file extension
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Unsupported file type. Please upload PDF or image files.')
        return file 
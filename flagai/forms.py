from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['description', 'document', 'offender_link', 'people_involved', 'contact_email', 'feedback']
        widgets = {
            'contact_email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

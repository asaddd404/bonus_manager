from django import forms
from .models import Client, MessageTemplate

class AddClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'balance']
        widgets = {
            'phone': forms.TextInput(attrs={'data-inputmask': "'mask': '+7(999)-999-99-99'"}),
        }

class BonusForm(forms.Form):
    amount = forms.DecimalField(min_value=0.01, decimal_places=2)
    type = forms.ChoiceField(choices=[('accrual', 'Начисление'), ('deduction', 'Списание')])

class TemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['accrual_template', 'deduction_template', 'reset_template']
        widgets = {
            'accrual_template': forms.Textarea(attrs={'rows': 3}),
            'deduction_template': forms.Textarea(attrs={'rows': 3}),
            'reset_template': forms.Textarea(attrs={'rows': 3}),
        }
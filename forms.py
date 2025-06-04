from django import forms

class CodeForm(forms.Form):
    user_input = forms.CharField(widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Enter code or prompt..."}))

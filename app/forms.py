from django import forms


class PositiveTestForm(forms.Form):
    name = forms.CharField(label="Person's name", max_length=100)
    phone = forms.CharField(label="Person's phone number", max_length=100)

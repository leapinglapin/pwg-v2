from django import forms

from tokens.models import Token, TokenCost


class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = ['name']


class TokenCostForm(forms.ModelForm):
    class Meta:
        model = TokenCost
        fields = ['token', 'cost']

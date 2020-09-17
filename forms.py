from django.forms import ModelForm
from django import forms

from .models import Research


class ResearchForm(ModelForm):

    class Meta:
        model = Research
        fields = [
            'name', 'objective'
        ]

class BasesForm(ModelForm):

    class Meta:
        model = Research
        fields = ('search_bases',)
        widgets = {
            'search_bases': forms.CheckboxSelectMultiple(),
        } 

class SearchParamsForm(ModelForm):
    class Meta:
        model = Research
        fields = ('search_params_string', 'search_params_date')


class PaperReviewForm(forms.Form):
    approved = forms.BooleanField(label="Paper approved?", required=False)
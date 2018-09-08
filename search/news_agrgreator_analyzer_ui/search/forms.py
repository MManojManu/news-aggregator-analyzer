from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Search Keyword Here'}),
                             max_length=50, label='', required=False)


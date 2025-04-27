from django import forms

class StockSearchForm(forms.Form):
    stock_name = forms.CharField(label='Stock Name', max_length=100)
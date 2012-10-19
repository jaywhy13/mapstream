from django import forms

class ThemeForm(forms.Form):

	name = forms.CharField(label="Enter a name for the theme, e.g. 'Disaster'", max_length=255)
	words = forms.CharField(label="Enter words describing the theme separated by commas, e.g. earthquake, flooding, flood, tropical storm'")
	color = forms.CharField(label="Select a color", max_length=10)


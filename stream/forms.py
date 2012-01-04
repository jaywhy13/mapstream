from django import forms
from models import EventType

class ReportEventForm(forms.Form):
	event_type_choices = [(t.id, t.name) for t in EventType.objects.all()]
	event_type = forms.ChoiceField(choices=event_type_choices)
	location = forms.CharField();
	lat_long = forms.CharField(widget=forms.HiddenInput())
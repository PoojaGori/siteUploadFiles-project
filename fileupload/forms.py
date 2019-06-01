from django import forms
from .models import SubmissionDetails

from django.forms import ModelForm, Textarea

class SubmitForm(forms.ModelForm):

    file1 = forms.FileField(label='Upload File', required=False)
    class Meta:
        model = SubmissionDetails
        # fields = ['process_department','process_ent_id','user','project','asset','version']
        fields = ['comments']
        fields_order = ['file1', 'comments']
        widgets = {
          'comments': Textarea(attrs={'rows':6, 'cols':40}),
        }

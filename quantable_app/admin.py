from django import forms
from django.contrib import admin
from .models import Quantable


class QuantableAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pair_id'].required = False
        self.fields['vote_stddev'].required = False
        self.fields['vote_skewness'].required = False

    class Meta:
        model = Quantable
        fields = '__all__'


@admin.register(Quantable)
class QuantableAdmin(admin.ModelAdmin):
    form = QuantableAdminForm

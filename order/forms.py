from django import forms
from django.forms import ModelForm
from .models import *


class OrderForm(ModelForm):
    # pickup_time = forms.DateTimeField(input_formats=["%Y-%m-%d %I:%M %p",])

    class Meta:
        model = Order
        fields = ['dropoff_addr', 'pickup_addr', 'contact_name', 'phone', 'pickup_time', 'dropoff_time', 'items'
            , 'payment_type']
        widgets = {
            'dropoff_addr': forms.TextInput(
                attrs={'required': True, 'class': 'form-control'}
            ),
            'pickup_addr': forms.TextInput(
                attrs={'readonly': True, 'class': 'form-control'}
            ),
            'contact_name': forms.TextInput(
                attrs={'readonly': True, 'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'readonly': True, 'class': 'form-control'}
            ),
            'pickup_time': forms.DateTimeInput(
                attrs={'readonly': True, 'class': 'form-control'},
                format='%Y-%m-%d %I:%M %p',
            ),
            'dropoff_time': forms.DateTimeInput(
                attrs={'readonly': True, 'class': 'form-control'},
                format='%Y-%m-%d %I:%M %p',
            ),        
            'items': forms.Select(
                choices=ITEMS,             	
                attrs={'readonly': True, 'class': 'form-control'}
            ),        
            'payment_type': forms.Select(
                choices=PAYMENT_TYPE,             	            	
                attrs={'readonly': True, 'class': 'form-control'}
            ),        
        }
        labels = {
            'dropoff_addr': 'Drop off Address',
            'pickup_addr': 'Pick up Address',
            'pickup_time': 'Pick up Time',
            'dropoff_time': 'Drop off Time',
        }
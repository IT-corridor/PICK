import hashlib, datetime, random
import requests
import json
import re

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from twilio.rest import TwilioRestClient 
from geopy.geocoders import Nominatim

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from .permissions import IsOwnerOnly
from .serializers import OrderSerializer
from sender.models import *
from .models import *
from .forms import *


class OrderViewSet(viewsets.ModelViewSet):
    """
    Creates/Returns Sender's order details in JSON format.

    Accepts the following GET parameters: token\n
    Accepts the following POST parameters:\n
        Required: token, contact_name, receiver's phone number, pickup time, dropoff time\n
        Optional: pickup address, items, payment type.\n
           default pickup address is sender's location.\n
           default items is sender's package type.\n
    Returns the created order or order list.
    """

    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOnly,)

    def perform_create(self, serializer):
		sender = Sender.objects.get(email=self.request.user)
		content = serializer.validated_data
		pickup_addr = sender.address
		if 'pickup_addr' in content:
			pickup_addr = content['pickup_addr']

		items = sender.package_type
		if 'items' in content:
			items = content['items']
		
		salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
		key = hashlib.sha1(salt+content['phone']).hexdigest()

		order = serializer.save(owner=self.request.user, pickup_addr=pickup_addr, items=items, key=key)
		# send SMS to confirm 
		send_SMS(order)

		print "Please provide your address and confirm your order. http://api.pick.sam/order_confirm/%d/%s" % (order.id, order.key)

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)


def confirm_order(request, id, key):
	try:
		order = Order.objects.get(id=id, key=key)
		
		if request.method == 'POST':
			orderform = OrderForm(request.POST)
			if orderform.is_valid():
				post = orderform.save(commit=False)			
				order.dropoff_addr=get_real_address(post.dropoff_addr)
				order.dropoff_time=post.dropoff_time
				order.save()				
				# send delivery request api
				send_delivery_request(order)
				return render(request, 'confirm_order_done.html', {'track_link': order.track_link})		
		else:
			orderform = OrderForm(initial=model_to_dict(order))

		# print orderform	
		context = {
			'id': id,
			'key': key,
			'orderform': orderform,
		}

		return render(request, 'confirm_order.html', context)		
	except ObjectDoesNotExist:
		return HttpResponse('Your link is invalid or expired!')	


def order_completed(request):
	'''
	web hook for order finish
	'''
	print 'Order is successfully finished'
	print request.json()

def get_real_address(address_location):
	'''
	if the argument is location, get the real address from it
	'''
	if re.search(r'^LatLng\(.*\)$', address_location):
		location = address_location[7:-1]
		geolocator = Nominatim()
		address = geolocator.reverse(location)
		return address.address
	else:
		return address_location

def send_SMS(order):
	'''
	send SMS to the customer to confirm the order using twilio
	'''
	client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN) 
	 
	client.messages.create(
		to='+'+order.phone, 
		from_="+12025688404", 
		body="Please provide your address and confirm your order. http://api.pick.sa/order_confirm/%d/%s" % (order.id, order.key),  
	)


def send_delivery_request(order):
	url = 'https://app.getswift.co/api/v2/deliveries'
	header = {"Content-Type": "application/json"}
	sender = Sender.objects.get(email=order.owner)

	body = {
		"apiKey": settings.APIKEY_GETSWIFT,
		"booking":{
			"pickupDetail": {
				"name": sender.first_name + ' ' + sender.last_name,
				"phone": sender.phone,
				"address": order.pickup_addr
			},
			"dropoffDetail": {
				"name": order.contact_name,
				"phone": order.phone,
				"address": order.dropoff_addr
			}
		}
	}            

	res = requests.post(url=url, headers=header, data=json.dumps(body))
	res_json = res.json()

	# update the state of the order
	order.status = 'Received'	
	order.track_link = res_json['delivery']['trackingUrls']['api']
	order.save()

	print res.json(), '@@@@@@@@@@'		

from core.models import Category ,Order , Share , Sharelist , Transport , GST_Numbers, Phone_Number, Address, Item
from accounts.forms import SignInViaUsernameForm
import django
import datetime ,datetime
import pytz
import time

def add_variable_to_context(request):
    csrf_token = django.middleware.csrf.get_token(request)
    mylist = dict()
    categories = Category.objects.all()
    for i in categories:
        item = Item.objects.filter(category = i.id)
        if (len(item)):
            mylist[i.id] = item[0].image.url
    return {
        'image_list' : mylist,
        'csrf_token':csrf_token,
        'category_list': Category.objects.all(),
        'transport_list': Transport.objects.all()
    }


def add_form_to_context(request):
    return {
        'loginform': SignInViaUsernameForm
    }

def present_order(request):
    try:
        if request.user.is_authenticated:
            Present_order = Order.objects.get(user = request.user, ordered = False)
            return {
                'present_order': Present_order,
                'gst_list':GST_Numbers.objects.filter(user=request.user),
                'phone_list':Phone_Number.objects.filter(user=request.user),
                'address_list':Address.objects.filter(user=request.user),

            }
        else:
            return {
            'present_order': 0
            }
    except Order.DoesNotExist:
        return {
            'present_order': 0,
            'gst_list':GST_Numbers.objects.filter(user=request.user),
            'phone_list':Phone_Number.objects.filter(user=request.user),
            'address_list':Address.objects.filter(user=request.user)
        }

def present_share(request):
    try:
        if request.user.is_authenticated:
            present_share = Share.objects.get(user = request.user, shared = False)
            return {
                'present_share': present_share
            }
        else:
            return {
            'present_share': 0
            }
    except Share.DoesNotExist:
        return {
            'present_share': 0
        }


def check_user(request):
    try:
        if request.user.is_authenticated:
            if not request.user.userprofile:
                users= 1
            else:
                users = 1
        else:
            users =0

        return {
            'user_valid': users
        }
    except:
        return {
            'user_valid': 0
        }






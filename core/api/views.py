from django_countries import countries
from accounts.models import LoggedInUser
from django.db.models import Q
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from Cashbackclick import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect ,HttpResponse
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
from django.views import generic
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
import os
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
import django
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from core.models import Item, OrderItem, Order
from .serializers import (
    ItemSerializer, OrderSerializer, ItemDetailSerializer, AddressSerializer,
    PaymentSerializer, ShareSerializer
)
from core.models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Variation, ItemVariation ,SharedItem,Share, Sharelist, Category , Transport, GST_Numbers, Phone_Number

from django.http import HttpResponseRedirect
from uuid import uuid4
import stripe
from django.template.loader import get_template

from django.http import HttpResponse
from django.views.generic import View

from core.api.utils import render_to_pdf #created in step 4

import datetime
from core.forms import AddressForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import pytz
import requests

#stripe.api_key = settings.STRIPE_SECRET_KEY


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)


class ItemListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ItemSerializer
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if request.user.userprofile.owner or request.user.userprofile.one_click_purchasing:
                    csrf_token = django.middleware.csrf.get_token(request)
                    queryset = Item.objects.filter(stock = True).order_by('?')
                    page = request.GET.get('page', 1)
                    paginator = Paginator(queryset, 20)
                    try:
                        users = paginator.page(page)
                    except PageNotAnInteger:
                        users = paginator.page(1)
                    except EmptyPage:
                        users = paginator.page(paginator.num_pages)

                    first_index = users.number - 5
                    last_index = users.number + 5
                    return render(request,"core/products.html",{"object_list":users,
                    "csrf_token": csrf_token , 'min':first_index,'max':last_index})
                else:
                    csrf_token = django.middleware.csrf.get_token(request)
                    queryset = Sharelist.objects.get(shared_user = request.user)
                    items =[]
                    final_items = []
                    date_today = datetime.date.today()
                    if queryset.share.end_date >= datetime.datetime(year= int(date_today.year), month = int(date_today.month) , day = int(date_today.day) ,tzinfo=pytz.UTC) and queryset.share.shared:
                        final_items = queryset.share.items.all()

                    for item in final_items:
                        if item.item.stock and item.item not in items:
                            items.append(item.item)
                            print(item.item)

                    if len(items):
                        page = request.GET.get('page', 1)
                        paginator = Paginator(list(set(items)), 20)
                        try:
                            users = paginator.page(page)
                        except PageNotAnInteger:
                            users = paginator.page(1)
                        except EmptyPage:
                            users = paginator.page(paginator.num_pages)

                        first_index = users.number - 5
                        last_index = users.number + 5
                        first_index = users.number - 5
                        last_index = users.number + 5
                        return render(request,"core/products.html",{"object_list":users,
                        "csrf_token": csrf_token , 'min':first_index,'max':last_index})
                    else:
                        users=[]
                        return render(request,"core/products.html",{"object_list":users,
                        "csrf_token": csrf_token})
            except Exception as e:
                print(str(e))
                print("Except")
                return render(request,"core/products.html",{"new__message":1})
        else:
            return redirect('accounts:login')
    def post(self, request, *args, **kwargs):
        print(request.POST)
        if request.user.is_authenticated:
            if request.user.userprofile.owner or request.user.userprofile.one_click_purchasing :
                csrf_token = django.middleware.csrf.get_token(request)
                queryset = Item.objects.filter(stock = True)
                page = request.GET.get('page', 1)
                paginator = Paginator(queryset, 10)
                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)

                return render(request,"core/products.html",{"object_list":users,
                "csrf_token": csrf_token})
            else:
                csrf_token = django.middleware.csrf.get_token(request)
                queryset = Sharelist.objects.filter(shared_user = request.user,share__shared = True)
                items =[]
                for my_sharelist in queryset:
                    for my_share_item in my_sharelist.share.items.all():
                        if my_share_item.item.stock:
                            items.append(my_share_item.item)
                if len(items):
                    page = request.GET.get('page', 1)
                    paginator = Paginator(list(set(items)), 10)
                    try:
                        users = paginator.page(page)
                    except PageNotAnInteger:
                        users = paginator.page(1)
                    except EmptyPage:
                        users = paginator.page(paginator.num_pages)


                    return render(request,"core/products.html",{"object_list":users,
                    "csrf_token": csrf_token})
                else:
                    users=[]
                    return render(request,"core/products.html",{"object_list":users,
                    "csrf_token": csrf_token})
        else:
            return redirect('accounts:login')



class ItemDetailView(generic.DetailView):
    model = Item
    template_name = "core/single.html"
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk",None)
            item = Item.objects.get(id=pk)
            item_list = Item.objects.filter(category = item.category)
            related_items = list(item_list)[:4]
            return render(request, "core/single.html",{"object":item,"object_list":related_items})
        except Item.DoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            print("hero")
            return redirect("order-list")









class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)



def add_to_cart(request, *args, **kwargs):
    if request.method == 'GET':
        pk = kwargs.get(
            "pk",
            None
        )
        item = get_object_or_404(Item, id=pk)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False,
            quantity = item.set

        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity =  order_item.quantity  + order_item.item.set
                order_item.save()
                return redirect(request.META['HTTP_REFERER'])
            else:
                order.items.add(order_item)
                return redirect(request.META['HTTP_REFERER'])
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return redirect(request.META['HTTP_REFERER'])
    elif request.method == "POST":
        print(request.POST)
        pk = request.POST["pk"]
        print(pk)
        item = get_object_or_404(Item, id=int(pk))
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False,
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity =  order_item.quantity  + order_item.item.set
                order_item.save()
                return redirect(request.META['HTTP_REFERER'])
            else:
                order_item.quantity = order_item.item.set
                order_item.save()
                order.items.add(order_item)
                return redirect(request.META['HTTP_REFERER'])
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order_item.quantity = order_item.item.set
            order_item.save()
            order.items.add(order_item)
            return redirect(request.META['HTTP_REFERER'])







def add_to_share(request, *args, **kwargs):
    if request.method == "GET":
        pk = kwargs.get(
                "pk",
                None
            )
    elif request.method == "POST":
        print(request.POST)
        pk = request.POST["pk"]
        print(pk)
    item = get_object_or_404(Item, pk=pk,stock =True)
    share_item, created = SharedItem.objects.get_or_create(
        item=item,
        user=request.user,
        shared=False
    )
    print(share_item, created)
    share_qs = Share.objects.filter(user=request.user, shared=False)
    if share_qs.exists():
        share = share_qs[0]
        # check if the order item is in the order
        if share.items.filter(item__pk=item.pk).exists():
            return redirect(request.META['HTTP_REFERER'])
        else:
            share.items.add(share_item)
            return redirect(request.META['HTTP_REFERER'])

    else:
        shared_date = timezone.now()
        share = Share.objects.create(
            user=request.user, shared_date=shared_date)
        share.items.add(share_item)
        return redirect(request.META['HTTP_REFERER'])

def remove_to_share(request, *args, **kwargs):
    if request.method == "GET":
        pk = kwargs.get(
                "pk",
                None
            )
    elif request.method == "POST":
        print(request.POST)
        pk = request.POST["pk"]
        print(pk)
    item = get_object_or_404(Item, pk=pk,stock =True)
    share_item, created = SharedItem.objects.get_or_create(
        item=item,
        user=request.user,
        shared=False
    )
    share_qs = Share.objects.filter(user=request.user, shared=False)
    if not created:
        if share_qs.exists():
            share = share_qs[0]
            # check if the order item is in the order
            if share.items.filter(item__pk=item.pk).exists():
                share.items.remove(share_item)
                return redirect(request.META['HTTP_REFERER'])
            else:
                return redirect(request.META['HTTP_REFERER'])

        else:
            shared_date = timezone.now()
            share = Share.objects.create(
                user=request.user, shared_date=shared_date)
            share.items.add(share_item)
            return redirect(request.META['HTTP_REFERER'])


def add_to_share_category(request,*args, **kwargs):
    categoryid = kwargs.get(
            "categoryid",
            None
        )
    category = Category.objects.get(id = categoryid)
    query = Q(stock = True)
    query.add(Q(category = category), Q.AND)
    query.add(Q(category__parent = category), Q.OR,)
    query.add(Q(category__parent__parent = category), Q.OR,)
    queryset = Item.objects.filter(query)
    print(queryset)
    for item in queryset:
        share_item, created = SharedItem.objects.get_or_create(
        item=item,
        user=request.user,
        shared=False
        )
        share_qs = Share.objects.filter(user=request.user, shared=False)
        if not share_qs.exists():
            shared_date = timezone.now()
            share = Share.objects.create(
                user=request.user, shared_date=shared_date)
            share.items.add(share_item)
            messages.info(request, "This item was added to your Sharelist")
        else:
            share = share_qs[0]
            share.items.add(share_item)

    return redirect(request.META['HTTP_REFERER'])

class OrderItemDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = OrderItem.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        pk = request.data.get('pk', None)
        variations = request.data.get('variations', [])
        if pk is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, pk=pk)

        minimum_variation_count = Variation.objects.filter(item=item).count()
        if len(variations) < minimum_variation_count:
            return Response({"message": "Please specify the required variation types"}, status=HTTP_400_BAD_REQUEST)

        order_item_qs = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
        )
        for v in variations:
            order_item_qs = order_item_qs.filter(
                Q(item_variations__exact=v)
            )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_item.item_variations.add(*variations)
            order_item.save()

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order_placed': 1,
                'object': order,
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("order-list")

class OrderListView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.all()
            my_order = qs.filter(user=self.request.user)
            if len(my_order):
                context = {
                    'order_list':1,
                    'object': my_order[::-1],
                }
            else:
                context = {
                    'no_order':1,
                    'order_list':1,
                    'object': my_order
                }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            print("hero")
            return redirect("/")
        except Exception as e:
            print(str(e))
            return redirect("/")




class DispatchDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter( ordered=True)
            my_order =[]
            for check_order in order:
                if check_order.get_total():
                    my_order.append(check_order)
                else:
                    check_order.delete()
            if len(my_order):
                context = {
                    'dispatch':1,
                    'object': my_order[::-1],
                }
            else:
                context = {
                    'no_order':1,
                    'dispatch':1,
                    'object': my_order,
                }

            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")



class SharelistAPI(RetrieveAPIView):
    serializer_class = ShareSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Sharelist.objects.filter(created_by=self.request.user)
            print(share)
            context = {
                'share_list':1,
                'object': share
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")



class ShareDetailView(RetrieveAPIView):
    serializer_class = ShareSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Share.objects.get(user=self.request.user, shared=False)
            Users = User.objects.all()
            context = {
                'object': share,
                'user_list': Users
            }
            return render(self.request, 'core/shareout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        userprofile = UserProfile.objects.get(user=self.request.user)
        #token = request.data.get('stripeToken')
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=self.request.user.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.save()

        amount = int(order.get_total() * 100)

        try:

                # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=userprofile.stripe_customer_id
            )
            # charge once off on the token
            # charge = stripe.Charge.create(
            #     amount=amount,  # cents
            #     currency="usd",
            #     source=token
            # )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            # order.ref_code = create_ref_code()
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            #messages.warning(self.request, "Rate limit error")
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(
            user=self.request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)


class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    template_name = "core/checkout.html"
    def get(self,request):
        template_name = "core/beverages.html"
        Address_list = Address.objects.filter(user= request.user)
        return render(request,template_name,{'Address_list':Address_list})
    def get_queryset(self):
        address_type = self.request.query_params.get('address_type', None)
        qs = Address.objects.all()
        if address_type is None:
            return qs
        return qs.filter(user=self.request.user, address_type=address_type)

class UserProfileView(View):
    def get(self,request):
        template_name = "core/faq.html"
        return render(request,template_name)


class AddressCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    def post(self, request):
        New_address = Address.objects.create(
            user = request.user,
            street_address = request.POST["street_address"],
            state = request.POST['state'],
            pincode = request.POST['pincode'],
            address_type = request.POST['address_type']
        )
        New_address.save()
        Address_list = Address.objects.filter(user= request.user)

        return render(request, "core/beverages.html",{'address_created':1,'Address_list':Address_list})




class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Address.objects.all()


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

def QuantityUpdate(request):
    if request.method == 'POST':
        print(request.POST["dispatch"])
        if 'id' in request.POST:
            if not int(request.POST["dispatch"]):
                found_item = OrderItem.objects.get(user= request.user, item__id = request.POST["pk"],ordered=False)
            else:
                print(request.POST["item"],request.POST)
                found_item = OrderItem.objects.get(user= request.user, id= request.POST["item"],ordered=True)
            found_order = Order.objects.get(user= request.user,id=request.POST["id"])
            if "special_requirement" in request.POST:
                    found_item.special_requirement = request.POST["special_requirement"]

            if int(request.POST["quantity"]):
                found_item.quantity = int(request.POST["quantity"])
                if found_item.ordered:
                    found_order.final_price = int(found_order.final_price) - int(found_item.total_price) + int(found_item.per_piece)*int(found_item.quantity)
                    found_order.total_tax = found_order.final_price*0.05
                    found_order.total_grand = found_order.final_price*1.05
                    if request.user.userprofile.rate_type:
                        found_item.per_piece = found_item.item.price
                    found_item.total_price = int(found_item.per_piece)*found_item.quantity
                found_item.save()
                found_order.save()
            else:
                found_order.items.remove(found_item)
                found_item.quantity = 0

                found_item.delete()
                found_order.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("index")


def QuantityShareUpdate(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            found_item = SharedItem.objects.get(user= request.user,id = request.POST["item"])
            found_order = Share.objects.get(user= request.user,id=request.POST["id"])
            found_order.items.remove(found_item)
            found_item.save()
            found_order.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("index")


class GenerateShareePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        shareid = kwargs.get(
            "shareid",
            None
        )

        share = Share.objects.get(id=shareid)
        context = {
            "customer_name": request.user.username,
            "object" : share,
            "catlog" :1,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

def Sharedlist(request):
    if request.method == 'POST':
        session_key = request.session.session_key
        if "share" in request.POST:
            share = Share.objects.get(id = request.POST["share"])
            user = User.objects.get(username=request.POST["shared_user"])
            try:

                Share_list = Sharelist.objects.get(shared_user=user)
                print(Share_list)
                for item in share.items.all():
                    Share_list.share.items.add(item)
                    Share_list.share.save()
                Share_list.share.shared = True
                Share_list.share.end_date = request.POST['enddate']
                Share_list.share.save()
                Share_list.save()
                if not share.shared :
                    share.delete()
                try:
                    logged_in_user = user.logged_in_user
                except LoggedInUser.DoesNotExist:
                    logged_in_user = LoggedInUser.objects.create(user=user, session_key=session_key)

                logged_in_user.count = 0
                logged_in_user.save()
                slug = str(uuid4())[:8]
                Share_list.slug = slug
                if "phone" in request.POST:
                    if request.POST["phone"] == "":
                        Share_list.phone = 0000000000
                    else:
                        Share_list.phone = request.POST["phone"]
                else:
                    Share_list.phone = 0000000000

                Share_list.save()
                Share_list.get_absolute_url()
                Share_list.url = request.build_absolute_uri(Share_list.get_absolute_url())
                Share_list.save()
                return render(request, 'core/share_now.html',
                              {"share_link": 1, "url_for_share": Share_list, "Shared_with": Share_list.shared_user})
            except Sharelist.DoesNotExist:
                if share.shared:
                    shared_date = timezone.now()
                    new_share = Share.objects.create(
                        user=request.user, shared_date=shared_date)
                    new_share.shared = True
                    for item in share.items.all():
                        new_share.items.add(item)
                        new_share.save()
                    new_share.save()
                    new_share.end_date = request.POST['enddate']
                    new_share.save()
                    user = User.objects.get(username=request.POST["shared_user"])
                    try:
                        logged_in_user = user.logged_in_user
                    except LoggedInUser.DoesNotExist:
                        logged_in_user = LoggedInUser.objects.create(user=user, session_key=session_key)

                    logged_in_user.count = 0
                    logged_in_user.save()
                    slug = str(uuid4())[:8]
                    Share_list = Sharelist.objects.create(
                        share=new_share,
                        shared_user=user,
                        slug=slug,
                        created_by=request.user
                    )
                    if "phone" in request.POST:
                        if request.POST["phone"] == "":
                            Share_list.phone = 0000000000
                        else:
                            Share_list.phone = request.POST["phone"]
                    else:
                        Share_list.phone = 0000000000

                    Share_list.save()
                    Share_list.get_absolute_url()
                    Share_list.url = request.build_absolute_uri(Share_list.get_absolute_url())
                    Share_list.save()
                    return render(request, 'core/share_now.html',
                                  {"share_link": 1, "url_for_share": Share_list, "Shared_with": Share_list.shared_user})
                else:
                    share.shared = True
                    share.end_date = request.POST['enddate']
                    share.save()
                    user = User.objects.get(username=request.POST["shared_user"])
                    try:
                        logged_in_user = user.logged_in_user
                    except LoggedInUser.DoesNotExist:
                        logged_in_user = LoggedInUser.objects.create(user=user, session_key=session_key)

                    logged_in_user.count = 0
                    logged_in_user.save()
                    slug = str(uuid4())[:8]
                    Share_list = Sharelist.objects.create(
                        share=share,
                        shared_user=user,
                        slug=slug,
                        created_by=request.user
                    )
                    if "phone" in request.POST:
                        if request.POST["phone"] == "":
                            Share_list.phone = 0000000000
                        else:
                            Share_list.phone = request.POST["phone"]
                    else:
                        Share_list.phone = 0000000000

                    Share_list.save()
                    Share_list.get_absolute_url()
                    Share_list.url = request.build_absolute_uri(Share_list.get_absolute_url())
                    Share_list.save()
                    return render(request, 'core/share_now.html',
                                  {"share_link": 1, "url_for_share": Share_list, "Shared_with": Share_list.shared_user})
            except:
                return redirect('index')

        else:
            return redirect('index')
    else:
        return redirect('index')

def PlaceOrder(request,pk):
    if request.method =="POST" :
        if "order" in request.POST:
            order = Order.objects.get(id  = request.POST["order"])
            if 'shipping_address' in request.POST:
                if request.POST['shipping_address'] == "others":
                    print("noshippongaddress")
                    if "new_address" in request.POST:
                        print("hello")
                        if not request.POST['new_address'] == "":
                            print("https://api.postalpincode.in/pincode/"+request.POST['new_pincode_number'])
                            pincode_verifcation = requests.get("https://api.postalpincode.in/pincode/"+request.POST['new_pincode_number']).json()[0]
                            if pincode_verifcation["Status"] == "Success":
                                city = pincode_verifcation["PostOffice"][0]["District"]
                                state = pincode_verifcation["PostOffice"][0]["State"]
                                shipping_address = Address.objects.create(
                                    user = request.user,
                                    street_address = request.POST['new_address'],
                                    pincode =  request.POST['new_pincode_number'],
                                    address_type = "S",
                                    city = city,
                                    state = state,
                                    )
                            else:
                                shipping_address = Address.objects.create(
                                    user = request.user,
                                    street_address = request.POST['new_address'],
                                    pincode =  request.POST['new_pincode_number'],
                                    address_type = "S",
                                    )
                else:
                    shipping_address_id = request.POST['shipping_address']
                    shipping_address = Address.objects.get(id=shipping_address_id)
            if 'gst_number' in request.POST:
                if request.POST['gst_number'] == "others":
                    print("gst_number")
                    if "new_gst_number" in request.POST:
                        if not  request.POST['new_gst_number'] == "":
                            if not request.POST['new_gst_number'] == "URP":
                                gst_number = GST_Numbers.objects.create(
                                    user = request.user,
                                    number = request.POST['new_gst_number']
                                    )
                            else:
                                gst_number, created = GST_Numbers.objects.get_or_create(
                                    number = "URP",
                                    user=request.user,
                                )
                else:
                    gst_nmuber_id = request.POST['gst_number']
                    gst_number = GST_Numbers.objects.get(id=gst_nmuber_id)

            if 'phone_number' in request.POST:
                if request.POST['phone_number'] == "others":
                    print("phone_number")
                    if "new_phone_number" in request.POST:
                        if not request.POST['new_phone_number']  == "":
                            phone_number = Phone_Number.objects.create(
                                user = request.user,
                                number = request.POST['new_phone_number'],
                                )

                else:
                    phone_nmuber_id = request.POST['phone_number']
                    phone_number = Phone_Number.objects.get(id=phone_nmuber_id)


            if not order.ordered:
                for order_item in  order.items.all():
                    order_item.ordered = True
                    if not request.user.userprofile.rate_type:
                        order_item.per_piece = order_item.item.price
                    else:
                        order_item.per_piece = order_item.item.boxprice
                    order_item.total_price = order_item.get_total_item_price()
                    order_item.save()



                if request.POST['shipping_address'] != "others" or request.POST['new_address'] is not None :
                    order.shipping_address = shipping_address
                elif len(Address.objects.filer(user=request.user)):
                    order.shipping_address = Address.objects.filer(user=request.user)[0]

                if request.POST['gst_number'] != "others" or request.POST['new_gst_number'] is not None :
                    order.gst = gst_number.number
                elif len(GST_Numbers.objects.filer(user=request.user)):
                    order.shipping_address = GST_Numbers.objects.filer(user=request.user)[0]


                if request.POST['phone_number'] != "others" or request.POST['new_phone_number'] is not None :
                    order.phone = phone_number.number
                elif len(Phone_Number.objects.filer(user=request.user)):
                    order.shipping_address = Phone_Number.objects.filer(user=request.user)[0]

                order.ordered_date = datetime.date.today()
                order.ordered = True
                order.final_price = order.get_total()
                order.total_tax = order.get_total_tax()
                order.total_grand = order.get_total_grand()
                order.save()
                return render( request, 'core/share_now.html',{"order_placed" : 1,"object":order})
            else:
                return redirect('index')


    else:
        return redirect('index')

def ProductStock(request, *args, **kwargs):
    if request.method =="GET" :
        pk = kwargs.get("pk",None)
        item = Item.objects.get(id=pk)
        item.stock = False
        item.save()
        return redirect(request.META['HTTP_REFERER'])
    elif request.method == "POST":
        print(request.POST)
        item = Item.objects.get(id = request.POST["pk"])
        item.stock = False
        item.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('index')


def DispatchOrder(request,pk):
    if request.method =="GET" :
        order = Order.objects.get(id=pk)
        return render( request, 'core/checkout.html',{'dispatch_final':1,"object":order})
    else:
        return redirect('index')


class SharedlistDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Share.objects.get(user=self.request.user, shared=False)
            context = {
                'object': share
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")




class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        orderid = kwargs.get(
            "orderid",
            None
        )
        order = Order.objects.get(id=orderid)
        if "bill_no" in  request.GET:
            bill_no = request.GET["bill_no"]
            order.Bill_no = bill_no
            order.dispatched_date = datetime.date.today()
            order.dispatched = True
            order.save()
        if "Transport" in request.GET:
            transport_id = request.GET['Transport']
            try:
                transport = Transport.objects.get(id=transport_id)
                order.transport = transport
                order.dispatched_date = datetime.date.today()
                order.dispatched = True
                order.save()
            except:
                pass


        context = {
            "customer_name": request.user.username,
            "amount": order.get_total(),
            "dispatch_challan":1,
            "object" : order,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    def post(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        orderid = kwargs.get(
            "orderid",
            None
        )
        order = Order.objects.get(id=orderid)
        if "bill_no" in  request.POST:
            bill_no = request.POST["bill_no"]
            order.Bill_no = bill_no
            order.dispatched_date = datetime.date.today()
            order.dispatched = True
            if request.method == 'POST' or request.FILES['uploadFromPC']:
                try:
                    myfile = request.FILES['uploadFromPC']
                    fs = FileSystemStorage()
                    filename = settings.MEDIA_ROOT +"/"+ fs.save(myfile.name, myfile)
                    order.lr = myfile
                except:
                    pass
            order.save()
        if "Transport" in request.POST:
            transport_id = request.POST['Transport']
            try:
                transport = Transport.objects.get(id=transport_id)
                order.transport = transport
                order.dispatched_date = datetime.date.today()
                order.dispatched = True
                order.save()
            except:
                pass


        context = {
            "customer_name": request.user.username,
            "amount": order.get_total(),
            "dispatch_challan":1,
            "object" : order,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GenerateInvoicePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        orderid = kwargs.get(
            "orderid",
            None
        )

        order = Order.objects.get(id=orderid)
        order.save()
        context = {
            "customer_name": request.user.username,
            "amount": order.get_total(),
            "object" : order,
            "invoice": 1,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")




def Categorypage(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.method == 'GET':
            category_id = kwargs.get(
                "categoryid",
                None
            )
            category = Category.objects.get(id = category_id)
            if request.user.userprofile.owner or request.user.userprofile.one_click_purchasing:
                csrf_token = django.middleware.csrf.get_token(request)
                query = Q(stock = True)
                query.add(Q(category = category), Q.AND)
                query.add(Q(category__parent = category), Q.OR,)
                query.add(Q(category__parent__parent = category), Q.OR,)
                queryset = Item.objects.filter(query)
                page = request.GET.get('page', 1)
                paginator = Paginator(queryset, 20)
                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)

                first_index = users.number - 5
                last_index = users.number + 5
                return render(request,"core/products.html",{"object_list":users,"category_page":category,
                "csrf_token": csrf_token ,'min':first_index,'max':last_index })
            else:
                try:
                    csrf_token = django.middleware.csrf.get_token(request)
                    queryset = Sharelist.objects.get(shared_user=request.user)
                    items = []
                    final_items = []
                    date_today = datetime.date.today()
                    if queryset.share.end_date >= datetime.datetime(year=int(date_today.year), month=int(date_today.month),day=int(date_today.day),tzinfo=pytz.UTC) and queryset.share.shared:
                        final_items = queryset.share.items.all()

                    for item in final_items:
                        if item.item.stock and item.item not in items and (item.item.category == category or item.item.category.parent == category or item.item.category.parent.parent == category)  :
                            items.append(item.item)
                            print(item.item)
                    print(items)
                    if len(items):
                        page = request.GET.get('page', 1)
                        paginator = Paginator(list(set(items)), 20)
                        try:
                            users = paginator.page(page)
                        except PageNotAnInteger:
                            users = paginator.page(1)
                        except EmptyPage:
                            users = paginator.page(paginator.num_pages)

                        first_index = users.number - 5
                        last_index = users.number + 5

                        return render(request,"core/products.html",{"object_list":users,"category_page":category,
                        "csrf_token": csrf_token , 'min':first_index,'max':last_index })
                    else:
                        users=[]
                        return render(request,"core/products.html",{"object_list":users,"category_page":category,
                        "csrf_token": csrf_token})
                except Sharelist.DoesNotExist:
                     return redirect('product-list')

    else:
        return redirect('index')
def Checkoutpage(request, *args, **kwargs):
    try:
        if request.method == 'GET':
            order_id = kwargs.get(
                "orderid",
                None
            )
            order = Order.objects.get(id = order_id)
            if request.user.is_authenticated:
                csrf_token = django.middleware.csrf.get_token(request)
                return render(request,"core/order_checkout.html",
                {"csrf_token": csrf_token ,
                "order_checkout": 1,
                "object" : order,
                })
    except Order.DoesNotExist:
        return redirect('index')

def shareoutpage(request, *args, **kwargs):
    try:
        if request.method == 'GET':
            share_id = kwargs.get(
                "shareid",
                None
            )
            users = User.objects.all()
            share = Share.objects.get(id = share_id)
            if request.user.is_authenticated:
                csrf_token = django.middleware.csrf.get_token(request)
                return render(request,"core/order_checkout.html",
                {"csrf_token": csrf_token ,
                "share_checkout":1,
                "object" : share,
                "user_list": users
                })
    except Share.DoesNotExist:
        return redirect('index')



def search(request):
    if request.method == "POST":
        query = request.POST["search"]
        query_list = query.split()
        search_list = []
        csrf_token = django.middleware.csrf.get_token(request)
        if request.user.userprofile.owner or request.user.userprofile.one_click_purchasing:
            Item_qs = Item.objects.filter(stock= True)
        else:
            queryset = Sharelist.objects.filter(shared_user = request.user,share__shared = True,share__items__item__stock= True)
            Item_qs = queryset
        try:
            if request.user.userprofile.owner or request.user.userprofile.one_click_purchasing :
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(title__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(description__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(category__name__icontains=q)))
                if len(search_list):
                    return render(request,"core/products.html",{"object_list":search_list, "csrf_token": csrf_token})
                return render(request,"core/products.html",{"object_list":0,"No_search_found":1,"csrf_token": csrf_token})


            else:
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(title__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(description__icontains=q)))

                if len(search_list):
                    items=[]
                    for my_sharelist in search_list:
                        for my_share_item in my_sharelist.share.items.all():
                            if my_share_item.item.stock:
                                items.append(my_share_item.item)
                    return render(request,"core/products.html",{"object_list":items, "csrf_token": csrf_token})
                return render(request,"core/products.html",{"object_list":0,"No_search_found":1,"csrf_token": csrf_token})


        except Exception as e:
            print(str(e))
            return redirect('index')
    else:
        return redirect('index')

def delete_cart(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            print(request.POST)
            found_order = Order.objects.get(id=request.POST["id"])
            for item in found_order.items.all():
                item.delete()
            found_order.delete()
            return redirect('index')
        print(request.POST)
        return redirect('index')



def New_address(request):
    return render(request, "core/beverages.html",{'form':AddressForm,'create_new':1})

def Category_Price(request):
    if request.method == "GET":
        return render(request,"core/categoryprice.html")

    if request.method == "POST":
        try:
            if request.user.userprofile.owner:
                category_id = int(request.POST['Category'])
                items_list =  Item.objects.filter(category__id = category_id)
                for item in items_list:
                    if int(request.POST["Price_type"]):
                        item.boxprice = int(request.POST["price"])
                        item.save()
                    else:
                        item.price = int(request.POST["price"])
                        item.save()

            return render(request,"core/categoryprice.html",{"category_price_changed":1})
        except:
            return redirect("index")

def resize(photo):
    im = Image.open(photo)
    f, e = os.path.splitext(photo)
    rgb_im = im.convert('RGB')
    if not "".join(e[1:]) == "jp2":
        rgb_im.save(photo.replace("".join(e[1:]), "jp2"), quality=95)


def change_extensions(request):
    if request.method == "GET":
        for item in Item.objects.all():
            resize("/home/prince603/suratsaree/media/" + str(item.image.url))




def lr_upload(request,order_id):
    if request.method == "GET":
        try:
            order = Order.objects.get(id= order_id)
            return render(request,"core/categoryprice.html",{"Lr_Upload":1,"object":order})
        except:
            return redirect("index")

    if request.method == 'POST' and request.FILES['uploadFromPC']:
        order = Order.objects.get(id= order_id)
        try:
            myfile = request.FILES['uploadFromPC']
            fs = FileSystemStorage()
            filename = settings.MEDIA_ROOT +"/"+ fs.save(myfile.name, myfile)
            order.lr = myfile
            order.save()
        except Exception as e:
            print(str(e))
            success = 0
            pass
        order.save()
        if "Transport" in request.POST:
            transport_id = request.POST['Transport']
            try:
                transport = Transport.objects.get(id=transport_id)
                order.transport = transport
                order.dispatched_date = datetime.date.today()
                order.dispatched = True
                order.save()
            except:
                success = 0
                pass

        return redirect('order-list')



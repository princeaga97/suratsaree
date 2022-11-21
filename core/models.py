from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
import requests



class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self',blank=True, null=True ,related_name='children',on_delete= models.CASCADE)

    class Meta:
        #enforcing that there can not be two categories under a parent with same slug

        # __str__ method elaborated later in post.  use __unicode__ in place of

        # __str__ if you are using python 2

        unique_together = ('slug', 'parent',)
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

Rate_Choices = (
    (0,'Regular Rate'),
    (1,'Box Rate'),
)
STATE_CHOICES = (("Andhra Pradesh","Andhra Pradesh"),("Arunachal Pradesh ","Arunachal Pradesh "),("Assam","Assam"),("Bihar","Bihar"),("Chhattisgarh","Chhattisgarh"),("Goa","Goa"),("Gujarat","Gujarat"),("Haryana","Haryana"),("Himachal Pradesh","Himachal Pradesh"),("Jammu and Kashmir ","Jammu and Kashmir "),("Jharkhand","Jharkhand"),("Karnataka","Karnataka"),("Kerala","Kerala"),("Madhya Pradesh","Madhya Pradesh"),("Maharashtra","Maharashtra"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),("Punjab","Punjab"),("Rajasthan","Rajasthan"),("Sikkim","Sikkim"),("Tamil Nadu","Tamil Nadu"),("Telangana","Telangana"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),("Uttarakhand","Uttarakhand"),("West Bengal","West Bengal"),("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),("Chandigarh","Chandigarh"),("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),("Daman and Diu","Daman and Diu"),("Lakshadweep","Lakshadweep"),("National Capital Territory of Delhi","National Capital Territory of Delhi"),("Puducherry","Puducherry"))
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    owner = models.BooleanField(default= False)
    show_rate = models.BooleanField(default= True)
    rate_type = models.IntegerField(choices=Rate_Choices,blank=True)
    valid_till = models.DateField(null=True,blank=True)
    one_click_purchasing = models.BooleanField(default=False)
    full_access = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    set = models.IntegerField()
    price = models.FloatField()
    boxprice = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey('Category', null=True, blank=True,on_delete= models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1,blank=True,)
    slug = models.SlugField()
    stock = models.BooleanField(default=True)
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={
            'pk': self.pk
        })

    def get_add_to_cart_url(self):
        print(self.title)
        return reverse("add-to-cart", kwargs={
            'pk': self.pk
        })
    def get_add_to_share_url(self):
        print(self.title)
        return reverse("add-to-share", kwargs={
            'pk': self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'pk': self.pk
        })
    def out_of_stock(self):
        return reverse("out-of-stock", kwargs={
            'pk': self.pk,
        })

class Image_url(models.Model):
    item = models.ForeignKey(Item, related_name="image_url", on_delete=models.CASCADE, default=1)
    image = models.URLField()

    def __str__(self):
        return self.item.title

    def image_confirm(self):
        if requests.get(self.image).status_code == 200:
            return True
        else:
            return False



class Item_Images(models.Model):
    item = models.ForeignKey(Item , related_name="item_images" , on_delete=models.CASCADE , default=1 )
    image = models.ImageField()
    def __str__(self):
       return self.item.title

class Variation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # size

    class Meta:
        unique_together = (
            ('item', 'name')
        )

    def __str__(self):
        return self.name


class ItemVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # S, M, L
    attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )

    def __str__(self):
        return self.value


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_variations = models.ManyToManyField(ItemVariation)
    special_requirement = models.CharField(max_length=500,null = True, blank=True)
    quantity = models.IntegerField(default=1)
    per_piece = models.FloatField(null = True,blank=True)
    total_price = models.FloatField(null = True,blank=True)



    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        if not  self.user.userprofile.rate_type:
            return self.quantity * self.item.price
        else:
            return self.quantity * self.item.boxprice

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        return self.get_total_item_price()


class SharedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    shared = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_variations = models.ManyToManyField(ItemVariation)

    def __str__(self):
        return self.item.title


class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(SharedItem)
    start_date = models.DateTimeField(auto_now_add=True)
    shared_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    shared = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def description(self):
        out = " "
        for item in self.items.all():
            out = out + "  *"+item.item.title+"*  \n"
        print(out)
        return out


class Transport(models.Model):
    name= models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    city = models.CharField(max_length=100,null=True, blank=True)
    state = models.CharField(choices=STATE_CHOICES,max_length=255, null=True, blank=True)
    gst = models.CharField(max_length=100)
    rating = models.FloatField(null = True,blank=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    dispatched_date = models.DateTimeField(blank = True,null= True)
    Bill_no = models.CharField(max_length=20, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    dispatched = models.BooleanField(default=False)
    transport = models.ForeignKey(Transport,
                             on_delete=models.CASCADE,null = True, blank= True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    final_price = models.FloatField(null = True,blank=True)
    total_tax = models.FloatField(null = True,blank=True)
    total_grand = models.FloatField(null = True,blank=True)
    gst = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    lr = models.ImageField(default=None)
    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    '''

    def __str__(self):
        return self.user.username

    def dispatched_url(self):
        return reverse("dispatch-order", kwargs={
            'pk': self.pk
        })
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

    def get_total_tax(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total*0.05

    def get_total_grand(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total*1.05

    def get_total_saved(self):
        total = 0
        for order_item in self.items.all():
            total = total +  order_item.get_total_item_price() - order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total






class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.TextField(max_length=5000)
    city = models.CharField(max_length=100)
    state = models.CharField(choices=STATE_CHOICES,max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'



class GST_Numbers(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    number = models.CharField(max_length=100)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name_plural = 'GSTNumbers'


class Phone_Number(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    number = models.CharField(max_length=100)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name_plural = 'phonenumbers'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class Sharelist(models.Model):
    share = models.ForeignKey(to = Share , on_delete= models.CASCADE , blank = True, null = True)
    slug = models.SlugField(max_length=8,default="12345678", unique = True)
    url = models.URLField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="Created_by")
    shared_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="shared_to")
    timestamp = models.DateTimeField(auto_now_add=True)
    phone = models.IntegerField(blank = True, null = True)
    def __str__(self):
        return self.shared_user.username

    def get_absolute_url(self):
        return reverse("share_list_url-detail", kwargs={
            'slug': self.slug
        })








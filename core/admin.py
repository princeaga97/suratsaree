from django.contrib import admin

from .models import (
    Item, OrderItem, Order, Payment, Coupon, Refund,
    Address, UserProfile, Variation, ItemVariation ,Category,
    SharedItem, Share, Sharelist, Item_Images , Transport ,Image_url, GST_Numbers, Phone_Number
)


class PropertyImageInline(admin.TabularInline):
    model = Item_Images
    extra = 3
class PropertyImageURLInline(admin.TabularInline):
    model = Image_url
    extra = 3


def InStock(modeladmin, request, queryset):
    queryset.update(stock = True)

def OutofStock(modeladmin, request, queryset):
    queryset.update(stock = False)


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'dispatched',
                    'shipping_address',
                    'billing_address',
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
    ]
    list_filter = ['ordered',
                   'dispatched',
                   'user',
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'city',
        'pincode',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type']
    search_fields = ['user', 'street_address', 'city', 'pincode']


class ItemVariationAdmin(admin.ModelAdmin):
    list_display = ['variation',
                    'value',
                    'attachment']
    list_filter = ['variation', 'variation__item']
    search_fields = ['value']

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ['stock','category__name']
    inlines = [ PropertyImageInline,PropertyImageURLInline ]
    actions = [InStock,OutofStock]


class ItemVariationInLineAdmin(admin.TabularInline):
    model = ItemVariation
    extra = 1


class VariationAdmin(admin.ModelAdmin):
    list_display = ['item',
                    'name']
    list_filter = ['item']
    search_fields = ['name']
    inlines = [ItemVariationInLineAdmin]

class UserAdmin(admin.ModelAdmin):
    list_display = ['user','owner','one_click_purchasing','show_rate','rate_type']
    list_filter = ['rate_type']

class GSTAdmin(admin.ModelAdmin):
    list_filter = ['user']

admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(SharedItem)
admin.site.register(Share)
admin.site.register(GST_Numbers,GSTAdmin)
admin.site.register(Phone_Number,GSTAdmin)
admin.site.register(Sharelist)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Category)
admin.site.register(Transport)


""" admin.site.register(ItemVariation, ItemVariationAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund) """


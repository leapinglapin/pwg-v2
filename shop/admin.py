from django.contrib import admin

# Register your models here.

from .models import *


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name', 'barcode']


admin.site.register(Product, ProductAdmin)
admin.site.register(Publisher)
admin.site.register(Category)
admin.site.register(Partner)
admin.site.register(CardCondition)

admin.site.register(InventoryItem)
admin.site.register(MadeToOrder)
# admin.site.register(ComicItem)
# admin.site.register(CardItem)
admin.site.register(UsedItem)

admin.site.register(ProductImage)

from django.contrib import admin

# Register your models here.
from events.models import *

admin.site.register(Event)
admin.site.register(EventTicketItem)

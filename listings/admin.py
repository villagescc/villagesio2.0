from django.contrib import admin

# Register your models here.
from listings.models import Listings


class ListingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'description')
    search_fields = ('user__username', 'title', 'description')


admin.site.register(Listings, ListingsAdmin)
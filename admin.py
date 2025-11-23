from django.contrib import admin
from .models import Property

# This decorator makes the admin interface look professional
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_in_billions', 'location_district', 'area_sqm', 'is_legal_clear')
    list_filter = ('location_district', 'is_legal_clear')
    search_fields = ('title', 'location_district')
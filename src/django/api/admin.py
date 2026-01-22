from django.contrib import admin
from .models import Restaurant, MenuItem, DataFlag


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'item_count', 'last_updated']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'calories', 'protein', 'carbs', 'fat', 'density_label', 'is_available']
    list_filter = ['restaurant', 'category', 'is_available']
    search_fields = ['name', 'restaurant__name']


@admin.register(DataFlag)
class DataFlagAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']

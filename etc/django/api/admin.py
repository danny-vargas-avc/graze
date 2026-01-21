"""
Django admin configuration for Graze.
"""
from django.contrib import admin
from .models import Restaurant, MenuItem, DataFlag, WaitlistEntry


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'item_count', 'last_updated']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['item_count', 'created_at']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'restaurant', 'category', 'calories', 'protein',
        'carbs', 'fat', 'density_label_display', 'is_available'
    ]
    list_filter = ['restaurant', 'category', 'is_available', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'restaurant__name']
    list_editable = ['is_available']
    readonly_fields = ['protein_per_100cal_display', 'density_label_display', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('restaurant', 'name', 'category', 'serving_size')
        }),
        ('Core Macros', {
            'fields': ('calories', 'protein', 'carbs', 'fat')
        }),
        ('Extended Nutrition', {
            'fields': ('fiber', 'sodium', 'sugar', 'saturated_fat'),
            'classes': ('collapse',)
        }),
        ('Calculated', {
            'fields': ('protein_per_100cal_display', 'density_label_display'),
        }),
        ('Dietary', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'allergens', 'tags'),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_available', 'seasonal_note')
        }),
        ('Tracking', {
            'fields': ('popularity_score', 'source_url', 'last_verified', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def protein_per_100cal_display(self, obj):
        return f"{obj.protein_per_100cal}g"
    protein_per_100cal_display.short_description = 'Protein/100cal'

    def density_label_display(self, obj):
        return obj.density_label.title()
    density_label_display.short_description = 'Density'


@admin.register(DataFlag)
class DataFlagAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']
    search_fields = ['menu_item__name', 'user_comment']
    list_editable = ['resolved']
    readonly_fields = ['user_ip', 'created_at']


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ['email', 'source', 'created_at']
    list_filter = ['source']
    search_fields = ['email']
    readonly_fields = ['created_at']

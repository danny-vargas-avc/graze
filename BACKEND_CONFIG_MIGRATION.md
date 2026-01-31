# Backend Configuration Migration Plan

**Goal**: Move all hardcoded frontend configuration to Django admin for easy CMS management.

## 📊 Overview

This migration moves the following from frontend code to backend CMS:
- Filter options (calories, protein, carbs, fat ranges)
- Quick filter presets
- Sort options
- Restaurant brand colors
- Map defaults (center, zoom)
- Pagination settings
- Radius options

**Benefits**:
- ✅ No frontend redeployment needed to change filters
- ✅ Business team can manage configurations
- ✅ A/B test different filter ranges easily
- ✅ Consistent configuration across frontend/mobile
- ✅ Audit trail of configuration changes

---

## 🏗️ Implementation Phases

### **Phase 1: Backend Foundation** (Tasks #1-4)

#### Task #1: Create Django Models
```python
# backend/apps/config/models.py

from django.db import models

class FilterConfiguration(models.Model):
    """Nutrition macro filter ranges"""

    FILTER_TYPES = [
        ('range', 'Range (min/max)'),
        ('max_only', 'Max Only'),
    ]

    name = models.CharField(max_length=50, unique=True)  # 'calories', 'protein'
    display_name = models.CharField(max_length=100)  # 'Calories'
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPES)
    unit = models.CharField(max_length=10, blank=True)  # 'g', 'mg', ''
    options = models.JSONField(
        help_text='Array of options: [{"label": "0-300", "min": 0, "max": 300}, ...]'
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name


class QuickFilter(models.Model):
    """Quick filter presets like 'High Protein 40g+'"""

    id_key = models.SlugField(unique=True)  # 'high-protein'
    label = models.CharField(max_length=100)  # 'High Protein 40g+'
    filter_params = models.JSONField(
        help_text='Filter parameters: {"protein_min": 40, "sort": "protein_desc"}'
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    requires_location = models.BooleanField(
        default=False,
        help_text='If true, only shown when user has location enabled'
    )

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class SortOption(models.Model):
    """Sort dropdown options"""

    value = models.CharField(max_length=50, unique=True)  # 'protein_desc'
    label = models.CharField(max_length=100)  # 'Highest Protein'
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    requires_location = models.BooleanField(
        default=False,
        help_text='If true, only shown when user has location (e.g., distance_asc)'
    )

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class AppConfiguration(models.Model):
    """Singleton for app-wide settings"""

    # Map defaults
    default_map_center_lng = models.FloatField(
        default=-74.0060,
        help_text='Default map longitude (NYC: -74.0060)'
    )
    default_map_center_lat = models.FloatField(
        default=40.7128,
        help_text='Default map latitude (NYC: 40.7128)'
    )
    default_map_zoom = models.IntegerField(
        default=12,
        help_text='Default map zoom level (1-20)'
    )

    # Pagination
    items_per_page = models.IntegerField(
        default=20,
        help_text='Number of dishes to load per page'
    )

    # Radius options
    radius_options = models.JSONField(
        default=list,
        help_text='Available radius options in miles: [5, 10, 25, 50]'
    )

    # Default sort
    default_sort = models.CharField(
        max_length=50,
        default='protein_ratio_desc',
        help_text='Default sort order for dishes'
    )

    # Feature flags
    enable_geolocation = models.BooleanField(
        default=True,
        help_text='Enable geolocation features'
    )
    enable_distance_sort = models.BooleanField(
        default=True,
        help_text='Enable distance-based sorting'
    )

    # Cache control
    config_version = models.IntegerField(
        default=1,
        help_text='Increment to force frontend cache refresh'
    )

    class Meta:
        verbose_name = 'App Configuration'
        verbose_name_plural = 'App Configuration'

    def save(self, *args, **kwargs):
        # Ensure singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'App Configuration'


# Add to existing Restaurant model
class Restaurant(models.Model):
    # ... existing fields ...
    brand_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Brand color in hex format (e.g., #A81612)'
    )
```

#### Task #2: Django Admin Setup
```python
# backend/apps/config/admin.py

from django.contrib import admin
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration

@admin.register(FilterConfiguration)
class FilterConfigurationAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'filter_type', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['filter_type', 'is_active']
    search_fields = ['name', 'display_name']

    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'filter_type', 'unit', 'is_active')
        }),
        ('Options', {
            'fields': ('options',),
            'description': 'JSON format: [{"label": "0-300", "min": 0, "max": 300}, ...]'
        }),
        ('Display', {
            'fields': ('order',),
        }),
    )


@admin.register(QuickFilter)
class QuickFilterAdmin(admin.ModelAdmin):
    list_display = ['label', 'id_key', 'order', 'requires_location', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['requires_location', 'is_active']
    search_fields = ['label', 'id_key']
    prepopulated_fields = {'id_key': ('label',)}

    fieldsets = (
        (None, {
            'fields': ('id_key', 'label', 'is_active')
        }),
        ('Filter Parameters', {
            'fields': ('filter_params',),
            'description': 'JSON format: {"protein_min": 40, "calories_max": 500}'
        }),
        ('Settings', {
            'fields': ('requires_location', 'order'),
        }),
    )


@admin.register(SortOption)
class SortOptionAdmin(admin.ModelAdmin):
    list_display = ['label', 'value', 'order', 'requires_location', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['requires_location', 'is_active']
    search_fields = ['label', 'value']


@admin.register(AppConfiguration)
class AppConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Singleton pattern - only one instance
        return not AppConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Cannot delete singleton
        return False

    fieldsets = (
        ('Map Defaults', {
            'fields': ('default_map_center_lng', 'default_map_center_lat', 'default_map_zoom'),
        }),
        ('Pagination', {
            'fields': ('items_per_page',),
        }),
        ('Filters', {
            'fields': ('radius_options', 'default_sort'),
        }),
        ('Features', {
            'fields': ('enable_geolocation', 'enable_distance_sort'),
        }),
        ('Cache Control', {
            'fields': ('config_version',),
            'description': 'Increment version to force frontend to refresh cached config'
        }),
    )
```

#### Task #3: API Endpoints
```python
# backend/apps/config/serializers.py

from rest_framework import serializers
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration

class FilterConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterConfiguration
        fields = ['name', 'display_name', 'filter_type', 'unit', 'options', 'order']


class QuickFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickFilter
        fields = ['id_key', 'label', 'filter_params', 'requires_location', 'order']


class SortOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortOption
        fields = ['value', 'label', 'requires_location', 'order']


class AppConfigurationSerializer(serializers.ModelSerializer):
    default_map_center = serializers.SerializerMethodField()

    class Meta:
        model = AppConfiguration
        fields = [
            'default_map_center',
            'default_map_zoom',
            'items_per_page',
            'radius_options',
            'default_sort',
            'enable_geolocation',
            'enable_distance_sort',
            'config_version'
        ]

    def get_default_map_center(self, obj):
        return [obj.default_map_center_lng, obj.default_map_center_lat]


# backend/apps/config/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration
from .serializers import (
    FilterConfigurationSerializer,
    QuickFilterSerializer,
    SortOptionSerializer,
    AppConfigurationSerializer
)

class ConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Combined config endpoint for all app configuration
    """

    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all configuration in one request"""
        filters = FilterConfiguration.objects.filter(is_active=True)
        quick_filters = QuickFilter.objects.filter(is_active=True)
        sort_options = SortOption.objects.filter(is_active=True)
        app_config = AppConfiguration.get_config()

        return Response({
            'filters': FilterConfigurationSerializer(filters, many=True).data,
            'quick_filters': QuickFilterSerializer(quick_filters, many=True).data,
            'sort_options': SortOptionSerializer(sort_options, many=True).data,
            'app_settings': AppConfigurationSerializer(app_config).data,
            'version': app_config.config_version
        })


# backend/apps/config/urls.py

from django.urls import path
from .views import ConfigViewSet

urlpatterns = [
    path('all/', ConfigViewSet.as_view({'get': 'all'}), name='config-all'),
]
```

#### Task #4: Seed Initial Data
```python
# backend/apps/config/management/commands/seed_config.py

from django.core.management.base import BaseCommand
from apps.config.models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration

class Command(BaseCommand):
    help = 'Seed initial configuration data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding configuration data...')

        # Filter Configurations
        FilterConfiguration.objects.get_or_create(
            name='calories',
            defaults={
                'display_name': 'Calories',
                'filter_type': 'range',
                'unit': '',
                'options': [
                    {'label': 'Any', 'min': None, 'max': None},
                    {'label': '0-300', 'min': 0, 'max': 300},
                    {'label': '300-500', 'min': 300, 'max': 500},
                    {'label': '500-700', 'min': 500, 'max': 700},
                    {'label': '700+', 'min': 700, 'max': None},
                ],
                'order': 1
            }
        )

        FilterConfiguration.objects.get_or_create(
            name='protein',
            defaults={
                'display_name': 'Protein',
                'filter_type': 'range',
                'unit': 'g',
                'options': [
                    {'label': 'Any', 'min': None, 'max': None},
                    {'label': '0-20g', 'min': 0, 'max': 20},
                    {'label': '20-40g', 'min': 20, 'max': 40},
                    {'label': '40-60g', 'min': 40, 'max': 60},
                    {'label': '60g+', 'min': 60, 'max': None},
                ],
                'order': 2
            }
        )

        FilterConfiguration.objects.get_or_create(
            name='carbs',
            defaults={
                'display_name': 'Carbs',
                'filter_type': 'max_only',
                'unit': 'g',
                'options': [
                    {'label': 'Any', 'min': None, 'max': None},
                    {'label': '0-30g', 'min': None, 'max': 30},
                    {'label': '30-60g', 'min': None, 'max': 60},
                    {'label': '60-100g', 'min': None, 'max': 100},
                    {'label': '100g+', 'min': None, 'max': None},
                ],
                'order': 3
            }
        )

        FilterConfiguration.objects.get_or_create(
            name='fat',
            defaults={
                'display_name': 'Fat',
                'filter_type': 'range',
                'unit': 'g',
                'options': [
                    {'label': 'Any', 'min': None, 'max': None},
                    {'label': '0-15g', 'min': 0, 'max': 15},
                    {'label': '15-30g', 'min': 15, 'max': 30},
                    {'label': '30-50g', 'min': 30, 'max': 50},
                    {'label': '50g+', 'min': 50, 'max': None},
                ],
                'order': 4
            }
        )

        # Quick Filters
        QuickFilter.objects.get_or_create(
            id_key='high-protein',
            defaults={
                'label': 'High Protein 40g+',
                'filter_params': {'protein_min': 40},
                'order': 1
            }
        )

        QuickFilter.objects.get_or_create(
            id_key='under-500',
            defaults={
                'label': 'Under 500 cal',
                'filter_params': {'calories_max': 500},
                'order': 2
            }
        )

        QuickFilter.objects.get_or_create(
            id_key='best-ratio',
            defaults={
                'label': 'Best Ratio',
                'filter_params': {'sort': 'protein_ratio_desc'},
                'order': 3
            }
        )

        QuickFilter.objects.get_or_create(
            id_key='low-carb',
            defaults={
                'label': 'Low Carb',
                'filter_params': {'carbs_max': 30},
                'order': 4
            }
        )

        QuickFilter.objects.get_or_create(
            id_key='nearby-5mi',
            defaults={
                'label': 'Nearby 5 mi',
                'filter_params': {'radius': 5, 'sort': 'distance_asc'},
                'requires_location': True,
                'order': 0
            }
        )

        # Sort Options
        sort_options = [
            ('protein_ratio_desc', 'Best Protein/Cal', 1, False),
            ('protein_desc', 'Highest Protein', 2, False),
            ('protein_asc', 'Lowest Protein', 3, False),
            ('calories_asc', 'Lowest Calories', 4, False),
            ('calories_desc', 'Highest Calories', 5, False),
            ('carbs_asc', 'Lowest Carbs', 6, False),
            ('fat_desc', 'Highest Fat', 7, False),
            ('fat_asc', 'Lowest Fat', 8, False),
            ('alpha_asc', 'A-Z', 9, False),
            ('distance_asc', 'Nearest', 0, True),
        ]

        for value, label, order, requires_location in sort_options:
            SortOption.objects.get_or_create(
                value=value,
                defaults={
                    'label': label,
                    'order': order,
                    'requires_location': requires_location
                }
            )

        # App Configuration
        config = AppConfiguration.get_config()
        config.radius_options = [5, 10, 25, 50]
        config.save()

        self.stdout.write(self.style.SUCCESS('Configuration seeded successfully!'))
```

---

### **Phase 2: Frontend Integration** (Tasks #5-12)

#### Task #5: Create Config Store
```javascript
// src/graze/src/stores/config.js

import { defineStore } from 'pinia'
import axios from 'axios'

const CACHE_KEY = 'graze_config'
const CACHE_TTL = 24 * 60 * 60 * 1000 // 24 hours
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useConfigStore = defineStore('config', {
  state: () => ({
    filters: [],
    quickFilters: [],
    sortOptions: [],
    appSettings: null,
    version: null,
    loading: false,
    error: null,
    lastFetched: null,
  }),

  getters: {
    getFilterOptions: (state) => (filterName) => {
      const filter = state.filters.find(f => f.name === filterName)
      return filter?.options || []
    },

    restaurantColors: (state) => {
      // Will be populated from restaurants API
      return {}
    },

    isConfigLoaded: (state) => {
      return state.appSettings !== null
    },

    needsRefresh: (state) => {
      if (!state.lastFetched) return true
      const elapsed = Date.now() - state.lastFetched
      return elapsed > CACHE_TTL
    },
  },

  actions: {
    async fetchConfig(force = false) {
      // Check cache first
      if (!force && this.isConfigLoaded && !this.needsRefresh) {
        return
      }

      // Try loading from localStorage
      if (!force) {
        const cached = this.loadFromCache()
        if (cached) {
          return
        }
      }

      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`${API_URL}/api/config/all/`)
        const data = response.data

        this.filters = data.filters
        this.quickFilters = data.quick_filters
        this.sortOptions = data.sort_options
        this.appSettings = data.app_settings
        this.version = data.version
        this.lastFetched = Date.now()

        // Save to cache
        this.saveToCache()
      } catch (error) {
        this.error = error
        console.error('Failed to fetch config:', error)

        // Try to use cached data as fallback
        const cached = this.loadFromCache()
        if (!cached) {
          // Use hardcoded fallbacks as last resort
          this.useFallbacks()
        }
      } finally {
        this.loading = false
      }
    },

    saveToCache() {
      const cache = {
        filters: this.filters,
        quickFilters: this.quickFilters,
        sortOptions: this.sortOptions,
        appSettings: this.appSettings,
        version: this.version,
        lastFetched: this.lastFetched,
      }
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
    },

    loadFromCache() {
      try {
        const cached = localStorage.getItem(CACHE_KEY)
        if (!cached) return false

        const data = JSON.parse(cached)

        // Check if cache is still valid
        const elapsed = Date.now() - data.lastFetched
        if (elapsed > CACHE_TTL) {
          return false
        }

        // Check version
        if (this.version && data.version !== this.version) {
          return false
        }

        this.filters = data.filters
        this.quickFilters = data.quickFilters
        this.sortOptions = data.sortOptions
        this.appSettings = data.appSettings
        this.version = data.version
        this.lastFetched = data.lastFetched

        return true
      } catch (error) {
        console.error('Failed to load cache:', error)
        return false
      }
    },

    clearCache() {
      localStorage.removeItem(CACHE_KEY)
      this.lastFetched = null
    },

    useFallbacks() {
      // Hardcoded fallbacks matching current frontend code
      this.appSettings = {
        default_map_center: [-74.0060, 40.7128],
        default_map_zoom: 12,
        items_per_page: 20,
        radius_options: [5, 10, 25, 50],
        default_sort: 'protein_ratio_desc',
        enable_geolocation: true,
        enable_distance_sort: true,
      }
      this.filters = [
        {
          name: 'calories',
          display_name: 'Calories',
          options: [
            { label: 'Any', min: null, max: null },
            { label: '0-300', min: 0, max: 300 },
            { label: '300-500', min: 300, max: 500 },
            { label: '500-700', min: 500, max: 700 },
            { label: '700+', min: 700, max: null },
          ]
        },
        // ... other filters
      ]
      // ... other fallbacks
    },

    async refreshConfig() {
      this.clearCache()
      await this.fetchConfig(true)
    },
  },
})
```

#### Tasks #6-11: Update Components
See individual task descriptions for component updates.

#### Task #12: Initialize on Startup
```javascript
// src/graze/src/App.vue

<script setup>
import { onMounted } from 'vue'
import { useConfigStore } from './stores/config'

const configStore = useConfigStore()

onMounted(async () => {
  // Fetch config on app start (non-blocking)
  configStore.fetchConfig()
})
</script>
```

---

### **Phase 3: Testing & Documentation** (Tasks #13-15)

See individual task descriptions.

---

## 🚀 Deployment Checklist

### Backend
- [ ] Run migrations: `python manage.py migrate`
- [ ] Seed config: `python manage.py seed_config`
- [ ] Update restaurant colors in admin
- [ ] Test API endpoints
- [ ] Configure cache settings
- [ ] Set up cache invalidation signals

### Frontend
- [ ] Update API URL in .env
- [ ] Test config loading
- [ ] Verify all filters work
- [ ] Test localStorage caching
- [ ] Test fallback behavior
- [ ] Clear browser cache after deployment

### Verification
- [ ] Change filter range in admin → verify change in frontend
- [ ] Add new quick filter → verify appears in frontend
- [ ] Change restaurant color → verify map markers update
- [ ] Increment config version → verify frontend refreshes cache

---

## 📝 Usage Guide (For Admins)

### Adding a New Filter Range

1. Go to Django Admin → Config → Filter Configurations
2. Click "Add Filter Configuration"
3. Fill in:
   - **Name**: `sodium` (internal key)
   - **Display Name**: `Sodium`
   - **Filter Type**: `max_only`
   - **Unit**: `mg`
   - **Options** (JSON):
     ```json
     [
       {"label": "Any", "min": null, "max": null},
       {"label": "Low (0-500mg)", "min": null, "max": 500},
       {"label": "Medium (500-1000mg)", "min": null, "max": 1000},
       {"label": "High (1000mg+)", "min": null, "max": null}
     ]
     ```
   - **Order**: `5`
   - **Is Active**: ✓
4. Save
5. Users will see the new filter after refreshing the page

### Changing Restaurant Brand Colors

1. Go to Django Admin → Restaurants
2. Find the restaurant (e.g., "Chipotle")
3. Update **Brand Color** field (e.g., `#A81612`)
4. Save
5. Map markers update after page refresh

### Force Config Refresh

If you need users to immediately see config changes:
1. Go to Django Admin → App Configuration
2. Increment **Config Version** (e.g., from `1` to `2`)
3. Save
4. Frontend will detect version mismatch and refresh config

---

## 🔄 Migration Timeline

**Estimated**: 3-5 days

- **Day 1**: Backend models, admin, API (Tasks #1-4)
- **Day 2**: Frontend config store (Task #5)
- **Day 3**: Update all components (Tasks #6-11)
- **Day 4**: Testing & fixes (Task #14)
- **Day 5**: Documentation & deployment (Tasks #13, #15)

---

## ⚡ Quick Start

```bash
# Backend
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_config
python manage.py runserver

# Frontend
cd src/graze
yarn dev

# Access admin
open http://localhost:8000/admin
```

Now all configuration is managed through Django admin! 🎉

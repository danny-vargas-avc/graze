from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration
from .serializers import (
    FilterConfigurationSerializer,
    QuickFilterSerializer,
    SortOptionSerializer,
    AppConfigurationSerializer
)


@api_view(['GET'])
def config_all(request):
    """
    Returns all configuration data for the frontend.

    GET /api/config/all/

    Response:
    {
        "filters": [...],
        "quick_filters": [...],
        "sort_options": [...],
        "app_settings": {...},
        "restaurant_colors": {...},
        "version": 1
    }
    """
    # Get active filters
    filters = FilterConfiguration.objects.filter(is_active=True)

    # Get active quick filters
    quick_filters = QuickFilter.objects.filter(is_active=True)

    # Get active sort options
    sort_options = SortOption.objects.filter(is_active=True)

    # Get app configuration (singleton)
    app_config = AppConfiguration.get_instance()

    # Get restaurant colors and icons
    restaurant_colors = {}
    restaurant_icons = {}
    try:
        from api.models import Restaurant
        restaurants = Restaurant.objects.all()
        restaurant_colors = {
            restaurant.slug: restaurant.brand_color
            for restaurant in restaurants
            if restaurant.brand_color
        }
        restaurant_colors['default'] = '#3B82F6'

        restaurant_icons = {
            restaurant.slug: restaurant.icon.url
            for restaurant in restaurants
            if restaurant.icon
        }
    except ImportError:
        restaurant_colors = {'default': '#3B82F6'}

    # Serialize data
    data = {
        'filters': FilterConfigurationSerializer(filters, many=True).data,
        'quick_filters': QuickFilterSerializer(quick_filters, many=True).data,
        'sort_options': SortOptionSerializer(sort_options, many=True).data,
        'app_settings': AppConfigurationSerializer(app_config).data,
        'restaurant_colors': restaurant_colors,
        'restaurant_icons': restaurant_icons,
        'version': app_config.version
    }

    return Response(data)

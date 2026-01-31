from rest_framework import serializers
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration


class FilterConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for filter configurations.
    """
    class Meta:
        model = FilterConfiguration
        fields = ['name', 'label', 'unit', 'options']


class QuickFilterSerializer(serializers.ModelSerializer):
    """
    Serializer for quick filter presets.
    """
    class Meta:
        model = QuickFilter
        fields = ['name', 'label', 'icon', 'description', 'filter_params', 'requires_location']


class SortOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for sort options.
    """
    class Meta:
        model = SortOption
        fields = ['value', 'label', 'requires_location']


class AppConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for app configuration.
    """
    class Meta:
        model = AppConfiguration
        fields = ['default_sort', 'items_per_page', 'radius_options', 'default_map_center', 'default_map_zoom', 'version']


class ConfigAllSerializer(serializers.Serializer):
    """
    Combined serializer for all configuration data.
    Returns complete config for frontend consumption.
    """
    filters = FilterConfigurationSerializer(many=True)
    quick_filters = QuickFilterSerializer(many=True)
    sort_options = SortOptionSerializer(many=True)
    app_settings = AppConfigurationSerializer()
    restaurant_colors = serializers.DictField()
    version = serializers.IntegerField()

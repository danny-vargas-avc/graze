from rest_framework import serializers
from .models import Restaurant, MenuItem, DataFlag, RestaurantLocation, LocationFlag


class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'logo_url', 'item_count']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'website_url', 'logo_url', 'nutrition_source_url', 'item_count', 'last_updated']


class MenuItemListSerializer(serializers.ModelSerializer):
    restaurant = RestaurantListSerializer(read_only=True)
    protein_per_100cal = serializers.DecimalField(max_digits=4, decimal_places=1, read_only=True)
    density_label = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'restaurant', 'category', 'serving_size', 'calories', 'protein', 'carbs', 'fat', 'protein_per_100cal', 'density_label']


class MenuItemDetailSerializer(serializers.ModelSerializer):
    restaurant = RestaurantDetailSerializer(read_only=True)
    protein_per_100cal = serializers.DecimalField(max_digits=4, decimal_places=1, read_only=True)
    density_label = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'restaurant', 'category', 'serving_size', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'sodium', 'sugar', 'saturated_fat', 'protein_per_100cal', 'density_label', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'source_url', 'last_verified']


class DataFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFlag
        fields = ['menu_item', 'flag_type', 'user_comment']


class LocationListSerializer(serializers.ModelSerializer):
    """Serializer for location list view with nested restaurant."""
    restaurant = RestaurantListSerializer(read_only=True)
    distance_miles = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        read_only=True,
        required=False,
        help_text="Distance from user location in miles (calculated in view)"
    )

    class Meta:
        model = RestaurantLocation
        fields = [
            'id',
            'restaurant',
            'name',
            'latitude',
            'longitude',
            'address',
            'city',
            'state',
            'postcode',
            'phone',
            'distance_miles',
            'is_active'
        ]


class LocationDetailSerializer(serializers.ModelSerializer):
    """Serializer for location detail view with all fields."""
    restaurant = RestaurantDetailSerializer(read_only=True)

    class Meta:
        model = RestaurantLocation
        fields = [
            'id',
            'restaurant',
            'osm_id',
            'name',
            'latitude',
            'longitude',
            'address',
            'city',
            'state',
            'postcode',
            'country',
            'phone',
            'website',
            'is_active',
            'is_verified',
            'data_source',
            'osm_amenity_type',
            'last_verified',
            'created_at',
            'updated_at'
        ]


class LocationFlagSerializer(serializers.ModelSerializer):
    """Serializer for user-reported location issues."""

    class Meta:
        model = LocationFlag
        fields = ['location', 'flag_type', 'user_comment']

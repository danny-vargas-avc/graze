"""
API serializers for Graze.
"""
from rest_framework import serializers
from .models import Restaurant, MenuItem, DataFlag


class RestaurantListSerializer(serializers.ModelSerializer):
    """Restaurant summary for list views."""
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'logo_url', 'item_count']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Full restaurant details."""
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'website_url', 'logo_url',
            'nutrition_source_url', 'item_count', 'last_updated'
        ]


class MenuItemListSerializer(serializers.ModelSerializer):
    """Menu item for list views with nested restaurant."""
    restaurant = RestaurantListSerializer(read_only=True)
    protein_per_100cal = serializers.DecimalField(
        max_digits=4, decimal_places=1, read_only=True
    )
    density_label = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'restaurant', 'category', 'serving_size',
            'calories', 'protein', 'carbs', 'fat',
            'protein_per_100cal', 'density_label'
        ]


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """Full menu item details."""
    restaurant = RestaurantDetailSerializer(read_only=True)
    protein_per_100cal = serializers.DecimalField(
        max_digits=4, decimal_places=1, read_only=True
    )
    density_label = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'restaurant', 'category', 'serving_size',
            'calories', 'protein', 'carbs', 'fat',
            'fiber', 'sodium', 'sugar', 'saturated_fat',
            'protein_per_100cal', 'density_label',
            'is_vegetarian', 'is_vegan', 'is_gluten_free',
            'allergens', 'tags',
            'source_url', 'last_verified'
        ]


class DataFlagSerializer(serializers.ModelSerializer):
    """Serializer for creating data flags."""
    class Meta:
        model = DataFlag
        fields = ['menu_item', 'flag_type', 'user_comment']

    def validate_flag_type(self, value):
        valid_types = ['incorrect', 'outdated', 'missing']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"flag_type must be one of: {', '.join(valid_types)}"
            )
        return value


class StatsSerializer(serializers.Serializer):
    """API statistics."""
    total_dishes = serializers.IntegerField()
    total_restaurants = serializers.IntegerField()
    last_updated = serializers.DateTimeField()
    top_protein_dish = MenuItemListSerializer()
    best_ratio_dish = MenuItemListSerializer()

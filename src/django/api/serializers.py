from rest_framework import serializers
from .models import Restaurant, MenuItem, DataFlag


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

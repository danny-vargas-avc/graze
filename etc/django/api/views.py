"""
API views for Graze.
"""
from decimal import Decimal, InvalidOperation
from django.db.models import Q, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Restaurant, MenuItem, DataFlag
from .serializers import (
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    MenuItemListSerializer,
    MenuItemDetailSerializer,
    DataFlagSerializer,
    StatsSerializer,
)


class DishListView(APIView):
    """
    GET /api/v1/dishes
    List and filter menu items.
    """

    SORT_OPTIONS = {
        'protein_desc': '-protein',
        'protein_asc': 'protein',
        'calories_asc': 'calories',
        'calories_desc': '-calories',
        'protein_ratio_desc': '-protein_per_100cal_sort',
        'carbs_asc': 'carbs',
        'fat_desc': '-fat',
        'fat_asc': 'fat',
        'alpha_asc': 'name',
        'relevance': '-relevance',
    }

    DEFAULT_SORT = 'protein_ratio_desc'
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def get(self, request):
        queryset = MenuItem.objects.filter(is_available=True).select_related('restaurant')

        # Track applied filters
        filters_applied = {}

        # Search
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(restaurant__name__icontains=search)
            )
            filters_applied['search'] = search

        # Calorie filters
        calories_min = self._parse_int('calories_min', request.query_params.get('calories_min'))
        calories_max = self._parse_int('calories_max', request.query_params.get('calories_max'))
        if calories_min is not None:
            queryset = queryset.filter(calories__gte=calories_min)
            filters_applied['calories_min'] = calories_min
        if calories_max is not None:
            queryset = queryset.filter(calories__lte=calories_max)
            filters_applied['calories_max'] = calories_max

        # Protein filters
        protein_min = self._parse_decimal('protein_min', request.query_params.get('protein_min'))
        protein_max = self._parse_decimal('protein_max', request.query_params.get('protein_max'))
        if protein_min is not None:
            queryset = queryset.filter(protein__gte=protein_min)
            filters_applied['protein_min'] = float(protein_min)
        if protein_max is not None:
            queryset = queryset.filter(protein__lte=protein_max)
            filters_applied['protein_max'] = float(protein_max)

        # Carbs filter
        carbs_max = self._parse_decimal('carbs_max', request.query_params.get('carbs_max'))
        if carbs_max is not None:
            queryset = queryset.filter(carbs__lte=carbs_max)
            filters_applied['carbs_max'] = float(carbs_max)

        # Fat filters
        fat_min = self._parse_decimal('fat_min', request.query_params.get('fat_min'))
        fat_max = self._parse_decimal('fat_max', request.query_params.get('fat_max'))
        if fat_min is not None:
            queryset = queryset.filter(fat__gte=fat_min)
            filters_applied['fat_min'] = float(fat_min)
        if fat_max is not None:
            queryset = queryset.filter(fat__lte=fat_max)
            filters_applied['fat_max'] = float(fat_max)

        # Category filter
        category = request.query_params.get('category', '').strip()
        if category:
            categories = [c.strip() for c in category.split(',')]
            queryset = queryset.filter(category__in=categories)
            filters_applied['category'] = categories

        # Restaurant filter (by slug)
        restaurants = request.query_params.get('restaurants', '').strip()
        if restaurants:
            slugs = [s.strip() for s in restaurants.split(',')]
            queryset = queryset.filter(restaurant__slug__in=slugs)
            filters_applied['restaurants'] = slugs

        # Sorting
        sort_param = request.query_params.get('sort', self.DEFAULT_SORT)
        if search and sort_param == self.DEFAULT_SORT:
            sort_param = 'relevance'

        if sort_param not in self.SORT_OPTIONS:
            raise ValidationError({'sort': f'Invalid sort option: {sort_param}'})

        filters_applied['sort'] = sort_param

        # Handle protein ratio sorting with annotation
        if sort_param == 'protein_ratio_desc':
            from django.db.models import F, ExpressionWrapper, DecimalField
            queryset = queryset.annotate(
                protein_per_100cal_sort=ExpressionWrapper(
                    F('protein') * 100 / F('calories'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)
                )
            )

        sort_field = self.SORT_OPTIONS[sort_param]
        if sort_param != 'relevance':
            queryset = queryset.order_by(sort_field)

        # Get total before pagination
        total = queryset.count()

        # Pagination
        limit = self._parse_int('limit', request.query_params.get('limit', self.DEFAULT_LIMIT))
        offset = self._parse_int('offset', request.query_params.get('offset', 0))

        if limit is None or limit < 1:
            limit = self.DEFAULT_LIMIT
        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT
        if offset is None or offset < 0:
            offset = 0

        queryset = queryset[offset:offset + limit]

        # Serialize
        serializer = MenuItemListSerializer(queryset, many=True)

        return Response({
            'data': serializer.data,
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total,
            },
            'filters_applied': filters_applied,
        })

    def _parse_int(self, field_name, value):
        if value is None or value == '':
            return None
        try:
            return int(value)
        except ValueError:
            raise ValidationError({field_name: f'{field_name} must be an integer'})

    def _parse_decimal(self, field_name, value):
        if value is None or value == '':
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            raise ValidationError({field_name: f'{field_name} must be a number'})


class DishDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/dishes/:id
    Get detailed menu item information.
    """
    queryset = MenuItem.objects.filter(is_available=True).select_related('restaurant')
    serializer_class = MenuItemDetailSerializer

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RestaurantListView(generics.ListAPIView):
    """
    GET /api/v1/restaurants
    List all restaurants.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RestaurantDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/restaurants/:slug
    Get restaurant details with all dishes.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    lookup_field = 'slug'

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Add dishes to response
        restaurant = self.get_object()
        dishes = MenuItem.objects.filter(
            restaurant=restaurant,
            is_available=True
        ).order_by('-protein')
        dishes_serializer = MenuItemListSerializer(dishes, many=True)
        response.data['dishes'] = dishes_serializer.data
        return response


class StatsView(APIView):
    """
    GET /api/v1/stats
    Get API statistics.
    """

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        total_dishes = MenuItem.objects.filter(is_available=True).count()
        total_restaurants = Restaurant.objects.count()
        last_updated = MenuItem.objects.aggregate(
            last=Max('updated_at')
        )['last']

        # Top protein dish
        top_protein = MenuItem.objects.filter(
            is_available=True
        ).order_by('-protein').first()

        # Best ratio dish (min 200 calories to avoid outliers)
        from django.db.models import F, ExpressionWrapper, DecimalField
        best_ratio = MenuItem.objects.filter(
            is_available=True,
            calories__gte=200
        ).annotate(
            ratio=ExpressionWrapper(
                F('protein') * 100 / F('calories'),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('-ratio').first()

        data = {
            'total_dishes': total_dishes,
            'total_restaurants': total_restaurants,
            'last_updated': last_updated,
            'top_protein_dish': MenuItemListSerializer(top_protein).data if top_protein else None,
            'best_ratio_dish': MenuItemListSerializer(best_ratio).data if best_ratio else None,
        }

        return Response(data)


class DataFlagCreateView(generics.CreateAPIView):
    """
    POST /api/v1/flags
    Report incorrect or outdated data.
    """
    serializer_class = DataFlagSerializer

    def perform_create(self, serializer):
        # Capture user IP
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        serializer.save(user_ip=ip)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {'message': 'Thank you for your report. We will review it shortly.'},
            status=status.HTTP_201_CREATED
        )

from decimal import Decimal, InvalidOperation
from django.db.models import Q, Max, F, ExpressionWrapper, DecimalField
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Restaurant, MenuItem, DataFlag
from .serializers import (
    RestaurantListSerializer, RestaurantDetailSerializer,
    MenuItemListSerializer, MenuItemDetailSerializer, DataFlagSerializer,
)


class DishListView(APIView):
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
    }

    def get(self, request):
        queryset = MenuItem.objects.filter(is_available=True).select_related('restaurant')
        filters_applied = {}

        # Search
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(restaurant__name__icontains=search))
            filters_applied['search'] = search

        # Filters
        for param, field, cast in [
            ('calories_min', 'calories__gte', int),
            ('calories_max', 'calories__lte', int),
            ('protein_min', 'protein__gte', Decimal),
            ('protein_max', 'protein__lte', Decimal),
            ('carbs_max', 'carbs__lte', Decimal),
            ('fat_min', 'fat__gte', Decimal),
            ('fat_max', 'fat__lte', Decimal),
        ]:
            value = request.query_params.get(param)
            if value:
                try:
                    queryset = queryset.filter(**{field: cast(value)})
                    filters_applied[param] = float(value) if cast == Decimal else int(value)
                except (ValueError, InvalidOperation):
                    raise ValidationError({param: f'{param} must be a valid number'})

        # Restaurant filter
        restaurants = request.query_params.get('restaurants', '').strip()
        if restaurants:
            slugs = [s.strip() for s in restaurants.split(',')]
            queryset = queryset.filter(restaurant__slug__in=slugs)
            filters_applied['restaurants'] = slugs

        # Sorting
        sort_param = request.query_params.get('sort', 'protein_ratio_desc')
        if sort_param not in self.SORT_OPTIONS:
            sort_param = 'protein_ratio_desc'
        filters_applied['sort'] = sort_param

        if sort_param == 'protein_ratio_desc':
            queryset = queryset.annotate(
                protein_per_100cal_sort=ExpressionWrapper(
                    F('protein') * 100 / F('calories'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)
                )
            )
        queryset = queryset.order_by(self.SORT_OPTIONS[sort_param])

        total = queryset.count()

        # Pagination
        try:
            limit = min(int(request.query_params.get('limit', 20)), 100)
            offset = max(int(request.query_params.get('offset', 0)), 0)
        except ValueError:
            limit, offset = 20, 0

        queryset = queryset[offset:offset + limit]
        serializer = MenuItemListSerializer(queryset, many=True)

        return Response({
            'data': serializer.data,
            'meta': {'total': total, 'limit': limit, 'offset': offset, 'has_more': offset + limit < total},
            'filters_applied': filters_applied,
        })


class DishDetailView(generics.RetrieveAPIView):
    queryset = MenuItem.objects.filter(is_available=True).select_related('restaurant')
    serializer_class = MenuItemDetailSerializer


class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer


class RestaurantDetailView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        restaurant = self.get_object()
        dishes = MenuItem.objects.filter(restaurant=restaurant, is_available=True).order_by('-protein')
        response.data['dishes'] = MenuItemListSerializer(dishes, many=True).data
        return response


class StatsView(APIView):
    def get(self, request):
        total_dishes = MenuItem.objects.filter(is_available=True).count()
        total_restaurants = Restaurant.objects.count()
        last_updated = MenuItem.objects.aggregate(last=Max('updated_at'))['last']

        top_protein = MenuItem.objects.filter(is_available=True).order_by('-protein').first()
        best_ratio = MenuItem.objects.filter(is_available=True, calories__gte=200).annotate(
            ratio=ExpressionWrapper(F('protein') * 100 / F('calories'), output_field=DecimalField(max_digits=5, decimal_places=2))
        ).order_by('-ratio').first()

        return Response({
            'total_dishes': total_dishes,
            'total_restaurants': total_restaurants,
            'last_updated': last_updated,
            'top_protein_dish': MenuItemListSerializer(top_protein).data if top_protein else None,
            'best_ratio_dish': MenuItemListSerializer(best_ratio).data if best_ratio else None,
        })


class DataFlagCreateView(generics.CreateAPIView):
    serializer_class = DataFlagSerializer

    def perform_create(self, serializer):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')
        serializer.save(user_ip=ip)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'message': 'Thank you for your report.'}, status=status.HTTP_201_CREATED)

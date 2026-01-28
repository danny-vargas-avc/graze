from decimal import Decimal, InvalidOperation
from django.db.models import Q, Max, F, ExpressionWrapper, DecimalField, FloatField, Value
from django.db.models.functions import ACos, Cos, Radians, Sin
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Restaurant, MenuItem, DataFlag, RestaurantLocation, LocationFlag
from .serializers import (
    RestaurantListSerializer, RestaurantDetailSerializer,
    MenuItemListSerializer, MenuItemDetailSerializer, DataFlagSerializer,
    LocationListSerializer, LocationDetailSerializer, LocationFlagSerializer,
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
        total_locations = RestaurantLocation.objects.filter(is_active=True).count()
        last_updated = MenuItem.objects.aggregate(last=Max('updated_at'))['last']

        top_protein = MenuItem.objects.filter(is_available=True).order_by('-protein').first()
        best_ratio = MenuItem.objects.filter(is_available=True, calories__gte=200).annotate(
            ratio=ExpressionWrapper(F('protein') * 100 / F('calories'), output_field=DecimalField(max_digits=5, decimal_places=2))
        ).order_by('-ratio').first()

        return Response({
            'total_dishes': total_dishes,
            'total_restaurants': total_restaurants,
            'total_locations': total_locations,
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


class LocationListView(APIView):
    """List restaurant locations with geospatial filtering and distance calculation."""

    def get(self, request):
        queryset = RestaurantLocation.objects.filter(is_active=True).select_related('restaurant')

        # Parse query params
        user_lat = request.query_params.get('lat')
        user_lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', '25')
        bbox = request.query_params.get('bbox')
        restaurants = request.query_params.get('restaurants', '').strip()

        # Parse limit
        try:
            limit = min(int(request.query_params.get('limit', 100)), 100)
        except ValueError:
            limit = 100

        # Filter by restaurant slugs
        if restaurants:
            slugs = [s.strip() for s in restaurants.split(',')]
            queryset = queryset.filter(restaurant__slug__in=slugs)

        # Bounding box filtering
        if bbox:
            try:
                sw_lat, sw_lng, ne_lat, ne_lng = [Decimal(x.strip()) for x in bbox.split(',')]
                queryset = queryset.filter(
                    latitude__gte=sw_lat,
                    latitude__lte=ne_lat,
                    longitude__gte=sw_lng,
                    longitude__lte=ne_lng
                )
            except (ValueError, InvalidOperation):
                raise ValidationError({'bbox': 'bbox must be 4 comma-separated numbers: sw_lat,sw_lng,ne_lat,ne_lng'})

        # Distance calculation and radius filtering
        distance_calculated = False
        if user_lat and user_lng:
            try:
                user_lat = Decimal(user_lat)
                user_lng = Decimal(user_lng)
                radius_miles = Decimal(radius)

                # Haversine formula for distance calculation (in miles)
                # distance = 3959 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lng2) - radians(lng1)) + sin(radians(lat1)) * sin(radians(lat2)))
                queryset = queryset.annotate(
                    distance_miles=ExpressionWrapper(
                        Value(3959.0) * ACos(
                            Cos(Radians(Value(float(user_lat)))) *
                            Cos(Radians(F('latitude'))) *
                            Cos(Radians(F('longitude')) - Radians(Value(float(user_lng)))) +
                            Sin(Radians(Value(float(user_lat)))) *
                            Sin(Radians(F('latitude')))
                        ),
                        output_field=FloatField()
                    )
                )
                distance_calculated = True

                # Filter by radius if not using bbox
                if not bbox:
                    queryset = queryset.filter(distance_miles__lte=float(radius_miles))

                # Order by distance
                queryset = queryset.order_by('distance_miles')

            except (ValueError, InvalidOperation):
                raise ValidationError({'lat/lng': 'lat, lng, and radius must be valid numbers'})
        else:
            # No distance calculation, order by restaurant name and city
            queryset = queryset.order_by('restaurant__name', 'city')

        # Apply limit
        total = queryset.count()
        queryset = queryset[:limit]

        serializer = LocationListSerializer(queryset, many=True)

        # Build meta response
        meta = {
            'total': total,
            'limit': limit,
        }

        if distance_calculated:
            meta['center_lat'] = float(user_lat)
            meta['center_lng'] = float(user_lng)
            meta['radius_miles'] = float(radius)

        return Response({
            'data': serializer.data,
            'meta': meta,
        })


class LocationDetailView(generics.RetrieveAPIView):
    """Retrieve detailed information about a single restaurant location."""
    queryset = RestaurantLocation.objects.filter(is_active=True).select_related('restaurant')
    serializer_class = LocationDetailSerializer


class LocationFlagCreateView(generics.CreateAPIView):
    """Create user-reported location issues."""
    serializer_class = LocationFlagSerializer

    def perform_create(self, serializer):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')
        serializer.save(user_ip=ip)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'message': 'Thank you for reporting this location issue.'}, status=status.HTTP_201_CREATED)

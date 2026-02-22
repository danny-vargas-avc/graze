from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from api.admin_views import import_menu_items, import_locations, parse_nutrition_pdf

urlpatterns = [
    # Custom admin views (before admin.site.urls so they don't get caught by admin/)
    path('admin/import/menu-items/', import_menu_items, name='import_menu_items'),
    path('admin/import/locations/', import_locations, name='import_locations'),
    path('admin/import/parse-pdf/', parse_nutrition_pdf, name='parse_nutrition_pdf'),

    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('api/v1/config/', include('config.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

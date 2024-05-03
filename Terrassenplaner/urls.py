from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from . import views
from .views import terrassen_planer_view

urlpatterns = [
    
    path('', terrassen_planer_view, name='planer_view'),
    path('materials/', views.material_list, name='material_list'),
    path('import/', views.add_xls, name='add_xls'),
    # Weitere URL-Muster
]

# Debug-Toolbar-Konfiguration
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve static and media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

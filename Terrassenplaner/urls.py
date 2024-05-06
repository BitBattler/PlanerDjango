from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from . import views
from .views import terrassen_planer_view

urlpatterns = [
    
    path('', views.terrassen_planer_view, name='planer_view'),
    path('materials/', views.material_list, name='material_list'),
    path('import/', views.add_xls, name='add_xls'),
    path('categorize/', views.finalize_xls, name='finalize_xls'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('messages/', views.messages, name='messages'),
    

]

# Debug-Toolbar-Konfiguration
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve static and media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

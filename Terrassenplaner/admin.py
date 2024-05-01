from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Kategorie, Material

@admin.register(Kategorie)
class KategorieAdmin(admin.ModelAdmin):
    list_display = ['name']  
    search_fields = ['name']

@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):  # Verwenden Sie das ImportExportModelAdmin-Mixin
    list_display = ['material_name', 'material_kategorie']
    list_filter = ['material_kategorie']
    search_fields = ['material_name', 'material_kategorie__name']

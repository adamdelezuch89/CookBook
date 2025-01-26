from django.contrib import admin
from .models import Recipe, Category, Tag, ScannedRecipe

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at', 'servings', 'total_time']
    list_filter = ['categories', 'tags', 'created_at']
    search_fields = ['name', 'description', 'ingredients', 'instructions']
    autocomplete_fields = ['categories', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['name', 'description', 'image']
        }),
        ('Kategoryzacja', {
            'fields': ['categories', 'tags', 'rating']
        }),
        ('Czasy', {
            'fields': ['prep_time', 'cook_time', 'idle_time', 'total_time']
        }),
        ('Szczegóły przepisu', {
            'fields': ['servings', 'ingredients', 'instructions', 'notes']
        }),
        ('Dodatkowe informacje', {
            'fields': ['nutrition', 'equipment', 'video', 'source']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(ScannedRecipe)
class ScannedRecipeAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'image']
    readonly_fields = ['created_at', 'scanned_text']
    fields = ['image', 'scanned_text', 'created_at']


from django.contrib import admin
from .models import Category, Product, Sale, SaleItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','category','price','stock','is_active')
    list_filter = ('category','is_active')
    search_fields = ('name',)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id','seller','created_at','total')
    inlines = [SaleItemInline]

from django.contrib import admin
from .models import InventoryItem, Category

admin.site.register(InventoryItem)
admin.site.register(Category)

# http://127.0.0.1:8000/admin
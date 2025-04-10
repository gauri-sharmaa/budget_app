from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, MealPlan, Expense

# Register the models
admin.site.register(UserProfile)
admin.site.register(MealPlan)
admin.site.register(Expense)
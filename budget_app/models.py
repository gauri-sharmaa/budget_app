from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from django.forms import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weekly_limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.user.username

class MealPlanType(Enum):
    UNLIMITED = 'unlimited'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

class MealPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meal_plan')
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=MealPlanType.choices())

    def __str__(self):
        return f"{self.user.username}'s Meal Plan"

class ExpenseType(Enum):
    MEAL = 'meal'
    SAVINGS = 'savings'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses', blank=True, null=True)
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='expenses', blank=True, null=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=ExpenseType.choices())
    date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    recurring_day = models.IntegerField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def clean(self):
        if not self.user and not self.meal_plan:
            raise ValidationError('Either user or meal plan must be provided.')

    def __str__(self):
        return f"{self.title} - {self.cost}"
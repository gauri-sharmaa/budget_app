from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from enum import Enum

from django.forms import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    mealPlan = models.OneToOneField('MealPlan', on_delete=models.CASCADE, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class MealPlanType(Enum):
    UNLIMITED = 'unlimited'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]
class MealPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=MealPlanType.choices())

    def __str__(self):
        return f"{self.user.name}'s Meal Plan"

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
        # Ensure a user or a meal plan is provided
        if not self.user and not self.meal_plan:
            raise ValidationError('Either user or meal plan must be provided.')

    def __str__(self):
        return f"{self.title} - {self.cost}"
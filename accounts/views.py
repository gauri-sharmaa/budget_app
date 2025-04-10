from django import forms
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from budget_app.models import MealPlan, MealPlanType, UserProfile


@login_required
def logout(request):
    auth_logout(request)
    return redirect("accounts.login")

def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard.index")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("dashboard.index")
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "login.html")
    return render(request, "login.html")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': field.label
            })

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard.index")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user data in the session
            request.session['user_data'] = form.cleaned_data
            return redirect("accounts.create_user_profile")  # Redirect to the next step
        else:
            return render(request, "register.html", {"form": form})

    form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

class CustomUserProfileCreationForm(forms.ModelForm):
    income = forms.DecimalField(required=True, label="Income")
    balance = forms.DecimalField(required=True, label="Balance")
    weekly_limit = forms.DecimalField(required=True, label="Weekly Limit")
    class Meta:
        model = UserProfile
        fields = ['income', 'balance', 'weekly_limit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': field.label
            })
class CustomMealPlanCreationForm(forms.ModelForm):
    balance = forms.DecimalField(required=True, label="Balance")
    type = forms.ChoiceField(choices=MealPlanType.choices(), label="Type")

    class Meta:
        model = MealPlan
        fields = ['balance', 'type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': field.label
            })
def create_user_profile(request):
    if request.user.is_authenticated:
        return redirect("dashboard.index")
    if request.session.get('user_data') is None:
        return redirect("accounts.register")
    
    if request.method == "POST":
        userProfileForm = CustomUserProfileCreationForm(request.POST)
        mealPlanForm = CustomMealPlanCreationForm(request.POST)

        if userProfileForm.is_valid() and mealPlanForm.is_valid():
            # Retrieve the user data from the session
            user_data = request.session.get('user_data')
            if not user_data:
                return redirect("accounts.register")  # Redirect back if session data is missing

            # Create the User
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password1'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )

            # Create the UserProfile
            user_profile = userProfileForm.save(commit=False)
            user_profile.user = user
            user_profile.save()

            # Create the MealPlan
            meal_plan = mealPlanForm.save(commit=False)
            meal_plan.user = user
            meal_plan.save()

            # Log the user in
            auth_login(request, user)

            # Clear the session data
            del request.session['user_data']

            # Redirect to the dashboard
            return redirect("dashboard.index")
        else:
            return render(request, "create_user_profile.html", {
                "userProfileForm": userProfileForm,
                "mealPlanForm": mealPlanForm,
            })

    userProfileForm = CustomUserProfileCreationForm()
    mealPlanForm = CustomMealPlanCreationForm()
    return render(request, "create_user_profile.html", {
        "userProfileForm": userProfileForm,
        "mealPlanForm": mealPlanForm,
    })
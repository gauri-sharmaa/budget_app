from django import forms
from django.shortcuts import redirect, render
from budget_app.models import Expense, MealPlan, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    return render(request, "index.html")

@login_required
def dashboard(request):
    # Check if the user has a UserProfile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found")
        return redirect("dashboard.index")
    # Check for meal plan
    try:
        meal_plan = request.user.meal_plan
    except MealPlan.DoesNotExist:
        messages.error(request, "Meal plan not found")
        return redirect("dashboard.index")
    return render(request, "dashboard.html")

class AddExpenseForm(forms.ModelForm):
    EXPENSE_CHOICES = [
        ('user', 'User Expense'),
        ('mealplan', 'MealPlan Expense'),
    ]
    expense_for = forms.ChoiceField(choices=EXPENSE_CHOICES, label="Expense For", widget=forms.RadioSelect)

    class Meta:
        model = Expense
        fields = ['expense_for', 'title', 'type', 'date', 'cost', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pass the user to the form
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder': field.label
                })
            else:
                field.widget.attrs.update({
                    'class': 'px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500'
                })

    def makeValid(self):
        """Set the user or meal_plan based on the expense_for field."""
        expense_for = self.data.get('expense_for')

        if expense_for == 'user':
            self.instance.user = self.user  # Set the user on the instance
        elif expense_for == 'mealplan':
            try:
                self.instance.meal_plan = self.user.meal_plan  # Set the meal_plan on the instance
            except MealPlan.DoesNotExist:
                raise forms.ValidationError("You do not have a meal plan to link this expense to.")

@login_required
def add_expense(request):
    if request.method == "POST":
        form = AddExpenseForm(request.POST, user=request.user)  # Pass the user to the form
        try:
            form.makeValid()  # Set user or meal_plan before validation
        except forms.ValidationError as e:
            messages.error(request, str(e))
            return redirect("dashboard.add_expense")
        if form.is_valid():  # Ensure the form is valid
            expense = form.save(commit=False)
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect("dashboard.dashboard")
    else:
        form = AddExpenseForm(user=request.user)  # Pass the user to the form

    return render(request, "add_expense.html", {"form": form})
from django.shortcuts import render

def index(request):
    context = {"template_data": {"title": "Budget App"}}
    return render(request, "index.html", context)
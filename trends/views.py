from django.shortcuts import render, redirect
from .forms import *


def create_trend_stuff(request):
    form_data = TrendStuffForm(request.POST or None)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        return redirect('products:home')

    context = {
        'data' : form_data,
        'title' : 'trend-Stuff',
        'page_title' : 'trend-Stuff',
        'btn' : 'Create'
    }

    return render(request, 'form.html', context)

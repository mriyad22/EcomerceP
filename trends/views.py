from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import TrendStuffModel


def create_trend_stuff(request):
    trends = TrendStuffModel.objects.all().order_by('-created_at')
    form_data = TrendStuffForm(request.POST or None)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'Trend created.')
        return redirect('trends:trend')

    context = {
        'data' : form_data,
        'title' : 'trend-Stuff',
        'page_title' : 'trend-Stuff',
        'btn' : 'Create',
        'trends' : trends
    }
    return render(request, 'trends/trend_form.html', context)



#--------> Trends Edit View
def edit_trend_stuff(request, edit_id):
    trend_id = get_object_or_404(TrendStuffModel, id = edit_id)
    
    form_data = TrendStuffForm(request.POST or None, instance=trend_id)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'Trend Update.')
        return redirect('trends:trend')

    context = {
        'data' : form_data,
        'title' : 'trend update',
        'page_title' : 'Trend update',
        'btn' : 'Update'
    }
    return render(request, 'trends/trend_form.html', context)



#--------> Trend delete View
def delete_trend(request, delete_id):
    if not request.user.username == 'superadmin':
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
    delete_brand = get_object_or_404(TrendStuffModel, id = delete_id)
    if request.method == 'POST':
        delete_brand.delete()
        messages.success(request, 'Trend deleted.')
        return redirect('trends:trend')
    
    context = {
        'title' : 'trend delete',
        'object' : delete_brand,
        'trend_pate' : True
    }
    return render(request, 'delete.html', context)

    

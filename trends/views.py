from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import *
from .models import TrendStuffModel


def create_trend(request):
    if not request.user.is_superuser:
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
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
def edit_trend(request, edit_id):
    if not request.user.is_superuser:
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
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
@require_POST
def delete_trend(request, delete_id):
    if not request.user.is_superuser:
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
    delete_brand = get_object_or_404(TrendStuffModel, id = delete_id).delete()
    messages.success(request, 'Trend deleted.')
    return redirect('trends:trend')


from django.shortcuts import render

def dashboard(request):

    return render(request, 'cpanel/dashboard.html')

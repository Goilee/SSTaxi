from django.http import HttpResponse
from django.shortcuts import render

import requests
import json
def index(request):
    context = {}
    if request.method == 'POST':
        city = request.POST.get('city')
        end = request.POST.get('end')
        context={"route": str(city)+' - '+str(end)}
        print(city,end)
    return render(request, "index.html", context)



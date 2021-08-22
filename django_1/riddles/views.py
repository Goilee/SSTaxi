import ast

from riddles import TCPClient
from django.shortcuts import render
import socket

a = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
beg = None
end = None
res = ''
context = {}
def index(request):
    global beg, end, a, res, context
    if request.POST.get('city') in a and beg == None:
        beg = request.POST.get('city')
        res = beg
        print(beg,end)
        if beg in a:
            context = {"msg": "Введите конечную точку"}
    elif request.POST.get('city') in a and beg in a:
        end = request.POST.get('city')
        context = {"msg": "Ожадание отправки..."}
    elif request.POST.get('err') == 'err':
        end, beg = None, None
        context = {"msg": "Введите начальную точку"}
    elif request.method == 'POST' and beg in a and end in a:
        context={"route": str(beg)+' - '+str(end), "msg": "Введите начальную точку"}
        end, beg = None, None

    return render(request, "index.html", context)



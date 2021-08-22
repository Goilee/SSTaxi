import ast

from riddles import TCPClient
from django.shortcuts import render
import socket

a = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
beg = ''
end = ''
res = ''
context = {}
def index(request):
    global beg, end, a, res, context
    dict1 = { 1: ('37px', '7px'),
	2: ('102px', '1px') }
    d = [i for i in dict1.values()]
    context = context.update({"chod": d})
    print(context)
    if request.POST.get('city') in a:
        beg = request.POST.get('city')
        if beg in a:
            context = {"msg": "Введите конечную точку"}
    elif request.POST.get('end') in a:
        end = request.POST.get('end')
        context = {"msg": "Ожадание отправки..."}
    elif request.POST.get('err') == 'err':
        end, beg = None, None
        context = {"msg": "Введите начальную точку"}
    elif request.method == 'POST' and beg in a and end in a:
        context={"route": str(beg)+' - '+str(end), "msg": "Введите начальную точку"}
        end, beg = None, None

    return render(request, "index.html", context)



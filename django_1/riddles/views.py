import ast
import json
from .TCP import TCPClient
from django.shortcuts import render
from django.http import JsonResponse
a = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
beg = None
end = None
res = ''
context = {}
client = ''
coord1 = [[79,50],[50,50], [50,80]]
#coord2 = []
context['back'] = "Отмена"
context["chod"] = coord1
context["color"] = "black"
def index(request):
    global beg, end, a, res, context, client
    if client == '':
        client = TCPClient.ClientSocket(25566,"banana",'192.168.189.26')
    if request.POST.get('city') in a and beg == None:
        context["back"] = 'Отмена'
        context["color"] = "black"
        beg = request.POST.get('city')
        res = beg
        context["beg"] = int(res)
        if beg in a:
            context["msg"] = "Введите конечную точку"
    elif request.POST.get('city') in a and beg in a:
        end = request.POST.get('city')
        context["msg"] = "Ожадание отправки..."
        context["end"] = int(end)
    elif request.POST.get('err') == 'err':
        end, beg = None, None
        context["route"] = ''
        context["end"] = ''
        context["beg"] = ''
        context["msg"] = "Введите начальную точку"
    elif request.method == 'POST' and beg in a and end in a and beg != end:
        context["route"] = str(beg)+' - '+str(end)
        context["color"] = "gray"
        print(1)
        client.sendWay([int(res)-1, int(end)-1])
        context["msg"] = "Поездка началась"
        client.waitStopSign()
        context["msg"] = "Поездка окончена. Введите начальную точку"
        end, beg = None, None
        context["end"] = ''
        context["beg"] = ''
    elif beg == end and beg in a and end in a: context["msg"] = "Точки совпадают"
    return render(request, "index.html", context)




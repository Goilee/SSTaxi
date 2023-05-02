import ast
import json
from .TCP import TCPClient
from django.shortcuts import render
from django.http import JsonResponse
from  django.http import HttpResponse
a = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
beg = None
end = None
res,res_1 = '',''
context = {}
client = ''
coord1 = [[79,50],[50,50], [50,80]]
#coord2 = []
GREEN = "#7FFF00"
context['back'] = "Отмена"
context["chod"] = coord1
context["color"] = "black"
context["msg"] = ''
context["one"] = "white"
context["two"] = "white"
context["three"] = "white"
data_str = None
index_1 = None
prev_data = ""
def index(request):
    global beg, end, a, res, context, client, res_1, index_1, data_str, prev_data
    """if client == '':
        # client = TCPClient.ClientSocket(25566,"banana",'192.168.189.26')
        client = TCPClient.ClientSocket(25566,"banana",'192.168.190.75')
        # client = TCPClient.ClientSocket(25566,"banana",'localhost')
        index_1 = client.waitSTR()
        context["msg"] = "Машина в точке: " + str(index_1[0])
    if context["msg"] == "Посещена точка":
        end, beg = None, None
        context["end"] = ''
        context["beg"] = ''
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
        res_1 = end
    elif request.POST.get('err') == 'err':
        end, beg = None, None
        context["route"] = ''
        context["end"] = ''
        context["beg"] = ''
        context["msg"] = "Введите начальную точку"
    elif request.method == 'POST' and beg in a and end in a and beg != end:
        context["route"] = str(beg)+' - '+str(end)
        context["color"] = "gray"
        # client.sendWay([int(res)-1, int(end)-1])
        context["msg"] = "Поездка началась"

        if index_1 is not None and data_str is None:
            # data_str = [index_1, "initial"]
            print(index_1)
            data_str = index_1.split(" ")
            print("init_data:", data_str)
            index_1 = None

        prev_data = ""
        while data_str[1] != "done":
            prev_data = data_str
            data_str = client.waitSTR().split(" ")
            print("data:", prev_data, data_str)
            # client.waitStopSign()

        context["msg"] = "Поездка окончена. Введите начальную точку"
        end, beg = None, None
        context["end"] = ''
        context["beg"] = ''

    elif beg == end and beg in a and end in a: context["msg"] = "Точки совпадают"""""
    return render(request, "index.html", context)


def data(request):
    print(request.POST)
    return HttpResponse("works?")
    # pass


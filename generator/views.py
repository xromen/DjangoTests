from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import datetime
from os import path


def get_interval(d):
    return d['interval']

def get_current_time() -> datetime:
    delta = datetime.timedelta(hours=10, minutes=0)
    return datetime.datetime.now(datetime.timezone.utc) + delta

def lists_subtract(a, b):
    c = []
    for i in a:
        if not (i in b):
            c.append(i)
    return c

intervals = ['8:00-9:30',
                 '9:30-11:00',
                 '11:00-12:30',
                 '12:30-14:00',
                 '14:00-15:30',
                 '15:30-17:00',
                 '17:00-18:30',
                 '18:30-20:00',
                 '20:00-21:30',
                 '21:30-23:00']
def getTodayStr():
    today = get_current_time()
    return str(today.day) + '.' + str(today.month) + '.' + str(today.year)

def getFilePath():
    return 'generator/static/history/' + getTodayStr() + '.json'

# Create your views here.
def home(request):
    if request.COOKIES.get('secNameC'):
        secNameC = request.COOKIES.get('secNameC')
    else:
        secNameC = ''
    if request.COOKIES.get('roomC'):
        roomC = request.COOKIES.get('roomC')
    else:
        roomC = ''

    todayStr = getTodayStr()
    filePath = getFilePath()
    dat = []

    datetime.time(hour=7, minute=30)
    if path.exists(filePath):
        with open(filePath, encoding='utf-8') as file:
            data = json.load(file)

        a = [[k for k in data if k['aNum'] == i] for i in range(4)]

        if not len(data) == 0:
            for j, elem in enumerate(a):
                k = 0
                dat.append([])
                if len(elem) == 0:
                    continue
                for i in range(10):
                    if elem[k]['interval'] == i:
                        dat[j].append(elem[k])
                        if not k == len(elem) - 1:
                            k = k + 1
                    else:
                        dat[j].append({})
    else:
        with open(filePath, 'w', encoding='utf-8') as file:
            json.dump([], file)
        data = []

    if get_current_time().time() >= datetime.time(hour=23, minute=30):
        return render(request, 'generator/home.html', {'fData': data,
                                                   'intervals': intervals,
                                                   'data': dat,
                                                   'today': todayStr,
                                                   'nowTime': get_current_time(),
                                                   'isActive': get_current_time().time() >= datetime.time(hour=7, minute=30),
                                                   'cookies': {'secNameC': secNameC,
                                                               'roomC': roomC}
                                                   })
    else:
        return render(request, 'generator/home.html', {'fData': [],
                                                       'intervals': intervals,
                                                       'data': [],
                                                       'today': todayStr,
                                                       'nowTime': get_current_time(),
                                                       'isActive': get_current_time().time() >= datetime.time(hour=7,
                                                                                                              minute=30),
                                                       'cookies': {'secNameC': secNameC,
                                                                   'roomC': roomC}
                                                       })
def done(request):
    filePath = getFilePath()

    interval = int(request.GET['interval'])
    zapis = dict()
    zapis['interval'] = interval
    zapis['room'] = request.GET['room']
    zapis['secName'] = request.GET['secName']
    zapis['aNum'] = int(request.GET['aNum'])

    response = redirect('/')

    #response.set_cookie('secNameC', zapis['secName'])
    #response.set_cookie('roomC', zapis['room'])

    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)

    if [zapis['interval'], zapis['aNum']] in [[i['interval'], i['aNum']] for i in data]:
        return render(request, 'generator/nDone.html', {'mess': 'Данный интервал стирки уже занят'})
    elif not zapis['secName'].isalpha():
        return render(request, 'generator/nDone.html', {'mess': 'Фамилия должна состоять только из букв'})
    elif len(zapis['secName']) > 15:
        return render(request, 'generator/nDone.html', {'mess': 'Длина фамилии не должна быть больше 10 символов'})
    elif len(zapis['room']) > 3:
        return render(request, 'generator/nDone.html', {'mess': 'Длина номера комнаты не должна быть больше 3 символов'})
    elif not zapis['room'].isdigit():
        return render(request, 'generator/nDone.html', {'mess': 'Номер комнаты должен быть числом и не пустым'})
    elif zapis['secName'] == '':
        return render(request, 'generator/nDone.html', {'mess': 'Фамилия не может быть пустой'})
    elif not get_current_time().time() >= datetime.time(hour=7, minute=30):
        return render(request, 'generator/nDone.html', {'mess': 'Запись начинается в 7:30'})
    else:
        data.append(zapis)
        data.sort(key=lambda x: (x['aNum'], x['interval']))

        with open(filePath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

        return response #render(request, 'generator/done.html', {'interval': intervals[interval]})

def vLogin(request):
    if request.GET:
        return render(request, 'generator/login.html', {'next' : request.GET['next']})
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.POST['next'])

@login_required
def admin(request):
    filePath = getFilePath()
    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)
    return render(request, 'generator/redact.html', {'data' : data, 'intervals': intervals})


def delZapis(request):
    filePath = getFilePath()
    keys = list(request.GET)
    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)
    for x, i in enumerate(keys):
        data.pop(int(i)-x)

    with open(filePath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

    return redirect('/admin/')

def checkChange(request):
    filePath = getFilePath()
    oldData = json.loads(request.POST['content'])
    oldNewData = json.loads(request.POST['newContent'])
    oldData = oldData + oldNewData

    with open(filePath, encoding='utf-8') as file:
        newData = json.load(file)

    sub = lists_subtract(newData, oldData)
    #print(sub)

    response = {
        'is_taken' : not sub==[],
        'data' : sub
    }

    if get_current_time().time() >= datetime.time(hour=23, minute=30):
        return JsonResponse(response)
    else:
        return JsonResponse({
        'is_taken' : False,
        'data' : []
    })
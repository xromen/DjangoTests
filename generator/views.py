from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import json
import datetime
from os import path

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

today = datetime.date.today()
todayStr = datetime.date.strftime(today, '%d.%m.%Y')
filePath = 'generator/static/history/'+todayStr+'.json'

# Create your views here.

def get_interval(d):
    return d['interval']

def get_current_time() -> datetime:
    delta = datetime.timedelta(hours=10, minutes=0)
    return datetime.datetime.now(datetime.timezone.utc) + delta

def home(request):
    dat = []

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

    return render(request, 'generator/home.html', {'intervals' : intervals, 'data' : dat, 'today' : todayStr, 'nowTime': get_current_time().hour})

def done(request):
    interval = int(request.GET['interval'])
    zapis = dict()
    zapis['interval'] = interval
    zapis['room'] = request.GET['room']
    zapis['secName'] = request.GET['secName']
    zapis['aNum'] = int(request.GET['aNum'])

    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)

    if [zapis['interval'], zapis['aNum']] in [[i['interval'], i['aNum']] for i in data]:
        return render(request, 'generator/nDone.html', {'mess': 'Данный интервал стирки уже занят'})
    elif not zapis['room'].isdigit():
        return render(request, 'generator/nDone.html', {'mess': 'Номер комнаты должен быть числом и не пустым'})
    elif zapis['secName'] == '':
        return render(request, 'generator/nDone.html', {'mess': 'Фамилия не может быть пустой'})
    else:
        data.append(zapis)
        data.sort(key=lambda x: ( x['aNum'], x['interval']))

        with open(filePath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

        return render(request, 'generator/done.html', {'interval': intervals[interval]})

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
    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)
    return render(request, 'generator/redact.html', {'data' : data, 'intervals': intervals})


def delZapis(request):
    keys = list(request.GET)
    with open(filePath, encoding='utf-8') as file:
        data = json.load(file)
    for i in keys:
        data.pop(int(i))

    with open(filePath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

    return redirect('/admin/')
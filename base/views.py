from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Room,Topic,Message,UserProfile
from .forms import RoomForm,UserProfileForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

# rooms=[
#     {'id':1,'name':'Lets learn python'},
#     {'id':2,'name':'Design with me'},
#     {'id':3,'name':'Frontend Developers'},
# ]

def loginPage(request):
    page ='login' 
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try :
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exists')
        user = authenticate(request,username= username,password= password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or password does not exists')
    context ={'page':page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page ='register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    return render(request,'base/login_register.html',{'form':form})

def home(request):
    # q = request.GET.get('q')
    # rooms = Room.objects.filter(topic__name__contains=q) if request.GET.get('q') != None else ''
    q = request.GET.get('q')
    if q:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) | 
            Q(name__icontains =q) | 
            Q(description__icontains =q)
            )
        roomMessages = Message.objects.filter(Q(room__topic__name__icontains=q))
        
    else:
        rooms = Room.objects.all() 
        roomMessages = Message.objects.all()

    topics = Topic.objects.all()
    room_count = rooms.count()
    
    context ={'rooms':rooms,'topics':topics,'room_count':room_count,'roomMessages':roomMessages}
    return render(request,'base/home.html',context)
def room(request,pk):
    rooms =Room.objects.all()
    room = None
    for i in rooms:
        if i.id == int(pk):
            room = i
            # print(room)
    roomMessages = Message.objects.filter(room=room)
    participants = room.participants.all()
    # print(participants)
    # print(messages)
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context ={'room':room,'roomMessages':roomMessages,'participants':participants}
    # print(context)
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id =pk)
    # rooms = user.room_set.all()
    rooms = Room.objects.filter(host = user)
    roomMessages = user.message_set.all()
    # print(roomMessages)
    topics = Topic.objects.all()
    context={'user':user,'rooms':rooms,'roomMessages':roomMessages,'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method =='POST':
        # print(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host :
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id = pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid():
            user_form.save()
            return redirect('user-profile', pk=request.user.id)  # Redirect to the user's profile page
    else:
        user_form = UserProfileForm(instance=user_profile)  # Populate the form with existing data

    return render(request, 'base/update-user.html', {'form': user_form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
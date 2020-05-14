from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.views import APIView
from MMSApp.models import *

from MMS import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound

import json
import uuid
from datetime import datetime,time,date,timedelta
from calendar import monthrange

from django.utils.timezone import localtime
from django.core.files import File
from io import BytesIO
from PIL import Image as IMage
from django.core.files.uploadedfile import InMemoryUploadedFile

import logging
import sys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import traceback

# 400 Bad Request
# 401 Unauthorized
# 403 Forbidden
# 404 Not Found
# 409 Conflict
# 200 OK
# 201 Created
# 202 Accepted

# CLASSES BELOW

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

# FUNCTIONS BELOW

# Authentication
@login_required(login_url='/login/')
def Home(request):
    return render(request,'MMSApp/home.html')

def Login(request):
    return render(request,'MMSApp/login.html')

def Signup(request):
    return render(request,'MMSApp/signup.html')

@login_required(login_url='/login/')
def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')

# Users

@login_required(login_url='/login/')
def Profile(request,username):
    if len(CustomUser.objects.filter(username=username))>0:
        return render(request,'MMSApp/profile.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 
# Group

@login_required(login_url='/login/')
def Create_Group(request):
    return render(request,'MMSApp/group_cu.html')

@login_required(login_url='/login/')
def Edit_Group(request, group_uuid):
    if len(Group.objects.filter(uuid=group_uuid))>0:
        return render(request,'MMSApp/group_cu.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 
    
@login_required(login_url='/login/')
def Single_Group(request, group_uuid):
    if len(Group.objects.filter(uuid=group_uuid))>0:
        return render(request,'MMSApp/group_rd.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 
# Meeting

@login_required(login_url='/login/')
def Create_Meeting(request,group_uuid):
    if len(Group.objects.filter(uuid=group_uuid))>0:
        return render(request,'MMSApp/meeting_cu.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 

@login_required(login_url='/login/')
def Edit_Meeting(request,meeting_uuid):
    if len(Meeting.objects.filter(uuid=meeting_uuid))>0:
        return render(request,'MMSApp/meeting_cu.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 


@login_required(login_url='/login/')
def Single_Meeting(request,meeting_uuid):
    if len(Meeting.objects.filter(uuid=meeting_uuid))>0:
        return render(request,'MMSApp/meeting_rd.html')
    return HttpResponseNotFound('<h1>Page not found</h1>') 

# Schedule

@login_required(login_url='/login/')
def Get_Schedule(request):
    return render(request,'MMSApp/schedule_crud.html')

# LOGGER

def error():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("\nLINE = :", exc_traceback.tb_lineno)
    formatted_lines = traceback.format_exc().splitlines()
    print("ERROR = ", formatted_lines[-1],end="\n")

# API SECTION BELOW

class Login_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response["status"] = 500

        try:
            data = request.data

            user = authenticate(username=data['username'], password=data['password'])

            if (len(User.objects.filter(username=data['username'])) == 1):
                response['status'] = 200
                login(request, user)
            else:
                response['status'] = 401

        except Exception as e:
            error()
            print("ERROR IN = Login_SubmitAPI", str(e))

        return Response(data=response)

Login_Submit = Login_SubmitAPI.as_view()

class Signup_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data

            if(len(User.objects.filter(username=data['username'])) == 0):
                try:
                    user = CustomUser.objects.create(username=data['username'], email=data['email'], password=data["password"])
                    user.uuid = str(uuid.uuid4())

                    filepath = settings.STATIC_ROOT+'/MMSApp/images/'+data['username'].upper()[0]+'.png'
                    print(filepath)

                    thumb = IMage.open(filepath)
                    im_type = thumb.format
                    thumb_io = BytesIO()
                    thumb.save(thumb_io, format=im_type)

                    thumb_file = InMemoryUploadedFile(thumb_io, None, filepath, 'image/'+im_type, thumb_io.getbuffer(), None)
                    user.dp = thumb_file

                    user.save()
                    response['status'] = 202

                except Exception as e:
                    print(str(e))
                    response['status'] = 400
            else:
                response['status']  = 409

        except Exception as e:
            error()
            print("ERROR = Signup_SubmitAPI", str(e))

        return Response(data=response)

Signup_Submit = Signup_SubmitAPI.as_view()

class Get_All_UsersAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            users = CustomUser.objects.all()

            response['users'] = {}

            for u in users:
                if u.username != user.username:
                    response['users'][u.username] = settings.MEDIA_URL+u.dp.name

            response['status'] = 200

        except Exception as e:
            error()
            print("ERROR IN = Get_User_ListAPI", str(e))

        return Response(data=response)

Get_All_Users = Get_All_UsersAPI.as_view()


class Create_Group_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)

            name = data['name']

            group = Group(name = name)
            group.uuid = str(uuid.uuid4())
            group.save()
            group.admins.add(user)
            group.members.add(user)

            members = json.loads(data['members'])
            admins = json.loads(data['admins'])

            for member in members:
                try:
                    user_obj = CustomUser.objects.get(username = str(member))
                    group.members.add(user_obj)
                except Exception as e:
                    print("error in ", str(e))

            for admin in admins:
                try:
                    user_obj = CustomUser.objects.get(username = str(admin))
                    group.admins.add(user_obj)
                    group.members.add(user_obj)
                except Exception as e:
                    print("error in ", str(e))

            group.save()
            response['status'] = 200

        except Exception as e:
            error()
            print("ERROR IN  = Create_Group_SubmitAPI", str(e))

        return Response(data=response)

Create_Group_Submit = Create_Group_SubmitAPI.as_view()

class Get_User_GroupsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)

            try:
                group_list = user.member.all()

                response['groups'] = []

                for g in group_list:
                    temp = {}
                    temp['uuid'] = g.uuid
                    temp['group_name'] = g.name

                    response['groups'].append(temp)

                response['status']=200

            except Exception as e:
                error()
                print(str(e))
        except Exception as e:
            error()
            print("ERROR IN = Get_User_GroupsAPI", str(e))

        return Response(data=response)

Get_User_Groups = Get_User_GroupsAPI.as_view()


class Get_Group_DetailsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            try:
                try:
                    user = CustomUser.objects.get(username = user.username)
                    group = Group.objects.get(uuid = str(data['uuid']))

                except Exception as e:
                    error()
                    print(str(e))
                    response['status'] = 404

                response['name']   = group.name
                response['admins'] = []
                response['members'] = []
                response['past_meets'] = []
                response['ongoing_meets'] = []
                response['upcoming_meets'] = []
                response['isAdmin'] = "0"
                response['created_date'] = group.get_created_date()

                admin_set = set(group.admins.all())

                for admin in admin_set:
                    temp = {}
                    temp['uuid'] = admin.uuid
                    temp['username'] = admin.username
                    temp['dp'] = settings.MEDIA_URL + admin.dp.name
                    response['admins'].append(temp)

                member_list = group.members.all()

                for member in member_list:
                    if member not in admin_set:
                        temp = {}
                        temp['uuid'] = member.uuid
                        temp['username'] = member.username
                        temp['dp'] = settings.MEDIA_URL + member.dp.name
                        response['members'].append(temp)

                if user in admin_set:
                    response['isAdmin'] = "1"

                past_meets = group.meeting_set.all().filter(end_time__lte = datetime.now())
                ongoing = group.meeting_set.all().filter(start_time__lte = datetime.now(), end_time__gte = datetime.now())
                upcoming = group.meeting_set.all().filter(start_time__gte = datetime.now())

                for meet in past_meets:
                    temp = {}
                    temp['uuid'] = meet.uuid
                    temp['name'] = meet.name
                    temp['agenda'] = meet.agenda
                    temp['meeting_date'] = meet.get_meeting_date()
                    temp['start_time'] = meet.get_start_time()
                    temp['end_time'] = meet.get_end_time()
                    response['past_meets'].append(temp)

                for meet in ongoing:
                    temp = {}
                    temp['uuid'] = meet.uuid
                    temp['name'] = meet.name
                    temp['agenda'] = meet.agenda
                    temp['meeting_date'] = meet.get_meeting_date()
                    temp['start_time'] = meet.get_start_time()
                    temp['end_time'] = meet.get_end_time()
                    response['ongoing_meets'].append(temp)

                for meet in upcoming:
                    temp = {}
                    temp['uuid'] = meet.uuid
                    temp['name'] = meet.name
                    temp['agenda'] = meet.agenda
                    temp['meeting_date'] = meet.get_meeting_date()
                    temp['start_time'] = meet.get_start_time()
                    temp['end_time'] = meet.get_end_time()
                    response['upcoming_meets'].append(temp)

                response['status']=200

            except Exception as e:
                response['status']=400
                print(str(e))

        except Exception as e:
            error()
            print("ERROR IN = Get_Group_DetailsAPI", str(e))

        return Response(data=response)

Get_Group_Details = Get_Group_DetailsAPI.as_view()


class Edit_Group_DetailsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            try:
                try:
                    user = CustomUser.objects.get(username = user.username)
                    group = Group.objects.get(uuid = str(data['uuid']))

                except Exception as e:
                    error()
                    print(str(e))
                    response['status'] = 404

                response['name']   = group.name
                response['admins'] = []
                response['members'] = []

                admin_set = set(group.admins.all())

                for admin in admin_set:
                    if user.username != admin.username:
                        temp = {}
                        temp['uuid'] = admin.uuid
                        temp['username'] = admin.username
                        temp['dp'] = settings.MEDIA_URL + admin.dp.name
                        response['admins'].append(temp)

                member_list = group.members.all()

                for member in member_list:
                    if (member not in admin_set) and (user.username != member.username):
                        temp = {}
                        temp['uuid'] = member.uuid
                        temp['username'] = member.username
                        temp['dp'] = settings.MEDIA_URL + member.dp.name
                        response['members'].append(temp)

                response['status']=200

            except Exception as e:
                error()
                response['status']=400
                print(str(e))

        except Exception as e:
            error()
            print("ERROR IN Edit_Group_DetailsAPI", str(e))

        return Response(data=response)

Edit_Group_Details = Edit_Group_DetailsAPI.as_view()


class Edit_Group_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)

            group_id = str(data['uuid'])
            group = Group.objects.get(uuid = group_id)

            members = json.loads(data['members'])
            admins = json.loads(data['admins'])

            group.name = data['name']
            group.members.clear()
            group.admins.clear()

            group.admins.add(user)
            group.members.add(user)

            for member in members:
                try:
                    user_obj = CustomUser.objects.get(username = str(member))
                    group.members.add(user_obj)
                except Exception as e:
                    error()
                    print("error in ", str(e))

            for admin in admins:
                try:
                    user_obj = CustomUser.objects.get(username = str(admin))
                    group.admins.add(user_obj)
                    group.members.add(user_obj)
                except Exception as e:
                    error()
                    print("error in ", str(e))

            group.save()
            response['status'] = 200

        except Exception as e:
            error()
            print("ERROR IN = Edit_Group_SubmitAPI", str(e))

        return Response(data=response)

Edit_Group_Submit = Edit_Group_SubmitAPI.as_view()


class Create_Meeting_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)
            group = Group.objects.get(uuid = str(data['group_uuid']))
            chatroom    = ChatRoom(name=data['name'])
            chatroom.save()

            m1 = Meeting()

            m1.name        = data['name']
            m1.agenda      = data['agenda']
            m1.group       = group
            m1.start_time  = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['s_hour']),int(data['s_min']))
            m1.end_time    = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['e_hour']),int(data['e_min']))
            m1.meeting_date= date(int(data['year']),int(data['month']),int(data['day']))
            m1.duration    = int(data['duration'])
            m1.venue       = data['venue']
            m1.chatroom    = chatroom
            # resources

            m1.save()

            group = m1.group

            for user in group.members.all():
                try:
                    n1 = Notification.objects.get(user=user,meeting=m1)
                except:
                    n1 = Notification(user=user,meeting=m1)
                    n1.save()

            response['meeting_uuid'] = m1.uuid
            print(m1.start_time)

            response['status']=200
        except Exception as e:
            error()
            print("ERROR IN  = Create_Meeting_SubmitAPI", str(e))

        return Response(data=response)

Create_Meeting_Submit = Create_Meeting_SubmitAPI.as_view()


class Get_Meeting_DetailsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)
            meet = Meeting.objects.get(uuid = data['meeting_uuid'])

            response['name'] = meet.name
            response['agenda'] = meet.agenda
            response['start_time']=[]
            response['end_time']=[]
            response['meeting_date']=[]
            response['meeting_date_str'] = meet.get_meeting_date()
            response['start_time_str'] = meet.get_start_time()
            response['end_time_str'] = meet.get_end_time()
            response['duration']=meet.duration
            response['venue']=meet.venue

            response['start_time'].append(meet.start_time.hour)
            response['start_time'].append(meet.start_time.minute)

            response['end_time'].append(meet.end_time.hour)
            response['end_time'].append(meet.end_time.minute)

            response['meeting_date'].append(meet.meeting_date.day)
            response['meeting_date'].append(meet.meeting_date.month)
            response['meeting_date'].append(meet.meeting_date.year)

            response['group_uuid'] = meet.group.uuid

            print(response['meeting_date'])

            response['status']=200
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_Details", str(e))

        return Response(data=response)

Get_Meeting_Details = Get_Meeting_DetailsAPI.as_view()


class Edit_Meeting_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)

            m1 = Meeting.objects.get(uuid = str(data['meeting_uuid']))

            group = m1.group
            
            for user in group.members.all():
                if user.schedule != None:
                    try:
                        schedule = user.schedule
                        ds = schedule.daily_schedules.all().get(date=m1.meeting_date)
                        e = ds.events.all().get(name=m1.name,start_time=m1.start_time,end_time=m1.end_time)
                        e.delete()
                    except:
                        pass

            m1.name        = data['name']
            m1.agenda      = data['agenda']
            m1.start_time  = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['s_hour']),int(data['s_min']))
            m1.end_time    = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['e_hour']),int(data['e_min']))
            m1.meeting_date= date(int(data['year']),int(data['month']),int(data['day']))
            m1.duration    = int(data['duration'])
            m1.venue       = data['venue']
            # resources
            m1.save()

            for user in group.members.all():
                try:
                    n1 = Notification.objects.get(user=user,meeting=m1)
                except:
                    n1 = Notification(user=user,meeting=m1)
                    n1.save()

            response['meeting_uuid'] = m1.uuid
            response['name'] = m1.name
            print(m1.start_time)

            response['status']=200
        except Exception as e:
            error()
            print("ERROR IN  = Edit_Meeting_SubmitAPI", str(e))

        return Response(data=response)

Edit_Meeting_Submit = Edit_Meeting_SubmitAPI.as_view()

class Delete_MeetingAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            user = CustomUser.objects.get(username = user.username)

            m1 = Meeting.objects.get(uuid = str(data['meeting_uuid']))

            group = m1.group
            
            for user in group.members.all():
                if user.schedule != None:
                    try:
                        schedule = user.schedule
                        ds = schedule.daily_schedules.all().get(date=m1.meeting_date)
                        e = ds.events.all().get(name=m1.name,start_time=m1.start_time,end_time=m1.end_time)
                        e.delete()
                    except:
                        pass

            for user in group.members.all():
                try:
                    n1 = Notification.objects.get(user=user,meeting=m1)
                    n1.delete()
                except:
                    pass

            m1.delete()
            response['group_uuid'] = group.uuid
            response['status']=200
        except Exception as e:
            error()
            print("ERROR IN  = Edit_Meeting_SubmitAPI", str(e))

        return Response(data=response)

Delete_Meeting = Delete_MeetingAPI.as_view()


class Get_Monthly_ScheduleAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user

            month = int(data['month'])
            year = int(data['year'])

            user = CustomUser.objects.get(username = user.username)

            day1,days = monthrange(year,month)

            response['schedule'] = []
            for i in range(days+1):
                response['schedule'].append("")

            # uncomment for testing
            # s = Schedule()
            # s.save()
            # d = DailySchedule(date=datetime(year,month,2))
            # d.save()
            #
            # d2 = DailySchedule(date=datetime(year,month,4))
            # d2.save()
            #
            # e1 = Event(name="Event1",venue="v1",start_time=datetime.now(),end_time=datetime.now()+timedelta(hours=2))
            # e1.save()
            #
            # e2 = Event(name="Event2",venue="v2",start_time=datetime.now()+timedelta(hours=1),end_time=datetime.now()+timedelta(hours=2))
            # e2.save()
            #
            # e3 = Event(name="Event3",venue="v3",start_time=datetime.now(),end_time=datetime.now()+timedelta(hours=2))
            # e3.save()
            #
            # e4 = Event(name="Event3",venue="v3",start_time=datetime.now(),end_time=datetime.now()+timedelta(hours=2))
            # e4.save()
            #
            # d.events.add(e1)
            # d.events.add(e2)
            # d.events.add(e3)
            # d.save()
            # d2.events.add(e4)
            # d2.save()
            # s.daily_schedules.add(d)
            # s.daily_schedules.add(d2)
            # s.save()
            #
            # user.schedule = s
            # user.save()
            #
            # print(user.schedule.daily_schedules.all())

            if(user.schedule!=None):

                d1 = datetime(year,month,1)
                d2 = datetime(year,month,days)

                schedule = user.schedule
                query_list = list(schedule.daily_schedules.all().filter(date__gte=d1,date__lte=d2))

                for daily in query_list:

                    events = list(daily.events.all().order_by('start_time'))

                    if(len(events)>0):
                        i = daily.date.day

                        response['schedule'][i] = {}
                        response['schedule'][i]['date_uuid'] = daily.uuid
                        response['schedule'][i]['events']=[]

                        for event in events:
                            temp = {}
                            temp['uuid'] = event.uuid
                            temp['name'] = event.name
                            temp['start_time'] = event.get_start_time()
                            temp['end_time'] = event.get_end_time()
                            temp['venue'] = event.venue
                            temp['description'] = event.description
                            response['schedule'][i]['events'].append(temp)

            response['status']=200
            response['first_day'] = day1
            response['days'] = days

        except Exception as e:
            error()
            print("ERROR IN  = Get_Monthly_ScheduleAPI", str(e))

        return Response(data=response)

Get_Monthly_Schedule = Get_Monthly_ScheduleAPI.as_view()


class Edit_Schedule_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            response,old_start,old_end,old_name = save_event(user,data,True)

            if response['status'] == 200:
                if (data['change_all']=="true"):
                    print(data['change_all'])
                    till_date = datetime(data['till_year'],data['till_month'],data['till_day'])

                    ds_day = int(data['ds_day'])
                    ds_month = int(data['ds_month'])
                    ds_year = int(data['ds_year'])
                    next_date = datetime(ds_year,ds_month,ds_day)+timedelta(days=7)

                    while(next_date<=till_date):
                        data['ds_day'] = next_date.day
                        data['ds_month'] = next_date.month
                        data['ds_year'] = next_date.year
                        data['ds_uuid'] = ""
                        save_event(user,data,False,old_start,old_end,old_name)

        except Exception as e:
            error()
            print("ERROR IN  = Edit_Schedule_SubmitAPI", str(e))

        return Response(data=response)

Edit_Schedule_Submit = Edit_Schedule_SubmitAPI.as_view()


def save_event(user,data,isFirst,old_start_time=0,old_end_time=0,old_name=""):

    response = {}
    response['status'] = 500

    print(data)

    ds_uuid = data['ds_uuid']
    ds_day = int(data['ds_day'])
    ds_month = int(data['ds_month'])
    ds_year = int(data['ds_year'])

    event = json.loads(data['event'])

    if(user.schedule==None):

        s = Schedule()
        s.save()
        user.schedule = s
        user.save()

    ds_date = datetime(ds_year,ds_month,ds_day)

    schedule = user.schedule

    if(ds_uuid==""):

        try:
            ds = schedule.daily_schedules.all().get(date = ds_date)
        except:
            error()
            ds = DailySchedule(date=datetime(ds_year,ds_month,ds_day))
            ds.save()
            schedule.daily_schedules.add(ds)
    else:

        ds = DailySchedule.objects.get(uuid=ds_uuid)

    # print(event['s_hour'])

    start_time = datetime(ds_year,ds_month,ds_day,int(event['s_hour']),int(event['s_min']))
    end_time = datetime(ds_year,ds_month,ds_day,int(event['e_hour']),int(event['e_min']))
    # end_time = start_time+timedelta(hours=1)
    print(start_time,end_time)
    if(event['is_deleted']):
        if isFirst:
            try:
                e = ds.events.all().get(uuid = event['uuid'])
                old_start_time,old_end_time,old_name = e.start_time,e.end_time,e.name
                e.delete()
            except:
                error()
                return response,0,0,0
        else:
            try:
                e = ds.events.all().get(start_time=old_start_time,end_time=old_end_time,name=old_name)
                e.delete()
            except:
                error()
                return response
        response['status'] = 200
    else:
        if(event['is_edited']):
            if isFirst:
                try:
                    e = ds.events.all().get(uuid = event['uuid'])
                except:
                    error()
                    return response,0,0,0
            else:
                try:
                    e = ds.events.all().get(start_time=old_start_time,end_time=old_end_time,name=old_name)
                except:
                    error()
                    return response
            # print("herer")
        else:
            e = Event()
            e.start_time = start_time
            e.end_time = end_time
            e.venue = event['venue']
            e.name = event['name']
            e.description = event['description']
        if isFirst:
            old_start_time = e.start_time
            old_end_time = e.end_time
            old_name = e.name

        if isFirst:
            clash = ds.events.all().filter(start_time__lt=end_time).exclude(uuid=e.uuid)
            # print(clash)
            clash = clash.exclude(end_time__lte=start_time)
            # print(clash)
        else:
            clash = ds.events.all().filter(start_time__lt=old_end_time).exclude(uuid=e.uuid)
            clash = clash.exclude(end_time__lte=old_start_time)

        # print("here")
        response['clash'] = []

        if(len(clash)>0):
            response['status'] = 409
            for event in clash:
                response['clash'].append(event.name)
            return response,0,0,0
        else:

            e.name = event['name']
            e.venue = event['venue']
            e.start_time = start_time
            e.end_time = end_time
            e.description = event['description']
            e.save()

            if (not event['is_edited']):
                ds.events.add(e)
            response['status']=200

    if isFirst:
        return response,old_start_time,old_end_time,old_name
    else:
        return response


class Get_User_MeetingsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            response['past_meets'] = []
            response['ongoing_meets'] = []
            response['upcoming_meets'] = []

            groups = Group.objects.filter(members__username=user.username)

            meetings = Meeting.objects.filter(group__in=groups)


            past_meets = meetings.filter(end_time__lte = datetime.now())
            ongoing = meetings.filter(start_time__lte = datetime.now(), end_time__gte = datetime.now())
            upcoming = meetings.filter(start_time__gte = datetime.now())

            for meet in past_meets:
                temp = {}
                temp['uuid'] = meet.uuid
                temp['name'] = meet.name
                temp['agenda'] = meet.agenda
                temp['meeting_date'] = meet.get_meeting_date()
                temp['start_time'] = meet.get_start_time()
                temp['end_time'] = meet.get_end_time()
                response['past_meets'].append(temp)

            for meet in ongoing:
                temp = {}
                temp['uuid'] = meet.uuid
                temp['name'] = meet.name
                temp['agenda'] = meet.agenda
                temp['meeting_date'] = meet.get_meeting_date()
                temp['start_time'] = meet.get_start_time()
                temp['end_time'] = meet.get_end_time()
                response['ongoing_meets'].append(temp)

            for meet in upcoming:
                temp = {}
                temp['uuid'] = meet.uuid
                temp['name'] = meet.name
                temp['agenda'] = meet.agenda
                temp['meeting_date'] = meet.get_meeting_date()
                temp['start_time'] = meet.get_start_time()
                temp['end_time'] = meet.get_end_time()
                response['upcoming_meets'].append(temp)

            response["status"] = 200

        except Exception as e:
            error()
            print("ERROR IN  = Edit_Schedule_SubmitAPI", str(e))

        return Response(data=response)

Get_User_Meetings = Get_User_MeetingsAPI.as_view()


class Resource_SubmitAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            meeting_uuid = data['meeting_uuid']
            resource = data['resource']
            name = data['name']

            meeting = Meeting.objects.get(uuid = meeting_uuid)
            group = meeting.group

            if user in group.admins.all():
                r = Resource(owner=user,rfile=resource,name=name)
                r.save()
                meeting.resources.add(r)
                response['status'] = 200
                response['file_owner'] = user.username
                response['file_path'] = settings.MEDIA_URL+r.rfile.name
                response['file_name'] = r.name
            else:
                response['status'] = 400

        except Exception as e:
            error()
            print("ERROR IN  = resources submit api", str(e))

        return Response(data=response)

Resource_Submit = Resource_SubmitAPI.as_view()


class Resource_DeleteAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            meeting_uuid = data['meeting_uuid']
            r_uuid = data['r_uuid']

            meeting = Meeting.objects.get(uuid = meeting_uuid)
            group = meeting.group

            if user in group.admins.all():
                r = Resource.objects.get(uuid=r_uuid)
                r.delete()
                response['status'] = 200
            else:
                response['status'] = 200
        except Exception as e:
            error()
            print("ERROR IN  = Resource_DeleteAPI", str(e))

        return Response(data=response)

Resource_Delete = Resource_DeleteAPI.as_view()


class Get_Meeting_ResourcesAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            meeting_uuid = data['meeting_uuid']
            meeting = Meeting.objects.get(uuid = meeting_uuid)

            if user in list(meeting.group.members.all()):
                response['resources'] = []
                # print("here")
                resources = list(meeting.resources.all())
                for r in resources:
                    temp = {}
                    temp['owner'] = r.owner.username
                    temp['owner_uuid'] = r.owner.uuid
                    temp['file_path'] = settings.MEDIA_URL+r.rfile.name
                    temp['file_name'] = r.name
                    temp['file_uuid'] = r.uuid
                    response['resources'].append(temp)
                response['status'] = 200
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Get_Meeting_Resources = Get_Meeting_ResourcesAPI.as_view()

class Get_NotificationsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            notifications = Notification.objects.filter(user=user)

            response['notifs'] = []

            for notif in notifications:
                temp = {}
                temp['meeting_name'] = notif.meeting.name
                temp['meeting_uuid'] = notif.meeting.uuid
                response['notifs'].append(temp)
            
            response['status'] = 200

        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Get_Notifications = Get_NotificationsAPI.as_view()

class Submit_NotificationAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            meeting_uuid = data['meeting_uuid']
            choice = data['choice']
            try:
                meeting = Meeting.objects.get(uuid = meeting_uuid)
                notif = Notification.objects.get(user=user,meeting=meeting)

                if choice == "Yes":
                    meeting.attendees.add(user)
                    meeting.save()
                    meeting_date = meeting.meeting_date
                    
                    if user.schedule == None:
                        schedule = Schedule()
                        schedule.save()
                        user.schedule = schedule
                        user.save()

                    schedule = user.schedule
                    try:
                        ds = schedule.daily_schedules.all().get(date=meeting_date)
                    except:
                        ds = DailySchedule(date=meeting_date)
                        ds.save()
                        schedule.daily_schedules.add(ds)
                        schedule.save()
                    
                    meeting_event = Event(name=meeting.name,start_time = meeting.start_time,end_time=meeting.end_time)
                    meeting_event.save()
                    ds.events.add(meeting_event)
                    ds.save()
                
                notif.delete()
                response['status'] = 200
            except Exception as e:
                print(str(e))
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Submit_Notification = Submit_NotificationAPI.as_view()


class Get_Meeting_AttendeesAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            meeting_uuid = data['meeting_uuid']
           
            try:
                meeting = Meeting.objects.get(uuid=meeting_uuid)

                response['attendees'] = []

                for user in list(meeting.attendees.all()):
                    temp = {}
                    temp['user_uuid'] = user.uuid
                    temp['user_name'] = user.username
                    temp['is_admin'] = False
                    
                    if user in meeting.group.admins.all():
                        temp['is_admin'] = True
                    
                    response['attendees'].append(temp)

                response['status'] = 200
            except Exception as e:
                print(str(e))

            except Exception as e:
                print(str(e))
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Get_Meeting_Attendees = Get_Meeting_AttendeesAPI.as_view()


class Get_User_ProfileAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = data['username'])

            response['username'] = user.username
            response['email']    = user.email
            user_groups = user.member.all()
            response['total_groups'] = len(user_groups)
            # print(user_groups)
            user_meetings = Meeting.objects.filter(group__in=user_groups)
            # print(user_meetings)
            response['total_meetings'] = len(user_meetings)
            response['user_dp'] = settings.MEDIA_URL+user.dp.name
            response['status'] = 200
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Get_User_Profile = Get_User_ProfileAPI.as_view()


class Leave_GroupAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            group_uuid = data['group_uuid']
            group = Group.objects.get(uuid = group_uuid)

            group.admins.remove(user)
            group.members.remove(user)
            group.save()

            if(len(group.members.all())==0):
                group.delete()
            elif(len(group.admins.all())==0):
                group.admins.add(group.members.first())

            response['status'] = 200
        except Exception as e:
            error()
            print("ERROR IN  = Get_Meeting_ResourcesAPI", str(e))

        return Response(data=response)

Leave_Group = Leave_GroupAPI.as_view()


class Get_Free_Time_SlotsAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            user = request.user
            user = CustomUser.objects.get(username = user.username)

            group_uuid = data['group_uuid']
            group = Group.objects.get(uuid = group_uuid)
            duration = int(data['duration'])  # In minutes
            year = int(data['year'])
            month = int(data['month'])
            day = int(data['day'])
            delta = int(data['delta'])  # In minutes
            meeting_date = datetime(year,month,day)

            assert duration<=12*60  # assuming duation is 8 to  20

            start_time  = datetime( year, month, day , 8 , 0 )
            end_time  = datetime( year, month, day, 8+duration//60 , duration%60 )

            end_of_day =  datetime( year, month, day, 20 , 0 )

            if user in group.members.all():
                response['time_slots'] = []
                while end_time<=end_of_day:
                    flag = True
                    for user in group.members.all():
                        try:
                            for event in user.schedule.daily_schedules.all().get(date = meeting_date).events.all():
                                start_time2 = datetime( year, month, day, event.start_time.hour, event.start_time.minute )
                                end_time2 = datetime( year, month, day, event.end_time.hour, event.end_time.minute )
                                if end_time<=start_time2 or end_time2<=start_time:
                                    continue
                                else:
                                    flag = False
                                    break
                            if flag==False:
                                break
                        except:
                            pass
                    if flag == True:
                        time_slot = {}
                        time_slot['start_time'] = start_time.strftime("%I:%M %p" )
                        time_slot['end_time'] = end_time.strftime("%I:%M %p" )
                        response['time_slots'].append(time_slot)

                    start_time = start_time + timedelta(minutes = delta)
                    end_time = end_time + timedelta(minutes = delta)
                response['status'] = 200
        except Exception as e:
            error()
            print("ERROR IN  = Get_Free_Time_SlotsAPI", str(e))

        return Response(data=response)

Get_Free_Time_Slots = Get_Free_Time_SlotsAPI.as_view()

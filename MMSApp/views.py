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
from django.http import HttpResponse, HttpResponseRedirect

import json
import uuid
from datetime import datetime,time,date

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

@login_required(login_url='/login/')
def Create_Group(request):
    return render(request,'MMSApp/group_cu.html')

@login_required(login_url='/login/')
def Edit_Group(request, group_uuid):
    return render(request,'MMSApp/group_cu.html')

@login_required(login_url='/login/')
def Single_Group(request, group_uuid):
    return render(request,'MMSApp/group_rd.html')

@login_required(login_url='/login/')
def Create_Meeting(request,group_uuid):
    return render(request,'MMSApp/meeting_cu.html')

@login_required(login_url='/login/')
def Edit_Meeting(request,meeting_uuid):
    return render(request,'MMSApp/meeting_cu.html')

@login_required(login_url='/login/')
def Single_Meeting(request,meeting_uuid):
    return render(request,'MMSApp/meeting_rd.html')

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
                    response['users'][u.username] = settings.MEDIA_ROOT+u.dp.name

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

            print(members)
            print(admins)

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
            print("group saved")
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
                response['status']=200
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
                    temp['time'] = meet.get_time()
                    response['past_meets'].append(temp)

                for meet in ongoing:
                    temp = {}
                    temp['uuid'] = meet.uuid
                    temp['name'] = meet.name
                    temp['agenda'] = meet.agenda
                    temp['time'] = meet.get_time()
                    response['ongoing_meets'].append(temp)

                for meet in upcoming:
                    temp = {}
                    temp['uuid'] = meet.uuid
                    temp['name'] = meet.name
                    temp['agenda'] = meet.agenda
                    temp['time'] = meet.get_time()
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
                response['status']=400
                print(str(e))

        except Exception as e:
            formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
            print(formatter)
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
                    print("error in ", str(e))

            for admin in admins:
                try:
                    user_obj = CustomUser.objects.get(username = str(admin))
                    group.admins.add(user_obj)
                    group.members.add(user_obj)
                except Exception as e:
                    print("error in ", str(e))

            group.save()
            print("edited group saved")
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
            print("the id",data['group_uuid'],"okay?")
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
            meet = Meeting.objects.get(uuid = data['uuid'])

            response['name'] = meet.name
            response['agenda'] = meet.agenda
            response['start_time']=[]
            response['end_time']=[]
            response['meeting_date']=[]
            response['duration']=meet.duration
            response['venue']=meet.venue

            response['start_time'].append(meet.start_time.hour)
            response['start_time'].append(meet.start_time.minute)

            response['end_time'].append(meet.end_time.hour)
            response['end_time'].append(meet.end_time.minute)

            response['meeting_date'].append(meet.meeting_date.day)
            response['meeting_date'].append(meet.meeting_date.month)
            response['meeting_date'].append(meet.meeting_date.year)

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

            m1 = Meeting.objects.get(uuid = str(data['uuid']))

            m1.name        = data['name']
            m1.agenda      = data['agenda']
            m1.start_time  = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['s_hour']),int(data['s_min']))
            m1.end_time    = datetime(int(data['year']),int(data['month']),int(data['day']),int(data['e_hour']),int(data['e_min']))
            m1.meeting_date= date(int(data['year']),int(data['month']),int(data['day']))
            m1.duration    = int(data['duration'])
            m1.venue       = data['venue']
            # resources

            m1.save()
            response['meeting_uuid'] = m1.uuid
            response['name'] = m1.name
            print(m1.start_time)

            response['status']=200
        except Exception as e:
            error()
            print("ERROR IN  = Edit_Meeting_SubmitAPI", str(e))

        return Response(data=response)

Edit_Meeting_Submit = Edit_Meeting_SubmitAPI.as_view()

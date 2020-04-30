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
            print("ERROR IN Login_SubmitAPI", str(e))

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
                    user.save()
                    response['status'] = 202

                except:
                    response['status'] = 400
            else:
                response['status']  = 409

        except Exception as e:
            print("ERROR IN Signup_SubmitAPI", str(e))

        return Response(data=response)

Signup_Submit = Signup_SubmitAPI.as_view()

class Get_All_UsersAPI(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data

            users = CustomUser.objects.all()

            response['users'] = {}

            for user in users:
                response['users'][user.username] = 1

            response['status'] = 200

        except Exception as e:
            print("ERROR IN Get_User_ListAPI", str(e))

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
            members = json.loads(data['members'])

            group = Group(name = name)
            group.admins.add(user)
            group.uuid = str(uuid.uuid4())
            group.save()

            for member in members:
                print(member)
                try:
                    user_obj = CustomUser.objects.get(username = str(member))
                    # print(user_obj)
                    group.members.add(user_obj)
                except Exception as e:
                    print("error in ", str(e))

            group.save()
            print("group saved")
            response['status'] = 200

        except Exception as e:
            print("ERROR IN Create_Group_SubmitAPI", str(e))

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

            group_list = user.member.all()

            response['group_list'] = []

            for g in group_list:
                temp = {}
                temp['uuid'] = g.uuid
                temp['group_name'] = g.name

                response['group_list'].append(temp)

            response['status']=200

        except Exception as e:
            print("ERROR IN Get_User_GroupsAPI", str(e))

        return Response(data=response)

Get_User_Groups = Get_User_GroupsAPI.as_view()


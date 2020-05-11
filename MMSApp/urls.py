from django.urls import path
from . import views

urlpatterns = [

    path('', views.Home),
    path('home/', views.Home),
    # Authentication
    path('login/', views.Login),
    path('logout/', views.Logout),
    path('signup/', views.Signup),
    path('login_submit/', views.Login_Submit),
    path('signup_submit/', views.Signup_Submit),
    # Users
    path('Get_All_Users/', views.Get_All_Users),
    # Group
    path('create/group/', views.Create_Group),
    path('edit/group/<str:group_uuid>/', views.Edit_Group),
    path('Create_Group_Submit/', views.Create_Group_Submit),
    path('Edit_Group_Submit/', views.Edit_Group_Submit),
    path('Edit_Group_Details/', views.Edit_Group_Details),
    path('Get_User_Groups/',views.Get_User_Groups),
    path('groups/<str:group_uuid>/', views.Single_Group),
    path('Get_Group_Details/', views.Get_Group_Details),
    # Meeting
    path('create/meeting/<str:group_uuid>/', views.Create_Meeting),
    path('edit/meeting/<str:meeting_uuid>/', views.Edit_Meeting),
    path('Create_Meeting_Submit/',views.Create_Meeting_Submit),
    path('meetings/<str:meeting_uuid>/', views.Single_Meeting),
    path('Get_Meeting_Details/',views.Get_Meeting_Details),
    path('Edit_Meeting_Submit/',views.Edit_Meeting_Submit),
]

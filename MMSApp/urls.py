from django.urls import path
from . import views

urlpatterns = [

    path('', views.Home),
    path('home/', views.Home),
    path('login/', views.Login),
    path('logout/', views.Logout),
    path('signup/', views.Signup),
    path('login_submit/', views.Login_Submit),
    path('signup_submit/', views.Signup_Submit),
    path('Get_All_Users/', views.Get_All_Users),
    path('Create_Group_Submit/', views.Create_Group_Submit),
    path('Edit_Group_Submit/', views.Edit_Group_Submit),
    path('Edit_Group_Details/', views.Edit_Group_Details),
    path('Get_User_Groups/',views.Get_User_Groups),
    path('groups/<str:group_uuid>/', views.Single_Group),
    path('create/group/', views.Create_Group),
    path('edit/group/<str:group_uuid>/', views.Edit_Group),
    path('Get_Group_Details/', views.Get_Group_Details),
    path('create/meeting/', views.Create_Meeting),
    path('meetings/<str:meeting_uuid>/', views.Single_Meeting),
]

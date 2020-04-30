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
    path('Get_User_Groups/',views.Get_User_Groups),
    # path('group/<str:group_uuid>/', views.Single_Group),

]

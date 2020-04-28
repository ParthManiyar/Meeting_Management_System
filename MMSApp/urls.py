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
    # path('group/<str:group_uuid>/', views.Group),
]

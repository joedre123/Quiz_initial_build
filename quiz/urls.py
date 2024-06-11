from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name='all-quizes'), #this will trigger challenges/
    path("register/", views.register, name='register'),
    path('login/', views.user_login, name='login'),
    #path("login/", auth_views.LoginView.as_view(template_name='quiz/login.html'), name='login'),  # Login URL
    path("leaderboard/", views.leaderboard, name='leaderboard'),  # Leaderboard URL
    path("<str:quiz>/", views.quizes, name="quiz"),
    
   
    #path("<str:quiz>/quiz_data/", views.quizes, name='quizes'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('contest/<int:contest_id>/',views.contest_leaderboard,name='contest_leaderboard'),
    path('contest/<int:contest_id>/check_similarity/', views.check_similarity, name='check_similarity'),
    path('user/<int:user_id>/contest/<int:contest_id>/submissions/', views.user_submissions, name='user_submissions'),  
]
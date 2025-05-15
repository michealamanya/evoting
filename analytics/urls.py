from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('election/<int:election_id>/', views.election_analytics, name='election_analytics'),
    path('voter-demographics/', views.voter_demographics, name='voter_demographics'),
    path('participation-trends/', views.participation_trends, name='participation_trends'),
    path('reports/', views.analytics_reports, name='analytics_reports'),
]

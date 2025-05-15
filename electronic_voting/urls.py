from django.urls import path
from . import views

urlpatterns = [
    path('', views.election_list, name='election_list'),
    path('<int:election_id>/', views.election_detail, name='election_detail'),
    path('<int:election_id>/position/<int:position_id>/vote/', views.vote_position, name='vote_position'),
    path('<int:election_id>/vote/', views.vote_all, name='vote_all'),
    path('<int:election_id>/results/', views.election_results, name='election_results'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Organisation endpoints
    path('organisation/register/', views.RegisterOrganisationView, name='register-organisation'),
    path('organisation/<str:params>/', views.organisation_details, name='organisation-details'),
    path('organisation-details/<str:params>/', views.organisation_details, name='organisation-details-direct'),

    # Group endpoints
    path('create/', views.CreateGroup, name='create-group'),
    path('create-group/', views.CreateGroup, name='create-group-direct'),
    path('group-details/<str:params>/', views.group_details, name='group-details-direct'),
    path('show-members/<str:params>/', views.show_members, name='show-members-direct'),
    path('<str:params>/add-member/<str:username>/', views.add_member_group, name='add-member-group'),
    path('<str:params>/members/', views.show_members, name='show-members'),
    path('<str:params>/', views.group_details, name='group-details'),
]

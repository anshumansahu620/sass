from django.shortcuts import render
from  .serializers import RegisterOrganisationSerializer,CreateGroupSerializer
from rest_framework.decorators import api_view,permission_classes 

from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Organisation, Group

from rest_framework.response import Response


# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])

def RegisterOrganisationView(request):
    if request.method=='POST':
        user=request.user
        seriaiizer=RegisterOrganisationSerializer(data=request.data)
        if seriaiizer.is_valid():
            seriaiizer.save(owner=user)
            return Response(data=seriaiizer.data,status=201)  
        return Response(seriaiizer.errors,status=400)    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def CreateGroup(request):
    if request.method=='POST':
        seriaiizer=CreateGroupSerializer(data=request.data)
        if seriaiizer.is_valid():
            seriaiizer.save()
            return Response(data=seriaiizer.data,status=201)  
        return Response(seriaiizer.errors,status=400)   

    

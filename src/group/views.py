from django.shortcuts import render
from  .serializers import RegisterOrganisationSerializer,CreateGroupSerializer
from rest_framework.decorators import api_view,permission_classes 

from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Organisation, Group

from rest_framework.response import Response
from rest_framework import status


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
    serializer = CreateGroupSerializer(data=request.data)

    if serializer.is_valid():
        organisation = serializer.validated_data["organisation"]

        if organisation.owner != request.user:
            return Response(
                {"detail": "You do not own this organisation."},
                status=status.HTTP_403_FORBIDDEN
            )

        group = serializer.save()

        return Response(
            CreateGroupSerializer(group).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

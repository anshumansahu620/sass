from django.shortcuts import render
from .serializers import RegisterOrganisationSerializer, CreateGroupSerializer, GroupDetails, AddGroupMembersSerializer
from rest_framework.decorators import api_view,permission_classes 

from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Organisation, Group, GroupMember

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])

def RegisterOrganisationView(request):
    
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
        GroupMember.objects.create(
            group=group,
            user=request.user,
            role=GroupMember.Role.ADMIN
        )

        return Response(
            CreateGroupSerializer(group).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_details(request,params):
    group=Group.objects.filter(id=params)
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer=GroupDetails(group)
    return Response(serializer.data, status=status.HTTP_200_OK)

    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def organisation_details(request,params):
    group=Organisation.objects.filter(org_id=params)
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer=CreateGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)
     
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_members(request,params):
    group=Group.objects.filter(group_id=params)
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer=CreateGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_group(request, params, username):
    # Check whether the new member exists
    new_member = User.objects.filter(username=username).first()
    if not new_member:
        return Response({"error": "No User Found"}, status=status.HTTP_404_NOT_FOUND)

    # Check whether the group exists
    group = Group.objects.filter(id=params).first()
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verify the requesting user's role in this group
    is_admin = GroupMember.objects.filter(
        group=group,
        user=request.user,
        role=GroupMember.Role.ADMIN
    ).exists()

    if is_admin:
        if GroupMember.objects.filter(group=group, user=new_member).exists():
            return Response(
                {"detail": "User is already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )

        role = request.data.get('role', GroupMember.Role.MEMBER)
        if role not in GroupMember.Role.values:
            role = GroupMember.Role.MEMBER

        member = GroupMember.objects.create(
            group=group,
            user=new_member,
            role=role
        )
        serializer = AddGroupMembersSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(
        {"detail": "You do not have permission to add members to this group."},
        status=status.HTTP_403_FORBIDDEN
    )
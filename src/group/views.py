from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import AppUser
from .models import Organisation, Group, GroupMember
from .utils import IsOwner, IsGroupAdmin
from .serializers import (
    RegisterOrganisationSerializer,
    OrganisationDetailsSerializer,
    CreateGroupSerializer,
    GroupDetailsSerializer,
    GroupMemberSerializer,
    GroupDetails,
    AddGroupMembersSerializer,
)

User = get_user_model()


# ============================================================================
# Swagger / OpenAPI Schema Definitions
# ============================================================================

ORGANISATION_REGISTER_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['org_name'],
    properties={
        'org_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Name of the organisation',
            example='Acme Technologies',
        ),
        'bio': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Short description / biography of the organisation',
            example='Building enterprise-grade cloud solutions.',
        ),
        'logo': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Organisation logo image (URL or uploaded file)',
            example='https://example.com/media/logos/acme.png',
        ),
    },
)

GROUP_CREATE_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['organisation', 'group_name'],
    properties={
        'organisation': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description='UUID of the parent organisation',
            example='c7a0d4c8-3e54-4f51-b847-fcf81db6028a',
        ),
        'group_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Name of the group',
            example='Backend Engineering',
        ),
        'group_logo': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Group icon / logo image (URL or uploaded file)',
            example='https://example.com/media/group/icons/backend.png',
        ),
    },
)

ADD_MEMBER_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'role': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['admin', 'member'],
            default='member',
            description='Role of the member in the group (choices: admin, member)',
            example='member',
        ),
    },
)

# Standard Response Schemas
SCHEMA_ERROR_400 = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description='Validation Error / Bad Request',
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Invalid input provided.'),
        'error': openapi.Schema(type=openapi.TYPE_STRING, example='User is already a member of this group.'),
    },
)

SCHEMA_ERROR_401 = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description='Unauthorized Error',
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Authentication credentials were not provided.'),
    },
)

SCHEMA_ERROR_403 = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description='Forbidden Error',
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING, example='You do not have permission to perform this action.'),
    },
)

SCHEMA_ERROR_404 = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description='Not Found Error',
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, example='Resource not found'),
    },
)

# Path Parameters
PARAM_ORG_ID = openapi.Parameter(
    name='params',
    in_=openapi.IN_PATH,
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_UUID,
    required=True,
    description='Organisation ID (UUID)',
    example='c7a0d4c8-3e54-4f51-b847-fcf81db6028a',
)

PARAM_GROUP_ID = openapi.Parameter(
    name='params',
    in_=openapi.IN_PATH,
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_UUID,
    required=True,
    description='Group ID (UUID)',
    example='e2b1f8c3-4d76-4f82-a931-1e9bf4380123',
)

PARAM_USERNAME = openapi.Parameter(
    name='username',
    in_=openapi.IN_PATH,
    type=openapi.TYPE_STRING,
    required=True,
    description='Username of the registered user to add as member',
    example='john_doe',
)


# Helper function
def get_or_create_app_user(user):
    """Retrieve or create the corresponding AppUser record for a django User."""
    app_user = AppUser.objects.filter(user=user).first()
    if not app_user:
        app_user, _ = AppUser.objects.get_or_create(user=user)
    return app_user


# ============================================================================
# Organisation Endpoints
# ============================================================================

@swagger_auto_schema(
    method='post',
    operation_summary='Register a new organisation',
    operation_description=(
        'Create a new organisation. Requires JWT authentication.\n\n'
        'The authenticated user is automatically set as the owner of this organisation.'
    ),
    tags=['Organisations'],
    security=[{'Bearer': []}],
    request_body=ORGANISATION_REGISTER_BODY,
    consumes=['application/json'],
    produces=['application/json'],
    responses={
        201: openapi.Response('Organisation created successfully', RegisterOrganisationSerializer),
        400: openapi.Response('Validation error', SCHEMA_ERROR_400),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def RegisterOrganisationView(request):
    app_user = get_or_create_app_user(request.user)
    serializer = RegisterOrganisationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=app_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_summary='Get organisation details',
    operation_description='Retrieve details of an organisation by its UUID. Requires JWT authentication.',
    tags=['Organisations'],
    security=[{'Bearer': []}],
    manual_parameters=[PARAM_ORG_ID],
    produces=['application/json'],
    responses={
        200: openapi.Response('Organisation details', OrganisationDetailsSerializer),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
        404: openapi.Response('Organisation not found', SCHEMA_ERROR_404),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def organisation_details(request, params):
    organisation = Organisation.objects.filter(id=params).first()
    if not organisation:
        return Response(
            {"error": "Organisation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = OrganisationDetailsSerializer(organisation)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# Group Endpoints
# ============================================================================

@swagger_auto_schema(
    method='post',
    operation_summary='Create a new group',
    operation_description=(
        'Create a new group within an organisation. Requires JWT authentication.\n\n'
        '**Rules:**\n'
        '- The authenticated user must be the **owner** of the specified organisation.\n'
        '- The creator is automatically added as an **ADMIN** member of the group.'
    ),
    tags=['Groups'],
    security=[{'Bearer': []}],
    request_body=GROUP_CREATE_BODY,
    consumes=['application/json'],
    produces=['application/json'],
    responses={
        201: openapi.Response('Group created successfully', GroupDetailsSerializer),
        400: openapi.Response('Validation error', SCHEMA_ERROR_400),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
        403: openapi.Response('Forbidden - User does not own this organisation', SCHEMA_ERROR_403),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def CreateGroup(request):
    serializer = CreateGroupSerializer(data=request.data)
    if serializer.is_valid():
        organisation = serializer.validated_data["organisation"]
        app_user = get_or_create_app_user(request.user)

        if organisation.owner != app_user:
            return Response(
                {"detail": "You do not own this organisation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        group = serializer.save(group_admin=app_user)
        GroupMember.objects.get_or_create(
            group=group,
            user=app_user,
            defaults={'role': GroupMember.Role.ADMIN},
        )

        return Response(
            GroupDetailsSerializer(group).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@swagger_auto_schema(
    method='get',
    operation_summary='Get group details',
    operation_description='Retrieve details of a group by its UUID. Requires JWT authentication.',
    tags=['Groups'],
    security=[{'Bearer': []}],
    manual_parameters=[PARAM_GROUP_ID],
    produces=['application/json'],
    responses={
        200: openapi.Response('Group details', GroupDetailsSerializer),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
        404: openapi.Response('Group not found', SCHEMA_ERROR_404),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_details(request, params):
    group = Group.objects.filter(id=params).first()
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = GroupDetailsSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# Group Members Endpoints
# ============================================================================

@swagger_auto_schema(
    method='get',
    operation_summary='List group members',
    operation_description='Retrieve all members belonging to the specified group. Requires JWT authentication.',
    tags=['Group Members'],
    security=[{'Bearer': []}],
    manual_parameters=[PARAM_GROUP_ID],
    produces=['application/json'],
    responses={
        200: openapi.Response('List of group members', GroupMemberSerializer(many=True)),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
        404: openapi.Response('Group not found', SCHEMA_ERROR_404),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_members(request, params):
    group = Group.objects.filter(id=params).first()
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    members = GroupMember.objects.filter(group=group).select_related('user__user')
    serializer = GroupMemberSerializer(members, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_summary='Add member to group',
    operation_description=(
        'Add a registered user to a group by username. Requires JWT authentication.\n\n'
        '**Rules:**\n'
        '- Only a group **ADMIN** can add new members.\n'
        '- The target username must exist in the system.\n'
        '- The user cannot already be a member of the group.\n'
        '- Optional body parameter `role` can be `"member"` (default) or `"admin"`.'
    ),
    tags=['Group Members'],
    security=[{'Bearer': []}],
    manual_parameters=[PARAM_GROUP_ID, PARAM_USERNAME],
    request_body=ADD_MEMBER_BODY,
    consumes=['application/json'],
    produces=['application/json'],
    responses={
        201: openapi.Response('Member added successfully', GroupMemberSerializer),
        400: openapi.Response('User already in group / Validation error', SCHEMA_ERROR_400),
        401: openapi.Response('Unauthorized', SCHEMA_ERROR_401),
        403: openapi.Response('Forbidden - Only group admins can add members', SCHEMA_ERROR_403),
        404: openapi.Response('User or Group not found', SCHEMA_ERROR_404),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def add_member_group(request, params, username):
    # Check whether the new member exists
    new_user = User.objects.filter(username=username).first()
    if not new_user:
        return Response({"error": "No User Found"}, status=status.HTTP_404_NOT_FOUND)

    new_app_user = get_or_create_app_user(new_user)

    # Check whether the group exists
    group = Group.objects.filter(id=params).first()
    if not group:
        return Response(
            {"error": "Group not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verify the requesting user's role in this group
    request_app_user = get_or_create_app_user(request.user)
    is_admin = (
        GroupMember.objects.filter(
            group=group,
            user=request_app_user,
            role=GroupMember.Role.ADMIN,
        ).exists()
        or (group.group_admin == request_app_user)
        or (group.organisation.owner == request_app_user)
    )

    if is_admin:
        if GroupMember.objects.filter(group=group, user=new_app_user).exists():
            return Response(
                {"detail": "User is already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = request.data.get('role', GroupMember.Role.MEMBER)
        if role not in GroupMember.Role.values:
            role = GroupMember.Role.MEMBER

        member = GroupMember.objects.create(
            group=group,
            user=new_app_user,
            role=role,
        )
        serializer = GroupMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(
        {"detail": "You do not have permission to add members to this group."},
        status=status.HTTP_403_FORBIDDEN,
    )




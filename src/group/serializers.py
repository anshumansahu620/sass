from rest_framework import serializers 
from .models import Group, Organisation, GroupMember


class RegisterOrganisationSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)

    class Meta:
        model = Organisation
        fields = ['id', 'org_name', 'bio', 'logo', 'owner', 'owner_username']
        read_only_fields = ['id', 'owner', 'owner_username']


class OrganisationDetailsSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)
    groups_count = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = ['id', 'org_name', 'bio', 'logo', 'owner', 'owner_username', 'groups_count']
        read_only_fields = ['id', 'owner', 'owner_username', 'groups_count']

    def get_groups_count(self, obj):
        return obj.groups.count()


class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'organisation', 'group_name', 'group_logo', 'group_admin', 'created_at']
        read_only_fields = ['id', 'group_admin', 'created_at']


class GroupDetailsSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source='organisation.org_name', read_only=True)
    admin_username = serializers.CharField(source='group_admin.user.username', read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id',
            'organisation',
            'organisation_name',
            'group_name',
            'group_logo',
            'group_admin',
            'admin_username',
            'created_at',
            'members_count',
        ]
        read_only_fields = [
            'id',
            'organisation',
            'organisation_name',
            'group_admin',
            'admin_username',
            'created_at',
            'members_count',
        ]

    def get_members_count(self, obj):
        return obj.memberships.count()


# Backward compatibility alias
GroupDetails = GroupDetailsSerializer


class GroupMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.user.username', read_only=True)
    email = serializers.EmailField(source='user.user.email', read_only=True)

    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'user', 'username', 'email', 'role', 'joined_at']
        read_only_fields = ['id', 'group', 'user', 'joined_at']


# Backward compatibility alias
AddGroupMembersSerializer = GroupMemberSerializer


class AddMemberRequestSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=GroupMember.Role.choices,
        default=GroupMember.Role.MEMBER,
        help_text="Role assigned to user: 'admin' or 'member'"
    )


class UpdateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'organisation', 'group_name', 'group_logo', 'created_at']
        read_only_fields = ['id', 'created_at', 'organisation']


# Backward compatibility alias
UpdateGroup = UpdateGroupSerializer
from rest_framework import serializers 
from .models import Group,Organisation,GroupMember

class RegisterOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Organisation
        fields='__all__'
    





class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields='__all__'

class GroupDetails(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=['organisation','group_name','group_logo']
class AddGroupMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['group', 'user', 'role']

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
    


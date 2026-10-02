from django.db import models
from uuid import uuid4
# Create your models here.

class Organisation(models.Model):
    id=models.UUIDField(uuid4,primary_key=True)
    org_name=models.CharField()
    logo=models.ImageField(_(""), upload_to=, height_field=None, width_field=None, max_length=None)
    


class Group(models.Model):
    id=models.UUIDField(uuid4,primary_key=True)
    group_name=models.CharField()

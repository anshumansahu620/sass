from uuid import uuid4
from django.db import models
from core.models import AppUser


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    org_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    def __str__(self):
        return self.org_name


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="groups"
    )
    group_name = models.CharField(max_length=255)
    group_logo = models.ImageField(upload_to="group/icons/", blank=True, null=True)
    members = models.ManyToManyField(
        AppUser, through="GroupMember", related_name="chat_groups"
    )

    def __str__(self):
        return f"{self.group_name} ({self.organisation})"


class GroupMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="group_memberships"
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "user"], name="unique_group_user")
        ]
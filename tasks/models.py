from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

from django.core.validators import MinValueValidator, MaxValueValidator

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=100, default=STATUS_CHOICES[0][0]
    )
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hour = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)], default=19
    )
    minute = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(59)], default=30
    )

    def __str__(self):
        return f"Profile: {self.user}" if self.user else "Profile: Anonymous"


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    if not UserProfile.objects.filter(user=kwargs["instance"]).exists():
        new_profile = UserProfile(user=kwargs["instance"])
        new_profile.save()


@receiver(post_save, sender=UserProfile)
def change_details(sender, **kwargs):
    pass

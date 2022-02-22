from tasks.models import Task, STATUS_CHOICES
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Serializer, Field
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    DateTimeFilter,
    NumberFilter,
)


class TaskFilter(FilterSet):
    title = CharFilter(
        lookup_expr="icontains"
    )  # Applying the filter - Title 'contains' search term?
    status = ChoiceFilter(choices=STATUS_CHOICES)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            "user",
            "id",
            "title",
            "description",
            "status",
        )


class TaskViewSet(ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

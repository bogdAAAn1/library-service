from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.serializers import UserSerializer
from user.permissions import IsPermission


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsPermission]
        return [permission() for permission in permission_classes]

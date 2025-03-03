from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from schemas.user_schema_decorator import (
    create_user_schema,
    manage_schema_view
)
from user.serializers import UserSerializer


@extend_schema(tags=["user"])
@create_user_schema()
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema(tags=["user"])
@manage_schema_view()
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

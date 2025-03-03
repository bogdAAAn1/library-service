from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)

from schemas.book_schema_parameters import book_filter_list_schema
from user.serializers import UserSerializer


def create_user_schema():
    return extend_schema(
        summary="Create user",
        description="Register a new client in a library.",
        examples=[
            OpenApiExample(
                name="Create",
                description="Register new user. Password should have length - 5 "
                "symbols or more.",
                value=[{"email": "user@example.com", "password": "P0_SDkj7897"}],
            )
        ],
        responses={
            201: OpenApiResponse(
                description="User successfully created",
                examples=[
                    OpenApiExample(
                        name="Example response",
                        value={"id": 3, "email": "user1@admin.com", "is_staff": False},
                        response_only=True,
                    )
                ],
            )
        },
    )


def manage_schema_view():
    return extend_schema_view(
        get=extend_schema(
            summary="User profile",
            description="Retrieve the details of the authenticated user.",
            responses={
                200: OpenApiResponse(
                    description="User details retrieved successfully",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "id": 3,
                                "email": "user1@admin.com",
                                "is_staff": False,
                            },
                            response_only=True,  # Це лише приклад відповіді
                        )
                    ],
                ),
                401: OpenApiResponse(
                    description="Unauthorized",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "detail": "Authentication credentials were not provided."
                            },
                            response_only=True,
                        )
                    ],
                ),
            },
        ),
        put=extend_schema(
            summary="Update user profile",
            description="Update the details of the authenticated user.",
            responses={
                200: OpenApiResponse(
                    description="User details updated successfully",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "id": 3,
                                "email": "updated_user@example.com",
                                "is_staff": False,
                            },
                            response_only=True,
                        )
                    ],
                ),
                400: OpenApiResponse(
                    description="Bad request",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={"detail": "Invalid data provided."},
                            response_only=True,
                        )
                    ],
                ),
                401: OpenApiResponse(
                    description="Unauthorized",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "detail": "Authentication credentials were not provided."
                            },
                            response_only=True,
                        )
                    ],
                ),
            },
        ),
        patch=extend_schema(
            summary="Partially update user data",
            description="Partially update the details of the authenticated user.",
            responses={
                200: OpenApiResponse(
                    description="User details partially updated successfully",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "id": 3,
                                "email": "user1@admin.com",
                                "is_staff": False,
                            },
                            response_only=True,
                        )
                    ],
                ),
                400: OpenApiResponse(
                    description="Bad request",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={"detail": "Invalid data provided."},
                            response_only=True,
                        )
                    ],
                ),
                401: OpenApiResponse(
                    description="Unauthorized",
                    examples=[
                        OpenApiExample(
                            name="Example response",
                            value={
                                "detail": "Authentication credentials were not provided."
                            },
                            response_only=True,
                        )
                    ],
                ),
            },
        ),
    )

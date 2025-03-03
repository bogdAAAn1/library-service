from drf_spectacular.utils import extend_schema, OpenApiParameter


def borrowing_list_get_schema():
    return extend_schema(
        tags=["borrowings"],
        methods=["GET"],
        summary="List of all borrowings",
        description="Retrieve a list of all borrowings for current user.  \n"
        "If **admin** authorized - possible to view borrowings from all "
        "users.  \nAdmins can filter by `user_id` and `is_active`.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=int,
                description="Filter by user ID (admin only)",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=str,
                description="Filter active borrowings (`true` or `false`)",
                required=False,
            ),
        ],
        responses={200: "List of borrowings"},
    )


def borrowing_list_post_schema():
    return extend_schema(
        tags=["borrowings"],
        methods=["POST"],
        summary="Create a new borrowing",
        description="Create a new borrowing entry. The user must be authenticated.",
    )


def borrowing_detail_get_schema():
    return extend_schema(
        tags=["borrowings"],
        methods=["GET"],
        summary="Retrieve borrowing",
        description="Retrieve all detail info about borrowing.",
        responses={200: "Borrowing details"},
    )


def borrowing_detail_return_post_schema():
    return extend_schema(
        tags=["borrowings"],
        methods=["POST"],
        summary="Return book to library",
        description="Create a payment for returning borrowed book.",
    )

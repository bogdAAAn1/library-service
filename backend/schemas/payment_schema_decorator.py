from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    extend_schema_view,
)


def payment_schema_view():
    return extend_schema_view(
        list=extend_schema(
            summary="Get list of payments of current user",
            description="Get list of payments of current user.",
        ),
        retrieve=extend_schema(
            summary="Payment details.",
            description="Retrieve details about particular payment.",
        ),
    )


def payment_chancel_view_schema():
    return extend_schema(
        tags=["payments"],
        methods=["GET"],
        summary="Payment unsuccessful",
        description="Payment was cancelled.",
        responses={
            400: OpenApiResponse(
                description="Payment was cancelled",
                examples=[
                    OpenApiExample(
                        name="Payment Cancelled",
                        value={"message": "Payment was cancelled"},
                        description="Example response when the payment process is cancelled.",
                    )
                ],
            ),
        },
    )


def payment_success_view_schema():
    return extend_schema(
        tags=["payments"],
        methods=["GET"],
        summary="Payment successful",
        description="Borrowing successfully paid.",
        responses={
            200: OpenApiResponse(
                description="Payment successful",
                examples=[
                    OpenApiExample(
                        name="Payment successful",
                        value={"message": "success"},
                        description="Example response when the payment successful.",
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        name="Bad Request",
                        value={"error": "error"},
                        description="Example response for bad request.",
                    )
                ],
            ),
        },
    )

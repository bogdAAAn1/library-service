from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


book_filter_list_schema = {
    "parameters": [
        OpenApiParameter(
            "author",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Comma separated list of authors (first name + last "
            "name) to filter",
            required=False,
        ),
        OpenApiParameter(
            "daily_fee",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Filters books with exactly this daily fee",
            required=False,
        ),
        OpenApiParameter(
            "id",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Comma separated list of book's ids to filter",
            required=False,
        ),
        OpenApiParameter(
            "max_fee",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Upper limit value for filtering",
            required=False,
        ),
        OpenApiParameter(
            "min_fee",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Lower limit value for filtering",
            required=False,
        ),
        OpenApiParameter(
            "ordering",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Sorts items by query parameter: title, author, "
            "inventory, daily_fee",
            required=False,
        ),
        OpenApiParameter(
            "search",
            OpenApiTypes.NUMBER,
            OpenApiParameter.QUERY,
            description="Search items by query parameter: title, cover, " "inventory",
            required=False,
        ),
    ]
}

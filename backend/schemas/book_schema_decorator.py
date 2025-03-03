from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from schemas.book_schema_parameters import book_filter_list_schema


def book_schema_view():
    return extend_schema_view(
        list=extend_schema(
            summary="Get list of books with filters",
            description="Retrieve a list of books with optional filtering, searching, and sorting.",
            parameters=book_filter_list_schema["parameters"],
        ),
        create=extend_schema(
            summary="Create a new book",
            description="Create a new book in the library.",
        ),
        retrieve=extend_schema(
            summary="Retrieve a book",
            description="Retrieve a specific book by its ID.",
        ),
        update=extend_schema(
            summary="Update a book",
            description="Update a book's details.",
        ),
        partial_update=extend_schema(
            summary="Partially update a book",
            description="Partially update a book's details.",
        ),
        destroy=extend_schema(
            summary="Delete a book",
            description="Delete a specific book.",
        ),
        upload_image=extend_schema(
            summary="Adding image to book",
            description="Upload image to specific book.",
            examples=[
                OpenApiExample(
                    name="Upload image",
                    description="Example of image uploading.",
                    value=[
                        {
                            "id": 1,
                            "title": "The Little Prince",
                            "author": "Antoine de Saint-Exupery",
                            "cover": "Hard",
                            "inventory": 10,
                            "daily_fee": "0.55",
                            "image": "http://127.0.0.1:8000/media/uploads/books/the-little-prince.jpg",
                        },
                    ],
                ),
            ],
        ),
    )

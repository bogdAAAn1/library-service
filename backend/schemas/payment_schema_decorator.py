from drf_spectacular.utils import extend_schema_view, extend_schema


def book_schema_view():
    return extend_schema_view(
        list=extend_schema(
            summary="Get list of books with filters",
            description="Retrieve a list of books with optional filtering, searching, and sorting.",
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
    )

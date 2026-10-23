from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """`?page=N&limit=M` (limit 1-100, default 20) -> {"data": [...], "meta": {page, limit, total, total_pages}}."""

    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        paginator = self.page.paginator
        return Response(
            {
                "data": data,
                "meta": {
                    "page": self.page.number,
                    "limit": paginator.per_page,
                    "total": paginator.count,
                    "total_pages": paginator.num_pages if paginator.count else 0,
                },
            }
        )

    def get_paginated_response_schema(self, schema):
        integer = {"type": "integer"}
        return {
            "type": "object",
            "required": ["data", "meta"],
            "properties": {
                "data": schema,
                "meta": {
                    "type": "object",
                    "required": ["page", "limit", "total", "total_pages"],
                    "properties": {"page": integer, "limit": integer, "total": integer, "total_pages": integer},
                },
            },
        }

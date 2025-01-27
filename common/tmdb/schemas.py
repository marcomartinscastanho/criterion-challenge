SEARCH_MOVIE_SCHEMA = {
    "total_results": {"type": "integer", "required": True, "min": 1},
    "results": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {"type": "dict", "schema": {"id": {"type": "integer", "required": True, "min": 0}}},
    },
}

MOVIE_DETAILS_SCHEMA = {
    "genres": {
        "type": "list",
        "required": True,
        "schema": {"type": "dict", "schema": {"name": {"type": "string", "required": True, "minlength": 1}}},
    },
    "production_countries": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "iso_3166_1": {"type": "string", "required": True, "minlength": 2, "maxlength": 2},
                "name": {"type": "string", "required": True, "minlength": 1},
            },
        },
    },
    "origin_country": {
        "type": "list",
        "required": True,
        "schema": {"type": "string", "minlength": 2, "maxlength": 2},
    },
    "credits": {
        "type": "dict",
        "required": True,
        "schema": {
            "crew": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {"type": "string", "required": True},
                        "job": {"type": "string", "required": True},
                    },
                },
            }
        },
    },
    "runtime": {"type": "integer", "required": True, "min": 1},
}

CUSTOM_CRITERIA_SCHEMA = schema = {
    "countries": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["in"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "foreign_key": {"type": "string", "allowed": ["regions"]},
                        "value": {
                            "type": "dict",
                            "schema": {
                                "key": {"type": "string"},
                                "value": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
    "directors": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["eq"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "foreign_key": {"type": "string", "allowed": ["directors"]},
                        "value": {
                            "type": "dict",
                            "schema": {
                                "key": {"type": "string"},
                                "value": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
    "genres": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["eq"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "foreign_key": {"type": "string", "allowed": ["genres"]},
                        "value": {
                            "type": "dict",
                            "schema": {
                                "key": {"type": "string"},
                                "value": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
    "keywords": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["in"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "foreign_key": {"type": "string", "allowed": ["keywords"]},
                        "value": {
                            "type": "dict",
                            "schema": {
                                "key": {"type": "string"},
                                "value": {"type": "list", "schema": {"type": "string"}},
                            },
                        },
                    },
                },
            },
        },
    },
    "spine": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["is_null", "gte", "lte"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "boolean": {"type": "boolean", "required": False},
                        "number": {"type": "integer", "required": False},
                    },
                },
            },
        },
    },
    "year": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "operation": {"type": "string", "allowed": ["eq", "gte", "lt"]},
                "value": {
                    "type": "dict",
                    "schema": {
                        "user_attribute": {"type": "string", "required": False},
                        "number": {"type": "integer", "required": False},
                    },
                },
            },
        },
    },
}

from django.db.models import Model


def get_object_sql_insert(obj: Model) -> str:
    """
    Generate an SQL INSERT query for the given object.
    """
    table = obj._meta.db_table
    columns = [field.column for field in obj._meta.local_fields if field.column != "id"]
    values = [getattr(obj, field.name) for field in obj._meta.local_fields if field.name != "id"]
    escaped_values = [
        f"'{value}'" if isinstance(value, str) else "NULL" if value is None else str(value) for value in values
    ]
    sql_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(escaped_values)});"
    sql_query = sql_query.replace("{", "{{")
    sql_query = sql_query.replace("}", "}}")
    sql_query = sql_query.replace("{{}}", "NULL")
    return sql_query

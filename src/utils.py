import json
from uuid import UUID


def obj_encoder(o):
    if isinstance(o, UUID):
        return str(o)


def json_encode(data):
    """Specialized json serializer"""

    return json.dumps(data, default=obj_encoder)

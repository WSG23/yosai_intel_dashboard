import json
from flask.json.provider import DefaultJSONProvider
from .json_serializer import YosaiJSONEncoder

class YosaiJSONProvider(DefaultJSONProvider):
    """Custom JSON provider using YosaiJSONEncoder for serialization."""

    def dumps(self, obj, **kwargs):
        kwargs.setdefault("cls", YosaiJSONEncoder)
        kwargs.setdefault("ensure_ascii", False)
        return json.dumps(obj, **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

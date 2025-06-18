from flask.json.provider import DefaultJSONProvider
from flask_babel import LazyString


class YosaiJSONProvider(DefaultJSONProvider):
    """JSON provider that safely serializes LazyString objects."""

    def default(self, obj):
        if isinstance(obj, LazyString):
            return str(obj)
        return super().default(obj)


__all__ = ["YosaiJSONProvider"]

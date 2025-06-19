import json
from flask.json.provider import DefaultJSONProvider
from .json_serializer import YosaiJSONEncoder


class YosaiJSONProvider(DefaultJSONProvider):
    """Custom JSON provider using YosaiJSONEncoder for serialization."""

    def dumps(self, obj, **kwargs):
        kwargs.setdefault("cls", YosaiJSONEncoder)
        kwargs.setdefault("ensure_ascii", False)
        try:
            return json.dumps(obj, **kwargs)
        except Exception as e:
            # Fallback for LazyString serialization errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON serialization failed: {e}")

            # Emergency LazyString handling
            if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
                return json.dumps(str(obj))

            return json.dumps({
                'error': 'JSON serialization failed',
                'message': str(e),
                'type': type(obj).__name__
            })

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# Manual LazyString Fix Instructions

## Option 1: Add to top of your app.py

Add this code at the very top of app.py, before any other imports:

```python
# LazyString JSON Fix - Add at TOP of app.py
import json

original_default = json.JSONEncoder.default

def lazystring_handler(self, obj):
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        return str(obj)
    if callable(obj):
        return str(obj)
    try:
        return original_default(self, obj)
    except TypeError:
        return str(obj)

json.JSONEncoder.default = lazystring_handler
```

## Option 2: Create .py file and import it first

Create `lazystring_patch.py`:
```python
import json

def apply_patch():
    original = json.JSONEncoder.default
    def handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        return original(self, obj)
    json.JSONEncoder.default = handler

apply_patch()
```

Then in app.py, add as first import:
```python
import lazystring_patch  # Must be first import
```

## Option 3: Environment variable

Set this before running:
```bash
export PYTHONPATH=".:$PYTHONPATH"
python3 -c "import json; json.JSONEncoder.default = lambda self, obj: str(obj) if 'LazyString' in str(type(obj)) else json.JSONEncoder.default(self, obj)" && python3 app.py
```

"""
Immediate LazyString Patch
Import this at the top of your app.py to fix LazyString issues
"""

def apply_lazystring_patch():
    """Apply LazyString patch - call this first thing in your app"""
    
    # 1. Patch Flask-Babel to return strings
    try:
        from flask_babel import lazy_gettext, gettext
        import flask_babel
        
        original_lazy = lazy_gettext
        original_get = gettext
        
        def string_lazy(string, **variables):
            return str(original_lazy(string, **variables))
        
        def string_get(string, **variables):
            return str(original_get(string, **variables))
        
        flask_babel.lazy_gettext = string_lazy
        flask_babel.gettext = string_get
        flask_babel._l = string_lazy
        
        print("✅ Flask-Babel patched to return strings")
        
    except ImportError:
        pass
    
    # 2. Patch JSON globally
    import json
    original_default = json.JSONEncoder.default
    
    def lazystring_json_handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        if hasattr(obj, '_func'):
            return str(obj)
        if callable(obj):
            return str(obj)
        try:
            return original_default(self, obj)
        except TypeError:
            return str(obj)
    
    json.JSONEncoder.default = lazystring_json_handler
    print("✅ JSON patched for LazyString")

# Auto-apply when imported
apply_lazystring_patch()

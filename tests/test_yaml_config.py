import os
import tempfile
import yaml
from config.yaml_config import ConfigurationManager

def test_app_title_loaded_from_yaml():
    data = {
        'app': {
            'title': 'Custom Dashboard'
        }
    }
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.yaml') as tmp:
        yaml.dump(data, tmp)
        tmp_path = tmp.name
    try:
        manager = ConfigurationManager(config_path=tmp_path)
        manager.load_configuration()
        assert manager.app_config.title == 'Custom Dashboard'
    finally:
        os.remove(tmp_path)



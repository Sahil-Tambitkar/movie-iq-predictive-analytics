import yaml
import json
import os

def load_config():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        
    metadata_path = os.path.join(base_dir, 'artifacts', 'metadata.json')
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                config['paths']['model'] = metadata.get('model_path', config['paths']['model'])
                config['paths']['model_features'] = metadata.get('model_features_path', config['paths']['model_features'])
                config['model_hmac'] = metadata.get('model_hmac')
                config['model_features_hmac'] = metadata.get('model_features_hmac')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load metadata.json properly: {e}")
            
    return config

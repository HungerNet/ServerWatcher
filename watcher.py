import os

# Update the configuration loading location to the current working directory
CONFIG_DIR = os.getcwd()  # Use the current working directory for config files

# Load configuration files from the new config directory
config_file_path = os.path.join(CONFIG_DIR, 'config.yaml')

import uuid
import os
from datetime import datetime

the_temp_dir = "craftsman_temp"

def generate_unique_docker_image_name(prefix='magic'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_name = f"{prefix}_{timestamp}_{str(uuid.uuid4())[:8]}"
    return unique_name

def remove_temp_directory(directory_path = the_temp_dir):
    if os.path.exists(directory_path):
        try:
            # Remove the directory and its contents forcefully
            os.system(f"rm -rf {directory_path}")
            print(f"Directory '{directory_path}' removed successfully.")
        except Exception as e:
            print(f"Error removing directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' does not exist.")
        

def create_temp_directory(directory_path = the_temp_dir):        
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
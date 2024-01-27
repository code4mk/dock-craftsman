import uuid
from datetime import datetime

def generate_unique_docker_image_name(prefix='magic'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_name = f"{prefix}_{timestamp}_{str(uuid.uuid4())[:8]}"
    return unique_name
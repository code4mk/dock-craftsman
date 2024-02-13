import docker
import humanize
import datetime as dt
from dateutil.parser import parse
from datetime import datetime, timedelta
from dateutil import parser

class TheImage:
    def __init__(self, docker_socket=None):
        # Create a Docker client
        self.client = docker.DockerClient(base_url=docker_socket)

    def get_lists(self, query=None):
        images = []
        containers = self.client.containers.list(all=True)

        for image in self.client.images.list(all=True):
            inspect_data = image.attrs
            image_id = inspect_data['Id'][7:19]  # Extract the 12-character image ID

            # Check if the image is used by any containers
            used_container_info = self.get_used_containers(containers, image_id)

            # Convert size from bytes to megabytes
            size_mb = self.convert_bytes_to_mb(inspect_data['Size'])

            # Check if any used containers are in "running" state
            used_running = any(container['container_status'] == 'running' for container in used_container_info)

            # Determine image status
            status = self.determine_image_status(inspect_data['RepoTags'], used_container_info)

            # Extract repository and tag or provide default values
            repo_tags = inspect_data['RepoTags']
            repository, tag = self.extract_repository_and_tag(repo_tags)

            image_info = {
                'repository': repository,
                'tag': tag,
                'tags': repo_tags,
                'image_id': image_id,
                'created': inspect_data['Created'],
                'created_humonize': self.get_the_time(inspect_data['Created']),
                'size': size_mb,
                'platform': {
                    'os': inspect_data['Os'],
                    'architecture': inspect_data['Architecture']
                },
                'used': bool(used_container_info),
                'used_running': used_running,
                'status': status,
                'used_container_info': used_container_info
            }

            # Apply query filters
            if query:
                if 'name' in query and query['name'] not in repository:
                    continue
                if 'status' in query and query['status'] != 'all' and query['status'] != status:
                    continue

            images.append(image_info)

        # Sort images based on date
        images.sort(key=lambda x: x['created'], reverse=query.get('date_sort') == 'desc' if query and 'date_sort' in query else False)

        return images

    def get_used_containers(self, containers, image_id):
        used_containers = []

        for container in containers:
            container_image_id = container.attrs['Image'][7:19]
            if container_image_id == image_id:
                used_containers.append({
                    'container_id': container.id,
                    'container_name': container.name,
                    'container_status': container.status
                })

        return used_containers

    @staticmethod
    def convert_bytes_to_mb(bytes_size):
        return "{:.2f}MB".format(bytes_size / (1024 * 1024))

    @staticmethod
    def determine_image_status(repo_tags, used_container_info):
        if not repo_tags or repo_tags[0] == '<none>:<none>':
            return 'dangling'
        elif used_container_info:
            return 'used'
        else:
            return 'unused'

    @staticmethod
    def extract_repository_and_tag(repo_tags):
        if repo_tags:
            repo, tag = repo_tags[0].split(':')
            return repo, tag
        else:
            # Default values when no tags are present
            return '<none>', '<none>'
    
    @staticmethod
    def get_the_time(date_str):
      # Convert date string to datetime object
        date_obj = parser.parse(date_str)
        timestamp_nano = int(date_obj.timestamp() * 1e9)

        # Current timestamp
        current_time = datetime.utcnow()
        current_timestamp_nano = int(current_time.timestamp() * 1e9)

        # Calculate the difference in seconds
        difference_seconds = min((current_timestamp_nano - timestamp_nano) / 1e9, 24 * 3600)

        return humanize.naturaltime(difference_seconds)
        # Define thresholds for different time units
        minute_threshold = 60
        hour_threshold = 6 * 3600  # 6 hours in seconds
        day_threshold = 6 * 24 * 3600  # 6 days in seconds
        week_threshold = 4 * 7 * 24 * 3600  # 4 weeks in seconds

        # Compare with thresholds and return the appropriate message
        if difference_seconds < minute_threshold:
            return f"{int(difference_seconds)} seconds ago"
        elif difference_seconds < hour_threshold:
            return f"{int(difference_seconds / 60)} minutes ago"
        elif difference_seconds < day_threshold:
            hours_ago = int(difference_seconds / 3600)
            if hours_ago == 1:
                return "1 hour ago"
            else:
                return f"{hours_ago} hours ago"
        elif difference_seconds < week_threshold:
            days_ago = int(difference_seconds / 86400)
            if days_ago == 1:
                return "1 day ago"
            else:
                return f"{days_ago} days ago"
        else:
            return date_obj.strftime("%B %d, %Y")  # Dynamic date format
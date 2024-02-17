import docker

class TheVolume:
    def __init__(self, docker_socket=None):
        # Create a Docker client
        self.client = docker.DockerClient(base_url=docker_socket)

    def get_used_containers(self, containers, volume):
        # List to store used container information
        used_containers = []

        # Check if the volume is used by any containers
        is_used = False
        is_used_live = False

        for container in containers:
            inspect_data = container.attrs
            mounts = inspect_data['Mounts']
            
            for mount in mounts:
                if mount["Type"] == 'volume':
                    if mount["Name"] == volume:
                        is_used = True
                        container_short_info = {
                            'container_id': inspect_data['Id'][:12],
                            'container_name': inspect_data['Name'][1:],
                            'status': inspect_data['State']['Status']
                        }
                        used_containers.append(container_short_info)
                        
                        if inspect_data['State']['Status'] == 'running':
                            is_used_live = True
                            
        print(used_containers)
        return is_used_live, is_used, used_containers
    
    def get_lists(self, query=None):
        volumes = []
        
        containers = self.client.containers.list(all=True)
        
        for volume in self.client.volumes.list():
            inspect_data = volume.attrs
            is_used_live ,is_used, used_containers = self.get_used_containers(containers, inspect_data['Name'])
            
            volume_info = {
                'name': inspect_data['Name'],
                'created_at': inspect_data['CreatedAt'],
                'driver': inspect_data['Driver'],
                'mount_point': inspect_data['Mountpoint'],
                'scope': inspect_data['Scope'],
                'labels': inspect_data['Labels'],
                'is_used': is_used,
                'is_used_live': is_used_live,
                'used_containers': used_containers
            }

            volumes.append(volume_info)

        return volumes

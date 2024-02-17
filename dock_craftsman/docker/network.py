import docker

class TheNetwork:
    def __init__(self, docker_socket=None):
        # Create a Docker client
        self.client = docker.DockerClient(base_url=docker_socket)

    def get_lists(self, query=None):
        networks = []
        
        containers = self.client.containers.list(all=True)
        
        for network in self.client.networks.list():
            inspect_data = network.attrs
            print(inspect_data)
            print("=============")
            #is_used_live ,is_used, used_containers = self.get_used_containers(containers, inspect_data['Id'])
            
            networks_info = {
                'name': inspect_data['Name'],
                'created_at': inspect_data['Created'],
                'driver': inspect_data['Driver'],
                'id': inspect_data['Id'],
                # 'is_used': is_used,
                # 'is_used_live': is_used_live,
                # 'used_containers': used_containers
            }

            networks.append(networks_info)

        return networks

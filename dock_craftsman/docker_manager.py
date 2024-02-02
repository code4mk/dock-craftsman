import docker
import json
import os
from docker.errors import APIError, ImageNotFound
from tqdm import tqdm

class DockerManager:
    def __init__(self, docker_socket=None):
        # Create a Docker client
        if docker_socket:
            self.client = docker.DockerClient(base_url=docker_socket)
        else:
            self.client = docker.from_env()
            
        # Initialize container_info_list
        self.container_info_list = []

    def container(self, image_tag, name=None, ports=None, detach=False, tty=False, env=None, volumes=None,
                  pull_from_docker_hub=False):
        """
        Prepare information for a Docker container without running it.

        :param image_tag: The tag of the Docker image.
        :param name: The name of the Docker container.
        :param ports: A string specifying port mappings in the format 'host:container'.
        :param detach: Whether to run the container in the background.
        :param tty: Allocate a pseudo-TTY and run the container in interactive mode.
        :param env: A list of dictionaries representing environment variables.
        :param volumes: A string specifying volume mappings in the format 'host_path:container_path'.
        :param pull_from_docker_hub: Whether to pull the image from Docker Hub before running.
        :return: None
        """
        # Get or create the Docker network
        network_name = 'my_docker_network'
        docker_network = self.get_or_create_network(network_name, driver='bridge')

        if pull_from_docker_hub:
            # Split image_tag into image name and tag
            image_name, tag = image_tag.split(':')
            print(f"Pulling image {image_name} with tag {tag} from Docker Hub...")
            image = self.client.images.pull(image_name, tag=tag)

        # Build the container run options
        run_options = {
            'detach': detach,
            'tty': tty,
        }

        if docker_network:
            run_options['network'] = network_name  # Connect the container to the specified network

        if ports:
            # Convert ports string to dictionary
            host_port, container_port = ports.split(':')
            ports_mapping = {f'{container_port}/tcp': int(host_port)}
            run_options['ports'] = ports_mapping

        if env:
            # Convert env list to dictionary
            env_dict = {item['env_name']: item['value'] for item in env}
            run_options['environment'] = env_dict

        if volumes:
            # Convert volumes string to dictionary
            host_path, container_path = volumes.split(':')
            volume_mapping = {host_path: {'bind': container_path, 'mode': 'rw'}}
            run_options['volumes'] = volume_mapping

        # Save container information to container_info_list
        container_info = {
            'image': image_tag,
            'name': name,  # Added name parameter
            'run_options': run_options,
        }
        self.container_info_list.append(container_info)
        
    def up(self):
        """
        Run the containers stored in container_info_list.
        """
        for container_info in self.container_info_list:
            try:
                # Get or create the Docker network
                network_name = 'my_docker_network'
                docker_network = self.get_or_create_network(network_name, driver='bridge')

                # Build the container run options
                run_options = container_info['run_options']

                if docker_network:
                    run_options['network'] = network_name  # Connect the container to the specified network

                # Run the container with the specified name
                container = self.client.containers.run(
                    container_info['image'],
                    name=container_info['name'],  # Added name parameter
                    **run_options,
                )

                # Save container information to container_info_list
                container_info['id'] = container.id[:12]

                print(f"Starting container with ID {container_info['id']} and name {container_info['name']}...")
                # Save container information to container_info_list
                self.save_container_info(container)
                print(f"Container with ID {container_info['id']} and name {container_info['name']} started.")
            except docker.errors.NotFound:
                print(f"Container with image {container_info['image']} not found.")
            except APIError as e:
                print(f"Error: API error during container start.")
                raise e

    def save_container_info(self, container):
        """
        Save container information to a JSON file.
        :param container: The Docker container object.
        """
        container_info = {
            'id': container.id[:12],
            'name': container.name,
            'image': container.image.tags[0],
            # Add more information as needed
        }
        json_filename = 'dock_craft_containers.json'
        # Check if the JSON file exists
        if os.path.exists(json_filename):
            # Read existing content
            with open(json_filename, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = []
            # Append new container info
            existing_data.append(container_info)
            # Write back to the file
            with open(json_filename, 'w') as json_file:
                json.dump(existing_data, json_file, indent=2)
        else:
            # Create a new file and store the data as an array
            with open(json_filename, 'w') as json_file:
                json.dump([container_info], json_file, indent=2)

    def down(self, rm=False):
        """
        Stop and remove Docker containers listed in the 'dock_craft_containers.json' file.
        """
        json_filename = 'dock_craft_containers.json'

        if os.path.exists(json_filename):
            with open(json_filename, 'r') as json_file:
                container_info_list = json.load(json_file)

            for container_info in container_info_list:
                container_id = container_info.get('id')
                try:
                    container = self.client.containers.get(container_id)
                    print(f"Stopping container with ID {container_id}...")
                    container.stop()
                    print(f"Container with ID {container_id} stopped.")

                    if rm:
                        print(f"Removing container with ID {container_id}...")
                        container.remove()
                        print(f"Container with ID {container_id} removed.")

                except docker.errors.NotFound:
                    print(f"Container with ID {container_id} not found.")
                except APIError as e:
                    print(f"Error: API error during container removal.")
                    raise e

            # Remove the JSON file after processing
            os.remove(json_filename)
        else:
            print("No containers found")

    def get_or_create_network(self, name, driver='bridge'):
        """
        Get an existing Docker network by name or create it if it doesn't exist.

        :param name: The name of the Docker network.
        :param driver: The driver for the Docker network (default is 'bridge').
        :return: The Docker network object.
        """
        try:
            docker_network = self.client.networks.get(name)
            return docker_network
        except docker.errors.NotFound:
            return self.create_network(name, driver)

    def create_network(self, name, driver='bridge'):
        """
        Create a Docker network with the specified name and driver.

        :param name: The name of the Docker network.
        :param driver: The driver for the Docker network (default is 'bridge').
        :return: The Docker network object.
        """
        try:
            print(f"Creating Docker network: {name}")
            docker_network = self.client.networks.create(name, driver=driver)
            return docker_network
        except APIError as e:
            print(f"Error: API error during network creation.")
            raise e
        
    def tree(self):
        """
        Display container information in a tree-like structure.
        """
        self.container_infos = []
        json_filename = 'dock_craft_containers.json'

        if os.path.exists(json_filename):
            with open(json_filename, 'r') as json_file:
                container_info_list = json.load(json_file)

            if container_info_list:
                print("\n==== Container Information (Tree View) ====")
                
                for container_info in container_info_list:
                    # Inspect the running container
                    if 'id' in container_info:
                        try:
                            container = self.client.containers.get(container_info['id'])
                            inspect_data = container.attrs
                            
                            ports = inspect_data['HostConfig']['PortBindings']
                            formatted_ports = ", ".join([f"localhost{v[0]['HostIp']}:{v[0]['HostPort']}->{k.split('/')[0]}" for k, v in ports.items()])
                            
                            the_container_info = {
                                'image': container_info['image'],
                                'status': inspect_data['State']['Status'],
                                'ports': formatted_ports,
                                'network': {
                                    'ip_address': inspect_data['NetworkSettings']['Networks']['my_docker_network']['IPAddress']
                                }
                            }
                            self.container_infos.append(the_container_info)
                        except docker.errors.NotFound:
                            print("Container not found (not running)")
                        except APIError as e:
                            print(f"Error inspecting container: {str(e)}")
                    else:
                        print("Not started")
                print(str(self.container_infos))
            else:
                print("No container information available.")
        else:
            print("No container information file found.")

import docker
import json
import os
from docker.errors import APIError, ImageNotFound

class DockerContainerRun:
    def __init__(self):
        # Create a Docker client
        self.client = docker.from_env()

    def run(self, image_tag, ports=None, detach=False, tty=False, env=None, pull_from_docker_hub=False):
        """
        Run a Docker container.

        :param image_tag: The tag of the Docker image.
        :param ports: A string specifying port mappings in the format 'host:container'.
        :param detach: Whether to run the container in the background.
        :param tty: Allocate a pseudo-TTY and run the container in interactive mode.
        :param env: A list of dictionaries representing environment variables.
        :param pull_from_docker_hub: Whether to pull the image from Docker Hub before running.
        :return: The container object.
        """
        try:
          
            # Get or create the Docker network
            network_name = 'my_docker_network'
            docker_network = self.get_or_create_network(network_name, driver='bridge')
            
            if pull_from_docker_hub:
              # Split image_tag into image name and tag
              image_name, tag = image_tag.split(':')
              print(f"Pulling image {image_name} with tag {tag} from Docker Hub...")
              import requests

              response = requests.get(
                  f"https://registry.hub.docker.com/v2/repositories/library/{image_name}/tags/{tag}/",
                  stream=True
              )

              for chunk in response.iter_content(chunk_size=1024):
                  if chunk:
                    print(str(chunk))
                      # pull_status = json.loads(chunk.decode('utf-8'))
                      # print(f"Status: {pull_status.get('status', '')}, Progress: {pull_status.get('progress', '')}")
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

            # Run the container
            container = self.client.containers.run(image_tag, **run_options)

            # Print the container ID
            print(f"Container ID: {container.id}")

            # Save container information to JSON file
            self.save_container_info(container)

            return container

        except ImageNotFound as e:
            print(f"Error: Image {image_tag} not found on Docker Hub.")
            raise e
        except APIError as e:
            print(f"Error: API error during container run.")
            raise e

    def save_container_info(self, container):
        """
        Save container information to a JSON file.

        :param container: The Docker container object.
        """
        container_info = {
            'id': container.id,
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
            print(f"Using existing Docker network: {name}")
            return docker_network
        except docker.errors.NotFound:
            print(f"Docker network not found: {name}. Creating the network...")
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
            print(f"Network created successfully: {docker_network.id}")
            return docker_network
        except APIError as e:
            print(f"Error: API error during network creation.")
            raise e
import docker

class TheContainer:
    def __init__(self):
        # Create a Docker client
        self.client = docker.from_env()

    def run(self, image_tag, ports=None, detach=False, tty=False):
        """
        Run a Docker container.

        :param image_tag: The tag of the Docker image.
        :param ports: A dictionary specifying port mappings.
        :param detach: Whether to run the container in the background.
        :param tty: Allocate a pseudo-TTY and run the container in interactive mode.
        :return: The container object.
        """
        # Build the container run options
        run_options = {
            'detach': detach,
            'tty': tty,
        }

        if ports:
            host_port, container_port = ports.split(':')
            ports_mapping = {f'{container_port}/tcp': int(host_port)}
            run_options['ports'] = ports_mapping

        # Run the container
        container = self.client.containers.run(image_tag, **run_options)

        # Print the container ID
        print(f"Container ID: {container.id}")

        return container

    def logs(self, container_id):
        """
        Retrieve the logs of a Docker container.

        :param container_id: The ID of the Docker container.
        :return: The container logs.
        """
        container = self.client.containers.get(container_id)
        return container.logs().decode('utf-8')

    def exec_cmd(self, container_id, *args):
        """
        Execute a command inside a running Docker container.

        :param container_id: The ID of the Docker container.
        :param args: The arguments for the command.
        :return: The output of the command.
        """
        command = ["/bin/bash", "-c"] + list(args)
        exec_id = self.client.api.exec_create(container_id, cmd=command)['Id']
        exec_output = self.client.api.exec_start(exec_id)
        result = exec_output.decode('utf-8')

        return result
      
    def stop(self, container_ids):
        """
        Stop Docker containers.

        :param container_ids: A single container ID or a list of container IDs.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        for container_id in container_ids:
            container = self.client.containers.get(container_id)
            container.stop()

    def remove(self, container_ids):
        """
        Remove Docker containers.

        :param container_ids: A single container ID or a list of container IDs.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        for container_id in container_ids:
            container = self.client.containers.get(container_id)
            container.remove()

    def start(self, container_ids):
        """
        Start Docker containers.

        :param container_ids: A single container ID or a list of container IDs.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        for container_id in container_ids:
            container = self.client.containers.get(container_id)
            container.start()

    def lists(self, all_containers=False):
        containers = []
        
        if all_containers:
            container_objects = self.client.containers.list(all=True)
        else:
            container_objects = self.client.containers.list()

        for container in container_objects:
            container_info = {
                'CONTAINER ID': container.id,
                'IMAGE': container.image.tags[0] if container.image.tags else '',
                'COMMAND': ' '.join(container.attrs['Config']['Cmd']),
                'CREATED': container.attrs['Created'],
                'STATUS': container.attrs['State']['Status'],
                'PORTS': ', '.join(container.ports.keys()) if container.ports else '',
                'NAMES': container.name
            }
            containers.append(container_info)

        return containers

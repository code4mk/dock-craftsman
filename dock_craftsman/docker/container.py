import docker
from docker.errors import NotFound


class TheContainer:
    def __init__(self, docker_socket=None):
        # Create a Docker client
        self.client = docker.DockerClient(base_url=docker_socket)

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
        log_data =  container.logs().decode('utf-8')
        return log_data

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
        :return: A dictionary with information about the stopped containers.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        stopped_containers = {'success': [], 'not_found': []}

        for container_id in container_ids:
            try:
                container = self.client.containers.get(container_id)
                container.stop()
                stopped_containers['success'].append({'id': container_id, 'message': 'Container stopped successfully'})
            except NotFound:
                stopped_containers['not_found'].append({'id': container_id, 'message': 'Container not found'})

        return stopped_containers
        

    def remove(self, container_ids):
        """
        Remove Docker containers.

        :param container_ids: A single container ID or a list of container IDs.
        :return: A dictionary with information about the removed containers.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        removed_containers = {'success': [], 'not_found': []}

        for container_id in container_ids:
            try:
                container = self.client.containers.get(container_id)
                container.remove()
                removed_containers['success'].append({'id': container_id, 'message': 'Container removed successfully'})
            except NotFound:
                removed_containers['not_found'].append({'id': container_id, 'message': 'Container not found'})

        return removed_containers

    def start(self, container_ids):
        """
        Start Docker containers.

        :param container_ids: A single container ID or a list of container IDs.
        :return: A dictionary with information about the started containers.
        """
        if isinstance(container_ids, str):
            container_ids = [container_ids]

        started_containers = {'success': [], 'not_found': []}

        for container_id in container_ids:
            try:
                container = self.client.containers.get(container_id)
                container.start()
                started_containers['success'].append({'id': container_id, 'message': 'Container started successfully'})
            except NotFound:
                started_containers['not_found'].append({'id': container_id, 'message': 'Container not found'})

        return started_containers

    def get_lists(self, all_containers=False):
        containers = []
        
        if all_containers:
            container_objects = self.client.containers.list(all=True)
        else:
            container_objects = self.client.containers.list(all=True)

        for container in container_objects:
            inspect_data = container.attrs
            
            container_full_info = {
                'container_id': inspect_data['Id'],
                'created': inspect_data['Created'],
                'path': inspect_data['Path'],
                'args': inspect_data['Args'],
                'state': {
                    'status': inspect_data['State']['Status'],
                    'running': inspect_data['State']['Running'],
                    'paused': inspect_data['State']['Paused'],
                    'restarting': inspect_data['State']['Restarting'],
                    'oom_killed': inspect_data['State']['OOMKilled'],
                    'dead': inspect_data['State']['Dead'],
                    'pid': inspect_data['State']['Pid'],
                    'exit_code': inspect_data['State']['ExitCode'],
                    'error': inspect_data['State']['Error'],
                    'started_at': inspect_data['State']['StartedAt'],
                    'finished_at': inspect_data['State']['FinishedAt'],
                },
                'image': inspect_data['Image'],
                'resolv_conf_path': inspect_data['ResolvConfPath'],
                'hostname_path': inspect_data['HostnamePath'],
                'hosts_path': inspect_data['HostsPath'],
                'log_path': inspect_data['LogPath'],
                'name': inspect_data['Name'],
                'restart_count': inspect_data['RestartCount'],
                'driver': inspect_data['Driver'],
                'platform': inspect_data['Platform'],
                'mount_label': inspect_data['MountLabel'],
                'process_label': inspect_data['ProcessLabel'],
                'app_armor_profile': inspect_data['AppArmorProfile'],
                'exec_ids': inspect_data['ExecIDs'],
                'host_config': inspect_data['HostConfig'],
                'graph_driver': inspect_data['GraphDriver'],
                'mounts': inspect_data['Mounts'],
                'config': inspect_data['Config'],
                'network_settings': inspect_data['NetworkSettings'],
            }
            
            ports = inspect_data['NetworkSettings']['Ports']

            formatted_ports = []
            for k, v in ports.items():
                if v is None or len(v) == 0:
                    continue
                host_ip = v[0]['HostIp']
                host_port = v[0]['HostPort']
                container_port = k.split('/')[0]
                
                formatted_port = f"localhost:{host_port}"
                
                # Check if formatted_port already exists in formatted_ports, and ignore if true
                if formatted_port in formatted_ports:
                    continue
                
                formatted_ports.append(formatted_port)

            formatted_ports_str = ", ".join(formatted_ports)
            print(formatted_ports_str)
                            
            container_short_info = {
                'container_id': inspect_data['Id'][:12],
                'container_name': inspect_data['Name'][1:],
                'status': inspect_data['State']['Status'],
                'running': inspect_data['State']['Running'],
                'restarting': inspect_data['State']['Restarting'],
                'paused': inspect_data['State']['Paused'],
                'pid': inspect_data['State']['Pid'],
                'created': inspect_data['Created'],
                'started_at': inspect_data['State']['StartedAt'],
                'finished_at': inspect_data['State']['FinishedAt'],
                'image': inspect_data['Config']['Image'],
                'env': inspect_data['Config']['Env'],
                'mounts': inspect_data['Mounts'],
                'ports': formatted_ports
            }
            container_info = {
                'short': container_short_info,
                'details': container_full_info
            }
            containers.append(container_info)

        return containers


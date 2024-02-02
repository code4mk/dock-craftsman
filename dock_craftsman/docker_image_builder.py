import docker
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from .utils import generate_unique_docker_image_name

class DockerImageBuilder:
    def __init__(self, docker_socket=None):
        self.image_name = generate_unique_docker_image_name()
        self.dockerfile_content = None
        self.dockerfile = None
        self.path = '.'
        self.tags = 'latest'
        self.build_args = {}
        self.platform = None
        self.cache_from = None
        self.extra_hosts = None
        self.client_error = False
        
        try:
            if docker_socket:
                self.docker_client = docker.DockerClient(base_url=docker_socket)
            else:
                self.docker_client = docker.from_env()
        except Exception as e:
            console = Console()
            console.print(Panel(f"{e}", title="Initialization Error", style="red"))
            self.client_error = True

    def set_name(self, image_name):
        self.image_name = image_name
        return self

    def set_tag(self, tags):
        self.tags = tags
        return self

    def set_content(self, dockerfile_content):
        self.dockerfile_content = dockerfile_content
        
        # Define the polyfill
        # source: https://github.com/docker/docker-py/issues/2105#issuecomment-613685891
        docker.api.build.process_dockerfile = lambda dockerfile, path: ('Dockerfile', dockerfile)
        
        return self
    
    def set_dockerfile(self, docker_file):
        self.dockerfile = docker_file
        return self
    
    def set_path(self, path):
        self.path = path
        return self

    def set_build_args(self, build_args):
        self.build_args = build_args
        return self

    def set_platform(self, platform):
        self.platform = platform
        return self

    def set_cache_from(self, cache_from):
        self.cache_from = cache_from
        return self

    def set_extra_hosts(self, extra_hosts):
        self.extra_hosts = extra_hosts
        return self

    def build(self):
        if self.client_error:
            return False
        
        import time
        start_time = time.time()  # Record the start time
        console = Console()

        console = Console()

        dockerfile_content = self.dockerfile_content

        build_params = {
            'tag': f'{self.image_name}:{str(self.tags)}',
            'buildargs': self.build_args,
            'platform': self.platform,
            'cache_from': self.cache_from,
            'extra_hosts': self.extra_hosts,
            'path': self.path,
            'pull': False,
            'nocache': False,
        }
        
        if self.dockerfile_content is not None:
            build_params.update({'dockerfile': self.dockerfile_content})
        
        if self.dockerfile is not None:
            build_params.update({'dockerfile': self.dockerfile})

        build_params = {k: v for k, v in build_params.items() if v is not None}

        try:
            response = self.docker_client.api.build(**build_params, decode=True, forcerm=True, rm=True)

            image_id = None
            is_using_cache = False

            for chunk in response:
                if 'errorDetail' in chunk:
                    error_detail = chunk['errorDetail']
                    console.print(Panel(f"{error_detail['message']}", title="Build Error", style="red"))
                    return False

                if 'stream' in chunk:
                    step_output = chunk['stream'].strip()

                    if "Using cache" in step_output:
                        is_using_cache = True
                        cache_message = step_output.replace("Using cache:", "").strip()
                        #console.print(f"[cyan]Using cache:[/cyan]")
                    elif "Step" in step_output:
                        cached_msg = 'CACHED ' if is_using_cache else ''
                        original_string = step_output[5:]
                        modified_string = f"[{original_string.split(':')[0].strip()}] {original_string.split(':', 1)[1].strip()}"
                        console.print(Text(f'=> {cached_msg} {modified_string}', style="blue"))
                        is_using_cache = False
                    elif "Successfully built" in step_output:
                        # Try to extract the image ID from the step output
                        parts = step_output.split()
                        if len(parts) == 3:
                            image_id = parts[2]
                            break
                    elif "[Warning] The requested image's platform (linux/amd64)" in step_output:
                        pass
                    else:
                        console.print(Text(step_output, style="yellow"))
            if image_id:
                
                from .utils import remove_temp_directory, the_temp_dir
                remove_temp_directory(the_temp_dir)
                        
                console.print(
                    Panel(
                        f"Build Successful\n\n"
                        f"Image Name: {self.image_name}\n"
                        f"Image Tag: {self.tags or 'latest'}",
                        title="Build Status",
                        style="green"
                    )
                )
                # console.print(f"Image ID: {image_id}")
                end_time = time.time()
                total_time = end_time - start_time
                total_time_minutes = total_time / 60
                console.print(f"Total Execution Time: {total_time_minutes:.2f} minutes")
                return True
            else:
                console.print(Panel("Build failed: Unable to retrieve image ID", title="Build Failed", style="red"))
                return False

        except docker.errors.BuildError as e:
            console.print(Panel(f"Docker build failed: {e}", title="Build Error", style="red"))
            return False
        except docker.errors.APIError as e:
            console.print(Panel(f"Docker API error: {e}", title="API Error", style="red"))
            return False
        except Exception as e:
            console.print(Panel(f"An unexpected error occurred during build: {e}", title="Unexpected Error", style="red"))
            console.print(Panel(f"Exception type: {type(e).__name__}", title="Exception Type", style="red"))
            return False

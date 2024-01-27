import os
from .utils import create_temp_directory, the_temp_dir

class DockerfileGenerator:
    def __init__(self):
        self.instructions = []
        self.current_stage = None
        create_temp_directory()

    def from_(self, base_image):
        if self.current_stage:
            self.instructions.append(f'FROM {base_image} AS {self.current_stage}\n')
        else:
            self.instructions.append(f'FROM {base_image}\n')
        return self

    def workdir(self, directory):
        self.instructions.append(f'WORKDIR {directory}\n')
        return self

    def copy(self, source, destination):
        if self.current_stage:
            self.instructions.append(f'COPY --from={self.current_stage} {source} {destination}\n')
        else:
            self.instructions.append(f'COPY {source} {destination}\n')
        return self

    def run(self, command):
        self.instructions.append(f'RUN {command}\n')
        return self

    def cmd(self, command):
        self.instructions.append(f'CMD {command}\n')
        return self

    def expose(self, port):
        self.instructions.append(f'EXPOSE {port}\n')
        return self

    def env(self, key, value):
        self.instructions.append(f'ENV {key} {value}\n')
        return self

    def arg(self, arg_name, default_value=None, env_variable=None):
        if env_variable:
            self.instructions.append(f'ARG {arg_name}=${{{env_variable}:{default_value}}}\n')
        else:
            self.instructions.append(f'ARG {arg_name}={default_value}\n')
        return self

    def label(self, key, value):
        self.instructions.append(f'LABEL {key}="{value}"\n')
        return self

    def user(self, username):
        self.instructions.append(f'USER {username}\n')
        return self

    def stage(self, stage_name):
        self.current_stage = stage_name
        self.instructions.append(f'\n# Stage: {stage_name}\n')
        return self
    
    def apt_install(self, packages):
        if isinstance(packages, str):
            packages = [packages]
        self.instructions.append(f'RUN apt-get update && apt-get -y install {" ".join(packages)} --no-install-recommends\n')
        return self
    

    def set_supervisord(self, supervisord_config_content, destination='/etc/supervisor/conf.d/supervisord.conf'):
        directory = the_temp_dir
        path = "supervisord.conf"

        # Write the supervisord configuration content to the file
        with open(f"{directory}/{path}", "w") as file:
            file.write(supervisord_config_content)

        # Optionally, you can copy the file (assuming self.copy is defined elsewhere)
        self.copy(f'./{directory}/{path}', destination)

        return self
    
    def copy_text(self, content, temp_file, destination):
        directory = the_temp_dir
        path = temp_file

        # Write the supervisord configuration content to the file
        with open(f"{directory}/{path}", "w") as file:
            file.write(content)

        # Optionally, you can copy the file (assuming self.copy is defined elsewhere)
        self.copy(f'./{directory}/{path}', destination)

        return self



    def get_content(self):
        return ''.join(self.instructions)
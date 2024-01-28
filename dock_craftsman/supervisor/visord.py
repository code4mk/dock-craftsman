# https://github.com/Supervisor/supervisor
class SupervisordConfig:
    def __init__(self, logfile='/var/log/supervisord/supervisord.log', logfile_maxbytes='50MB', logfile_backups=10, loglevel='info', pidfile='/var/run/supervisord/supervisord.pid', nodaemon=True, minfds=1024, minprocs=200):
        self.config_content = f'[supervisord]\nlogfile={logfile}\nlogfile_maxbytes={logfile_maxbytes}\nlogfile_backups={logfile_backups}\nloglevel={loglevel}\npidfile={pidfile}\nnodaemon={str(nodaemon).lower()}\nminfds={minfds}\nminprocs={minprocs}\n\n'
        self.programs = []

    def add_program(self, name):
        program = Program(name)
        self.programs.append(program)
        return program

    def generate_config(self):
        for program in self.programs:
            self.config_content += program.generate_config()
        return self.config_content

class Program:
    def __init__(self, name):
        self.name = name
        self.command_val = None
        self.directory_val = None
        self.autostart_val = True
        self.autorestart_val = True
        self.redirect_stderr_val = None
        self.stderr_logfile_val = None
        self.stdout_logfile_val = None

    def command(self, command):
        self.command_val = command
        return self

    def directory(self, directory):
        self.directory_val = directory
        return self

    def autostart(self, autostart):
        self.autostart_val = autostart
        return self

    def autorestart(self, autorestart):
        self.autorestart_val = autorestart
        return self

    def redirect_stderr(self, redirect_stderr):
        self.redirect_stderr_val = redirect_stderr
        return self

    def stderr_logfile(self, stderr_logfile):
        self.stderr_logfile_val = stderr_logfile
        return self

    def stdout_logfile(self, stdout_logfile):
        self.stdout_logfile_val = stdout_logfile
        return self

    def generate_config(self):
        config = f'[program:{self.name}]\n'
        config += f'command={self.command_val}\n'
        if self.directory_val:
            config += f'directory={self.directory_val}\n'
        config += f'autostart={str(self.autostart_val).lower()}\n'
        config += f'autorestart={str(self.autorestart_val).lower()}\n'
        
        if self.redirect_stderr_val:
            config += f'redirect_stderr={str(self.redirect_stderr_val).lower()}\n'
        if self.stderr_logfile_val:
            config += f'stderr_logfile={self.stderr_logfile_val}\n'
        if self.stdout_logfile_val:
            config += f'stdout_logfile={self.stdout_logfile_val}\n'
        config += '\n'
        return config

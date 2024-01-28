# supervisord
from dock_craftsman.supervisor.visord import SupervisordConfig
config = SupervisordConfig(loglevel='info', nodaemon=True)
config.add_program('nginx').command('/usr/sbin/nginx -g "daemon off;"').stderr_logfile('/var/log/nginx/error.log').stdout_logfile('/var/log/nginx/access.log')
config.add_program('django').command('pipenv run python manage.py runserver 0.0.0.0:8000').directory('/var/www/app').stdout_logfile('/var/log/django.log').redirect_stderr(True)
#config.add_program('celery-beat').command('pipenv run celery -A kintaro beat --loglevel=info').directory('/var/www/app').stderr_logfile('/var/log/celery-beat.err.log').stdout_logfile('/var/log/celery-beat.out.log')
#config.add_program('celery-worker').command('pipenv run celery -A kintaro worker --loglevel=info').directory('/var/www/app').stderr_logfile('/var/log/celery-worker.err.log').stdout_logfile('/var/log/celery-worker.out.log')
supervisord_config_content = config.generate_config()

#nginx
nginx_config = '''
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''

# Import the DockerfileGenerator class
from dock_craftsman.dockerfile_generator import DockerfileGenerator
from dock_craftsman.docker_image_builder import DockerImageBuilder

# Instantiate the DockerfileGenerator
dockerfile = DockerfileGenerator()

# Use the official Python 3.11.6 (slim) image
dockerfile.from_('python:3.11.6-slim')

# Set environment variables
dockerfile.env('PYTHONDONTWRITEBYTECODE', '1')
dockerfile.env('PYTHONUNBUFFERED', '1')

# Update the package list and install necessary packages
dockerfile.apt_install('supervisor')
dockerfile.apt_install('nginx')

# Copy Nginx configuration to the container
dockerfile.copy_text(nginx_config,'nginx-app.conf', '/etc/nginx/sites-enabled/app.conf')

# Copy Supervisor configuration to the container
dockerfile.set_supervisord(supervisord_config_content)

# Create the log and run directories for supervisord
dockerfile.run('mkdir -p /var/log/supervisord /var/run/supervisord')

# Set the working directory
dockerfile.workdir('/var/www/app')

# Copy requirements.txt and Pipfile.lock to the container
dockerfile.copy('Pipfile.lock', '/var/www/app/')

# Install project dependencies using pip and pipenv
dockerfile.run('pip install pipenv')
dockerfile.run('pipenv install --ignore-pipfile --verbose')

# Copy the rest of your project files to the container
dockerfile.copy('.', '.')

# Expose the port if your Django project uses it
dockerfile.expose(8000)

# Set the command to start supervisord
dockerfile.cmd('supervisord -n -c /etc/supervisor/conf.d/supervisord.conf')

# Get the content of the generated Dockerfile
generated_dockerfile = dockerfile.get_content()

# Print the generated Dockerfile
print(generated_dockerfile)


b = DockerImageBuilder()
b.set_platform('linux/amd64')
b.set_name('drf_friend_api')
b.set_tag('1.0.1')
b.set_content(generated_dockerfile)
b.build()

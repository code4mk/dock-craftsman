php_version = "8.2"  # Specify the PHP version you want

# supervisord
from dock_craftsman.supervisor.visord import SupervisordConfig
config = SupervisordConfig(loglevel='debug', nodaemon=True)
config.add_program('nginx').command('/usr/sbin/nginx -g "daemon off;"').stdout_logfile('/var/log/nginx/access.log').redirect_stderr(True)
config.add_program('php-fpm').command(f'/usr/sbin/php-fpm{php_version} -F').stderr_logfile(f'/var/log/php/php-fpm.log').stdout_logfile(f'/var/log/php/php-fpm.log').redirect_stderr(True)
supervisord_config_content = config.generate_config()

#nginx
nginx_config = f'''
server {{
    listen 81;
    server_name localhost;
    root /var/www/app/public;

    index index.php index.html index.htm;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php{php_version}-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }}

    error_log  /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
}}
'''

# Import the DockerfileGenerator class
from dock_craftsman.dockerfile_generator import DockerfileGenerator
from dock_craftsman.docker_image_builder import DockerImageBuilder

# Create an instance of the DockerfileGenerator
dockerfile = DockerfileGenerator()

# Base image and timezone configuration
dockerfile.from_('ubuntu:latest')
dockerfile.env('TZ', 'Europe/Minsk')
dockerfile.run('ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone')

# Install necessary packages
dockerfile.run('apt-get update && '
               'apt-get install -y curl zip unzip supervisor && '
               'apt-get clean && '
               'rm -rf /var/lib/apt/lists/*')

# Add Ondrej PHP repository and install PHP extensions
php_packages = ' '.join([f'php{php_version}-{ext}' for ext in [
    'bcmath', 'ctype', 'fileinfo', 'mbstring', 'pdo',
    'tokenizer', 'xml', 'dom', 'mysql', 'sqlite'
]])

dockerfile.run(f'apt-get update && '
               f'apt-get install -y software-properties-common && '
               f'add-apt-repository ppa:ondrej/php && '
               f'apt-get update && '
               f'apt-get install -y php{php_version} php{php_version}-fpm  {php_packages}')

# Create the PHP-FPM socket directory
dockerfile.run("mkdir -p /run/php/")

# Install Nginx and configure
dockerfile.run('apt-get update && apt-get install -y nginx')
dockerfile.copy_text(nginx_config, 'nginx-app.conf', '/etc/nginx/sites-enabled/app.conf')

# Configure supervisor
dockerfile.set_supervisord(supervisord_config_content)

# Install Composer
dockerfile.run('curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer')

# Set working directory and copy project code
dockerfile.workdir('/var/www/app')
dockerfile.copy('.', '.')

# Assign storage permission
dockerfile.run('mkdir -p /var/log/php /var/log/nginx && chown -R www-data:www-data /var/log/php /var/log/nginx')
dockerfile.run('chown -R www-data:www-data /var/www/app/storage && chmod -R 775 /var/www/app/storage')

# Install dependencies with Composer
dockerfile.run('composer install --no-interaction --no-dev --prefer-dist --ignore-platform-req=ext-dom')

# Generate application key
dockerfile.run('php artisan key:generate')

# Expose port for Nginx
dockerfile.expose(81)

# Create the log and run directories for supervisord
dockerfile.run('mkdir -p /var/log/supervisord /var/run/supervisord')

# Start Supervisor
dockerfile.cmd(f'supervisord -n -c /etc/supervisor/conf.d/supervisord.conf')

# Get the generated Dockerfile content
generated_dockerfile = dockerfile.get_content()

print(generated_dockerfile)

# Build the Docker image
b = DockerImageBuilder()
b.set_platform('linux/amd64')
b.set_name('laravel_friend_api')
b.set_tag('1.0.1')
b.set_content(generated_dockerfile)
b.build()

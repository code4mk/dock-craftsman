#!/bin/bash

# Prompt user to choose a package manager
read -p "Install dock-craftsman using pip, pip3, pipenv, or poetry? " the_pkg_manager

# Install dock-craftsman using the specified package manager
case $the_pkg_manager in
    pip | pip3 | pipenv | poetry)
        $the_pkg_manager install dock-craftsman
        ;;
    *)
        # Invalid choice
        echo "Invalid package manager choice. Exiting."
        exit 1
        ;;
esac

# Download build_image.py script
echo "Downloading build_image.py..."
curl -o build_image.py -LJO https://raw.githubusercontent.com/code4mk/dock-craftsman/main/template/python/django/build_image.py

# Modify build_image.py
echo "Modifying build_image.py"
echo "Run script with python3: python3 ./build_image.py"
echo "Run script with python: python ./build_image.py"

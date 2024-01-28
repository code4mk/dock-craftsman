#!/bin/bash

# Prompt user to choose a package manager
read -p "🚀 Install dock-craftsman using pip, pip3, pipenv, poetry, or no? " the_pkg_manager

# Check if the user opted for 'no'
if [ "$the_pkg_manager" == "no" ]; then
    echo "🛑 Skipping installation. Assuming dock-craftsman is already installed."
elif [ "$the_pkg_manager" == 'pipenv' ]; then
    pipenv install dock-craftsman
elif [ "$the_pkg_manager" == 'pip' || "$the_pkg_manager" == 'pip3' || "$the_pkg_manager" == 'poetry' ]; then
    # Install dock-craftsman using the specified package manager
    $the_pkg_manager install dock-craftsman
else
    # Invalid choice
    echo "❌ Invalid package manager choice. Exiting."
    exit 1
fi

# Download build_image.py script
echo "🔄 Downloading build_image.py..."
curl -o build_image.py -LJO https://raw.githubusercontent.com/code4mk/dock-craftsman/main/template/python/django/build_image.py

# Modify build_image.py
echo "🔧 Modifying build_image.py"
echo "🚀 Run script with python3: python3 ./build_image.py"
echo "🚀 Run script with python: python ./build_image.py"

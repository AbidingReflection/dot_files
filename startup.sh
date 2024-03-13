#!/bin/bash

echo "Starting setup..."

# Simple loading function
loading() {
    echo -n "Processing: "
    for i in {1..10}; do
        echo -n "#"
        sleep 1
    done
    echo " Done."
}

# Update the package lists
echo "Updating package lists..."
sudo apt update && echo "Package lists updated."

# Install dependencies
echo "Installing required packages..."
sudo apt install -y python3 python3-pip man man-db ninja-build gettext libtool libtool-bin autoconf automake cmake g++ pkg-config unzip curl doxygen git wget && echo "Required packages installed."
loading  # Show loading for installation process

# Check if the Neovim directory already exists
if [ ! -d "/opt/neovim" ]; then
    echo "Cloning Neovim repository..."
    sudo git clone https://github.com/neovim/neovim.git /opt/neovim && echo "Repository cloned."
    
    cd /opt/neovim || exit
    sudo git checkout tags/v0.9.2 && echo "Checked out v0.9.2."
    
    # Change ownership of the /opt/neovim directory to the current user
    sudo chown -R "$(whoami):$(whoami)" /opt/neovim && echo "Changed ownership of /opt/neovim."
    
    echo "Building Neovim..."
    sudo make CMAKE_BUILD_TYPE=RelWithDebInfo && sudo make install && echo "Neovim installed."
else
    echo "Neovim directory already exists. Consider pulling updates or skipping this step."
fi

# Ensure the .config/nvim directory exists for the current user
echo "Configuring Neovim..."
mkdir -p "/home/jake/.config/nvim" && echo "/home/jake/.config/nvim/ directory ensured."

# Check if init.lua file exists before downloading
if [ ! -f "/home/jake/.config/nvim/init.lua" ]; then
    echo "Downloading init.lua..."
    curl -o "/home/jake/.config/nvim/init.lua" https://raw.githubusercontent.com/AbidingReflection/dot_files/main/neovim/init.lua && echo "init.lua downloaded."
else
    echo "init.lua already exists. Skipping download."
fi

# Check if ~/.bash_aliases exists and append aliases
echo "Configuring bash aliases..."
if [ ! -f "/home/jake/.bash_aliases" ]; then
    touch "/home/jake/.bash_aliases" && echo "Created /home/jake/.bash_aliases."
fi

if ! grep -q "alias ll=" "/home/jake/.bash_aliases"; then
    echo "alias ll='ls -lha --color=auto --group-directories-first'" >> "/home/jake/.bash_aliases" && echo "Alias ll added."
fi

if ! grep -q "alias vim=" "/home/jake/.bash_aliases"; then
    echo "alias vim='nvim'" >> "/home/jake/.bash_aliases" && echo "Alias vim added."
fi

source "/home/jake/.bashrc"

echo "Setup completed. Please log out and log back in or run 'source ~/.bashrc' to apply alias changes."

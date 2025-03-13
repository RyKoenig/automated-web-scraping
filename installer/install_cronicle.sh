#!/bin/bash

# Exit immediately if a command fails
set -e

# Define the non-root user who will install Node.js
NON_ROOT_USER=$(logname)

echo "Installing Node.js as $NON_ROOT_USER using NVM..."

# Switch to the non-root user to install NVM & Node.js
sudo -u "$NON_ROOT_USER" bash <<EOF
    set -e
    export NVM_DIR="/home/$NON_ROOT_USER/.nvm"
    if [ ! -d "\$NVM_DIR" ]; then
        echo "Installing NVM..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    fi

    # Load NVM
    export NVM_DIR="/home/$NON_ROOT_USER/.nvm"
    [ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"
    [ -s "\$NVM_DIR/bash_completion" ] && . "\$NVM_DIR/bash_completion"

    # Install Node.js
    echo "Installing Node.js..."
    nvm install 16
    nvm use 16
EOF

echo "Node.js installation complete."

# Switch to root to install Cronicle
echo "Switching to installing Cronicle (must be run as root)..."

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Restarting script as root..."
    exec sudo "$0"
fi

# Load NVM (Node Version Manager)
export NVM_DIR="/home/$SUDO_USER/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"

# Ensure Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install it first using install_node.sh."
    exit 1
fi

echo "Installing Cronicle..."
curl -s https://raw.githubusercontent.com/jhuckaby/Cronicle/master/bin/install.js | node

# Set up Cronicle
echo "Setting up Cronicle..."
/opt/cronicle/bin/control.sh setup

# Start Cronicle service
echo "Starting Cronicle..."
/opt/cronicle/bin/control.sh start

# Change ownership so the non-root user can manage it
echo "Changing ownership of Cronicle to $SUDO_USER..."
chown -R "$SUDO_USER":"$SUDO_USER" /opt/cronicle

echo -e "\nCronicle installation completed!"

echo -e "\nAccess Cronicle at: http://<YOUR_SERVER_IP>:3012"
echo "Default login: admin / admin (change immediately)"

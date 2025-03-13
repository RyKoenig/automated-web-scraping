#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Downloading and installing Miniconda..."

# Download Miniconda installer
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh

# Run the installer
bash miniconda.sh -b -p $HOME/miniconda

# Remove installer file
rm miniconda.sh

# Initialize conda for shell use
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/bin/activate"
conda init bash

source ~/.bashrc

echo "Miniconda installed successfully!"

# Verify installation
conda --version


# =============================
# CREATE CONDA ENVIRONMENT
# =============================

INSTALLER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$INSTALLER_DIR/environment.yml"

if [ ! -f "$ENV_FILE" ]; then
    echo "environment.yml not found in $INSTALLER_DIR"
    exit 1
fi

echo "Creating Conda environment from environment.yml..."

# Create the environment
conda env create -f "$ENV_FILE"

echo "Conda environment created successfully!"

# # Activate the new environment
ENV_NAME=$(head -n 1 "$ENV_FILE" | cut -d ' ' -f 2)
# echo "Activating Conda environment: $ENV_NAME"
# conda activate "$ENV_NAME"

# # Verify installed packages
conda list

echo -e "Setup complete! You will need to restart your shell or run \n\nsource ~/.bashrc\n\nthen 'conda activate $ENV_NAME' to start using your new conda environment."


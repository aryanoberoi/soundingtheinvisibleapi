#!/bin/bash

# Define the repository URL
REPO_URL="https://github.com/aryanoberoi/soundingtheinvisibleapi"
# Clone the repository
git clone $REPO_URL

# Extract the repository name from the URL
REPO_NAME=$(basename $REPO_URL .git)

# Change directory into the cloned repository
cd $REPO_NAME

# Install the required Python packages
pip install -r requirements.txt

# Run the main Python script
python main_server.py
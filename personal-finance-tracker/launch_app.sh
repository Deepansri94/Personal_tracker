#!/bin/bash

# Set your project directory here
PROJECT_DIR="./"   

# Move into project directory
cd "$PROJECT_DIR" || { echo "Folder not found"; exit 1; }

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/Scripts/activate


# Install required packages
pip install --upgrade pip
pip install -r requirements-local.txt

# Run the Streamlit app
streamlit run app.py

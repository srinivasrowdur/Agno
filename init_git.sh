#!/bin/bash

# Initialize Git repository
echo "Initializing Git repository..."
git init

# Add all files to Git
echo "Adding files to Git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "Initial commit for Agno API project"

# Instructions for setting up remote repository
echo ""
echo "Git repository initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create a repository on GitHub, GitLab, or your preferred Git hosting service"
echo "2. Add the remote repository URL:"
echo "   git remote add origin <repository-url>"
echo "3. Push the code to the remote repository:"
echo "   git push -u origin main"
echo "" 
#!/bin/bash

# Script to push Napocalypse code to GitHub
# Run this from your local machine after downloading the napocalypse folder

echo "Pushing Napocalypse to GitHub..."

# Navigate to the napocalypse directory
cd "$(dirname "$0")"

# Add the remote if it doesn't exist
git remote add origin https://github.com/obscurepedia/napocalypse.git 2>/dev/null || true

# Add all files
git add .

# Commit any remaining changes
git commit -m "Complete Napocalypse application with all modules" || true

# Push to GitHub
git push -u origin main

echo "Done! Check https://github.com/obscurepedia/napocalypse to verify."
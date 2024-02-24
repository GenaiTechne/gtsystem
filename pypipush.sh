#!/bin/bash

# Step 1: Increment the patch version in pyproject.toml
# Read the current version using sed
current_version=$(sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml)
# Break the version into parts
IFS='.' read -ra ver <<< "$current_version"
# Increment the patch version
patch_version=$((ver[2] + 1))
# Construct the new version
new_version="${ver[0]}.${ver[1]}.$patch_version"
# Update pyproject.toml with the new version
sed -i '' "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml

echo "Updated version to $new_version"

# Step 2: Delete contents of dist/ folder
rm -rf dist/*

# Step 3: Run command python3 -m build
python3 -m build

# Step 4: Run python3 -m twine upload --repository pypi dist/*
# Automate the entry of username and password using an environment variable
echo "Uploading package to PyPI..."
echo "$PYPI_USERNAME" | python3 -m twine upload --repository pypi dist/* -u "$PYPI_USERNAME" -p "$PYPI_API_TOKEN"
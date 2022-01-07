#!/bin/sh
echo "System Update"
toolbox run -c $1 sudo dnf upgrade -y

echo ""
echo "Install Basic Packages"
toolbox run -c $1 sudo dnf install fish starship exa -y

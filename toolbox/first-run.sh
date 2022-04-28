#!/bin/sh
echo "Dnf Configuration"
toolbox run -c $1 sudo sh -c "echo 'deltarpm=true' >> /etc/dnf/dnf.conf"
toolbox run -c $1 sudo sh -c "echo 'max_parallel_downloads=12' >> /etc/dnf/dnf.conf"

echo "System Update"
toolbox run -c $1 sudo dnf upgrade -y

echo ""
echo "Install Basic Packages"
toolbox run -c $1 sudo dnf install fish starship exa direnv -y

SHELL=/bin/fish toolbox enter -c $1


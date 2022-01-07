#!/bin/sh
container_list=($(toolbox list -c | awk '{if (NR!=1) {print $2}}'))

for i in "${container_list[@]}"
do
  echo "Updating" $i
  toolbox run -c $i sudo dnf upgrade -y
  echo ""
done

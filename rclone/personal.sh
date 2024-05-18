#!/bin/sh
toolbox run -c rclone rclone bisync PersonalDrive:Personal\ Docs/ ~/Documents/PersonalDocs -P -v

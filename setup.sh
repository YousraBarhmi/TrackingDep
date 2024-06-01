#!/bin/bash

# Install libGL
sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx

# Update package lists
sudo apt-get update

# Install libgl1
sudo apt-get install -y libgl1-mesa-glx

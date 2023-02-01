#!/bin/bash
cd /home/ubuntu
chmod +x /home/ubuntu/ssrf.js
sudo apt update -y
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
npm init -y
npm install express axios 
npm install -g pm2 
pm2 start ssrf.js -f
echo ". $NVM_DIR/nvm.sh" >> ~/.bashrc
source ~/.bashrc

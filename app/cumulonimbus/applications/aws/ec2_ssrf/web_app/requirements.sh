#!/usr/bin/env bash
sudo apt update -y
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
. ~/.nvm/nvm.sh
nvm install --lts
npm init -y
npm install express --save
npm install axios --save
node ssrf.js
#!/usr/bin/env bash

sudo apt-get install -y pip libsqlite3-dev
output=$(tail -n 1 ~/.bashrc | grep 'echo export PATH=$HOME/.local/bin:$PATH')
if [ -z "$output" ]; then
  echo "Not set path, set path"
  echo "export PIPENV_MIRROR_URL=https://pypi.tuna.tsinghua.edu.cn/simple" >>~/.bashrc
  echo "export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple" >>~/.bashrc
  echo "export PATH=\$HOME/.local/bin:\$PATH" >>~/.bashrc
  source ~/.bashrc
fi
make init
pip show pyinstaller
if [ $? -ne 0 ]; then
  pip install pyinstaller
fi

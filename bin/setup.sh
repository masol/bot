#!/usr/bin/env bash

if ! command -v swipl &> /dev/null
then
    echo "SWI-Prolog is not installed. Do you want to install it now? (y/n)"
    if [ "$answer" = "y" ]; then
        sudo apt-add-repository -y ppa:swi-prolog/stable
        sudo apt-get -y update
        sudo apt-get -y install swi-prolog
    else
        echo "Installation cancelled."
        exit 1
    fi
fi
sudo apt-get install -y pip libsqlite3-dev swi-prolog python3-testresources
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
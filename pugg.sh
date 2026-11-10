#!/bin/bash
read -rp 'Search term: ' term; 
choice=$(python cli.py --search "$term" | fzf) \
&& [[ -n $choice ]] && \
python cli.py --play "$choice"

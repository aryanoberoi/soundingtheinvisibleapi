#!/usr/bin/env bash
set -euf -o pipefail

tmux -2 attach-session -t sti || tmux -2 \
  new-session -s sti \; \
  split-window -v -t sti \; \
  send-keys -t 0 "cd ~/Dev/soundingtheinvisibleapi" C-m \; \
  send-keys -t 0 "sclang soundserver.scd" C-m \; \
  send-keys -t 1 "source invisible-sound/bin/activate" C-m \; \
  send-keys -t 1 "python main_server.py" C-m \; \
  select-pane -t 0

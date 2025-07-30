function change-tank() {
  sudo raspi-config nonint do_hostname invisible-sound-$@.local;
}

function change-wifi() {
  sudo raspi-config nonint do_wifi_ssid_passphrase $1 '$2'
}

function update-api() {
  cd ~/Dev/soundingtheinvisibleapi
  git pull
}

alias soundserver="cd ~/Dev/soundingtheinvisibleapi && sclang soundserver.scd"
alias invisible-sound="~/Dev/soundingtheinvisibleapi/run.sh"
alias edit-wifi="sudo nano /boot/firmware/wpa_supplicant.conf"
alias check-wifi="iwconfig"
alias attach-server="tmux attach -t sti"
alias check-sound-logs="journalctl --user-unit supercollider"
alias clear-sound-logs="sudo journalctl --rotate --vacuum-time=1d unit=supercollider.service"
alias restart-sound-server="systemctl --user daemon-reload && systemctl --user restart supercollider.service"

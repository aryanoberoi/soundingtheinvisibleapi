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

export JACK_NO_AUDIO_RESERVATION=1
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:0
alias invisible-sound="~/Dev/soundingtheinvisibleapi/run.sh"
alias edit-wifi="sudo nano /boot/firmware/wpa_supplicant.conf"
alias check-wifi="iwconfig"
alias attach-server="tmux attach -t sti"
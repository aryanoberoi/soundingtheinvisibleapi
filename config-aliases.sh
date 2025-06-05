function change-tank() {
  sudo raspi-config nonint do_hostname invisible-sound-$@.local;
}

export JACK_NO_AUDIO_RESERVATION=1
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:0
alias invisible-sound="~/Dev/soundingtheinvisibleapi/run.sh"
alias change-wifi="sudo nano /boot/firmware/wpa_supplicant.conf"
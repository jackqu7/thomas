#!/bin/bash
set -e

if [ -z "$SSID" ]; then
    echo "Must pass SSID env var"
    exit 1
fi
if [ -z "$PASSWORD" ]; then
    echo "Must pass PASSWORD env var"
    exit 1
fi

cd /home/pi

# Put jack pubkey on box
mkdir -p .ssh
cat > .ssh/authorized_keys << EOF
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCju8fl4dgou4tnGA0aEcrZ7xNha7zlaMARFMX9+r8hvYJFuliWHOAgv2VLzO6IdhrxqL4XgcmIk6jZldYZ+49WqxxIawDHiJpY1cAq1H3uPBk7npdvHdCCs9pfoeN01pZsJZtit2K5naGE5XtVV8EnqK5gMhtdoL+3ECnlZV0jxkS5565eSzYdsTLnnIvy5FMjy1EvIlHhZnA/Fmtz3bx4APdQeYJjg76ZwtTwwP7j4obPrY2e+KsGkyekz5nivLVoJK1JHtKB4khXGEmDbcNzPJhzSnsL29QOImqK5/qGboJXOqzGpQ6GUIwml7JV5hZyISyknD5JVer9nxk+v/GL jack@unknown
EOF
chown -R pi: .ssh

# Change runlevel to 2
ln -fs /lib/systemd/system/multi-user.target /etc/systemd/system/default.target

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get upgrade -y

# Install deps from apt
apt-get -y install aptitude build-essential git-core htop libfreetype6-dev libjpeg-dev liblircclient-dev lirc python3 python3-numpy python3-pil python3-rpi.gpio python3-tk python3.4-dev traceroute vim wget wicd wicd-curses wpasupplicant zlib1g-dev supervisor

cd /home/pi

# Install wiringPi because it's useful
if [ ! -d wiringPi ]; then
  git clone git://git.drogon.net/wiringPi
  cd wiringPi
else
  cd wiringPi
  git pull origin
fi

./build

cd ..

# Install thomas
if [ ! -d thomas ]; then
  git clone https://github.com/jackqu7/thomas.git
  cd thomas
else
  cd thomas
  git pull origin
fi
pip3 install -r requirements.txt
python3 setup.py develop

# Install font
if [ ! -e assets/font.ttf ]; then
  mkdir -p /tmp/font
  cd /tmp/font
  wget http://dl.dafont.com/dl/?f=enhanced_led_board_7 -O font.zip
  unzip font.zip
  cp enhanced_led_board-7.ttf /home/pi/thomas/assets/font.ttf
fi

cd /home/pi
chown -R pi: thomas

# Create log dir
mkdir -p log

# Put thomas in supervisor conf
cat > /etc/supervisor/conf.d/thomas.conf << EOF
[program:thomas]
command=/usr/bin/python3 thomas/run.py
directory=/home/pi/thomas
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/pi/log/thomas.log
stdout_logfile_backups=2
priority=0
umask=022
EOF

# enable spi module, enable lirc module, decrease video mem
if [ -z "$(grep "gpio_in_pin" /boot/config.txt)" ]; then
  cat >> /boot/config.txt << EOF
dtoverlay=lirc-rpi,gpio_in_pin=4
gpu_mem=16
dtparam=spi=on
EOF
fi

# lirc config
cat > /etc/lirc/lircd.conf << EOF
# Please make this file available to others
# by sending it to <lirc@bartelmus.de>
#
# this config file was automatically generated
# using lirc-0.9.0-pre1(default) on Sat Oct 17 14:22:30 2015
#
# contributed by
#
# brand:                       /home/pi/out.conf
# model no. of remote control:
# devices being controlled by this remote:
#

begin remote

  name  /home/pi/out.conf
  bits           16
  flags SPACE_ENC|CONST_LENGTH
  eps            30
  aeps          100

  header       8976  4433
  one           595  1641
  zero          595   522
  ptrail        599
  repeat       8980  2198
  pre_data_bits   16
  pre_data       0xFF
  gap          107436
  toggle_bit_mask 0x0

      begin codes
          KEY_POWER                0xB24D
          KEY_SWITCHVIDEOMODE      0x2AD5
          KEY_MUTE                 0x6897
          KEY_RECORD               0x32CD
          KEY_CHANNELUP            0xA05F
          KEY_TIME                 0x30CF
          KEY_VOLUMEDOWN           0x50AF
          KEY_ZOOM                 0x02FD
          KEY_VOLUMEUP             0x7887
          BTN_0                    0x48B7
          KEY_CHANNELDOWN          0x40BF
          KEY_BACK                 0x38C7
          BTN_1                    0x906F
          BTN_2                    0xB847
          BTN_3                    0xF807
          BTN_4                    0xB04F
          BTN_5                    0x9867
          BTN_6                    0xD827
          BTN_7                    0x8877
          BTN_8                    0xA857
          BTN_9                    0xE817
      end codes

end remote
EOF

cat > /etc/lirc/hardware.conf << EOF
# /etc/lirc/hardware.conf
#
# Arguments which will be used when launching lircd
LIRCD_ARGS=""

#Don't start lircmd even if there seems to be a good config file
#START_LIRCMD=false

#Don't start irexec, even if a good config file seems to exist.
#START_IREXEC=false

#Try to load appropriate kernel modules
LOAD_MODULES=true

# Run "lircd --driver=help" for a list of supported drivers.
DRIVER="default"
# usually /dev/lirc0 is the correct setting for systems using udev
DEVICE="/dev/lirc0"
MODULES=""

# Default configuration files for your hardware if any
LIRCD_CONF=""
LIRCMD_CONF=""
EOF

cat > /etc/lirc/lircrc << EOF
begin
    button = KEY_POWER
    prog = irexec
    config = halt
    repeat = 1
end
EOF

# Wifi config
if [ -z "$(grep "network=" /etc/wpa_supplicant/wpa_supplicant.conf)" ]; then
  cat >> /etc/wpa_supplicant/wpa_supplicant.conf << EOF
network={
    ssid="$SSID"
    psk="$PASSWORD"
}
EOF
fi

echo '----------------------------'
echo Successfully Bootstrapped
echo Now reboot


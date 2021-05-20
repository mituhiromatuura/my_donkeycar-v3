#!/bin/bash

DOUBLE="/run/shm/doublestart.txt"

if [ $1 = "0" ]; then
  FILE="/run/shm/autostart.txt"
  if [ ! -e $FILE ]; then
    echo -n > $FILE
    exit
  fi
else
  if [ $1 = "d" ]; then
    rm $DOUBLE
  fi
  if [ $1 = "a" ]; then
    rm $DOUBLE
  fi
  if [ $1 = "s" ]; then
    rm $DOUBLE
  fi
fi

if [ -e $DOUBLE ]; then
  exit
fi
echo -n > $DOUBLE

#hostname="mini2018"
#hostname="mbp2008"
hostname="mba2010"
#ramdisk="RamDisk_1G"
ramdisk="RamDisk_2G"

TUB=/run/shm/mycar/data/tub

if [ $1 != "s" ]; then

rm -r /run/shm/mycar/
mkdir /run/shm/mycar
mkdir /run/shm/mycar/data

rm ./models/*.png
sudo pigpiod

if [ $1 != "a" ]; then
  #python manage.py drive $1
  python manage.py drive --js
else
  #python manage.py drive --model=./models/mypilot.h5 --js
  python manage.py drive --model=./models/mypilot-aug.tflite --type coral_tflite_linear --js
fi
sudo killall -9 pigpiod
sudo rm -rf /var/run/pigpio.pid

read -p "Hit enter: sudo zip"

cp config.py /run/shm/mycar/
cp myconfig.py /run/shm/mycar/
if [ $1 = "a" ]; then
  cp -r ~./models /run/shm/mycar/
fi

ymdhm=`date "+%Y%m%d%H%M"`

LOGS="/media/pi/MYCAR_LOGS"
if [ ! -e $LOGS ]; then
    LOGS="./logs"
fi

if [ $1 != "a" ]; then
  sudo zip -rq $LOGS/log_${ymdhm}_drive.zip /run/shm/mycar/
  sudo chown pi:pi $LOGS/log_${ymdhm}_drive.zip
else
  sudo zip -rq $LOGS/log_${ymdhm}_auto.zip /run/shm/mycar/
  sudo chown pi:pi $LOGS/log_${ymdhm}_auto.zip
fi

read -p "Hit enter: rsync *.json"
rsync -rtv --delete $TUB/*.json work@$hostname.local:/Volumes/$ramdisk/data/

read -p "Hit enter: makemovie"
donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_movie.mp4 --scale 1

read -p "Hit enter: rsync movie"
rsync -rtv $LOGS/log_${ymdhm}_movie.mp4 work@$hostname.local:/Volumes/$ramdisk/

#else
#
#read -p "rsync movie input filename: "
#read fn
#rsync -rtv $LOGS/$fn work@$hostname.local:/Volumes/$ramdisk/
#
fi

read -p "Hit enter: updown"
echo -n "input path: "
read str
rsync -rtv /run/shm/mycar work@ddprog.mydns.jp:/run/shm/$str/

echo $str
read -p "Hit enter: get model file"
rsync -rtv --delete work@ddprog.mydns.jp:/run/shm/$str/mycar/models ./

rm $DOUBLE

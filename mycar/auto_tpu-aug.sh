#!/bin/bash

FILE="/run/shm/autostart.txt"
if [ ! -e $FILE ]; then
  echo -n > $FILE
  exit
fi

DOUBLE="/run/shm/doublestart.txt"
if [ -e $DOUBLE ]; then
  exit
fi
echo -n > $DOUBLE

#hostname="mini2018"
#hostname="mbp2008"
hostname="mba2010"
#ramdisk="RamDisk_1G"
ramdisk="RamDisk_2G"

rm -r /run/shm/mycar/
rm ./models/*.png
sudo pigpiod

#python manage.py drive --model=/run/shm/mycar/models/mypilot $1
#python manage.py drive --model=./models/mypilot.h5 $1
#python manage.py drive --model=./models/mypilot.h5 --js
python manage.py drive --model=./models/mypilot-aug.tflite --type coral_tflite_linear --js

sudo killall -9 pigpiod
sudo rm -rf /var/run/pigpio.pid

read -p "Hit enter: sudo zip"

cp config.py /run/shm/mycar/
cp myconfig.py /run/shm/mycar/
cp -r ~/mycar/models /run/shm/mycar/

ymdhm=`date "+%Y%m%d%H%M"`

logs="/media/pi/MYCAR_LOGS"
if [ ! -e $logs ]; then
    logs="~/mycar/logs"
fi

sudo zip -rq $logs/log_${ymdhm}_auto.zip /run/shm/mycar/
sudo chown pi:pi $logs/log_${ymdhm}_auto.zip

read -p "Hit enter: rsync *.json"
rsync -rtv --delete /run/shm/mycar/data/*.json work@$hostname.local:/Volumes/$ramdisk/data/

read -p "Hit enter: makemovie"
donkey makemovie --tub /run/shm/mycar/data/ --out $logs/log_${ymdhm}_movie.mp4 --scale 1

read -p "Hit enter: rsync movie"
rsync -rtv $logs/log_${ymdhm}_movie.mp4 work@$hostname.local:/Volumes/$ramdisk/

read -p "Hit enter: updown"
echo -n "input path: "
read str
rsync -rtv /run/shm/mycar work@ddprog.mydns.jp:/run/shm/$str/

echo $str
read -p "Hit enter: get model file"
rsync -rtv --delete work@ddprog.mydns.jp:/run/shm/$str/mycar/models ~/mycar/

rm $DOUBLE

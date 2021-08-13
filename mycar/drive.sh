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
  if [ $1 = "z" ]; then
    rm $DOUBLE
  fi
  if [ $1 = "m" ]; then
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
#ramdisk="RamDisk_2G"
ramdisk="RamDisk"

MYCAR=/run/shm/mycar
TUB=$MYCAR/data/tub

ymdhm=`date "+%Y%m%d%H%M"`

LOGS="/media/pi/MYCAR_LOGS"
if [ ! -e $LOGS ]; then
    LOGS="/home/pi/projects/my_donkeycar-v3/mycar/logs"
fi

if [ $1 != "m" -a $1 != "s" ]; then

if [ $1 != "z" ]; then

rm -r $MYCAR/
mkdir $MYCAR
mkdir $MYCAR/data

rm ./models/*.png
sudo pigpiod

vcgencmd measure_clock arm
vcgencmd measure_temp

if [ $1 != "a" ]; then
  #python manage.py drive $1
  python manage.py drive --js
else
  #python manage.py drive --model=./models/mypilot.h5 --js
  if [ $2 == ""]; then
    MODEL=./models/mypilot-aug.tflite
  else
    MODEL=$2
  fi
  python manage.py drive --model=$MODEL --type coral_tflite_linear --js
fi
sudo killall -9 pigpiod
sudo rm -rf /var/run/pigpio.pid

vcgencmd measure_clock arm
vcgencmd measure_temp

fi

read -p "Hit enter: sudo zip"

cp config.py $MYCAR/
cp myconfig.py $MYCAR/
if [ $1 = "a" ]; then
  cp -r ./models $MYCAR/
fi

pushd /run/shm
if [ $1 != "a" ]; then
  sudo zip -rq $LOGS/log_${ymdhm}_drive.zip mycar
  sudo chown pi:pi $LOGS/log_${ymdhm}_drive.zip
else
  sudo zip -rq $LOGS/log_${ymdhm}_auto.zip mycar
  sudo chown pi:pi $LOGS/log_${ymdhm}_auto.zip
fi
popd

read -p "Hit enter: rsync log.csv"
rsync -rtv --delete $MYCAR/data/log.csv work@$hostname.local:/Volumes/$ramdisk/

fi
if [ $1 != "s" ]; then

read -p "Hit enter: makemovie"
if [ $1 != "a" ]; then
  donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_drive.mp4 --scale 1
  read -p "Hit enter: rsync movie"
  rsync -rtv $LOGS/log_${ymdhm}_drive.mp4 work@$hostname.local:/Volumes/$ramdisk/
else
  donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_auto.mp4 --scale 1
  read -p "Hit enter: rsync movie"
  rsync -rtv $LOGS/log_${ymdhm}_auto.mp4 work@$hostname.local:/Volumes/$ramdisk/
fi

fi

read -p "Hit enter: updown"
echo -n "input path: "
read str
rsync -rtv $MYCAR work@ddprog.mydns.jp:/run/shm/$str/

echo $str
read -p "Hit enter: get model file"
rsync -rtv --delete work@ddprog.mydns.jp:/run/shm/$str/mycar/models ./
cp ./models/mypilot-aug.h5 ./models/mypilot-aug_${ymdhm}.h5
cp ./models/mypilot-aug.tflite ./models/mypilot-aug_${ymdhm}.tflite

rm $DOUBLE

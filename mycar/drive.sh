#!/bin/bash

DOUBLE="/run/shm/doublestart.txt"

if [ $1 = "0" ]; then
  FILE="/run/shm/autostart.txt"
  if [ ! -e $FILE ]; then
    echo -n > $FILE
    exit
  fi
else
  if [ $1 = "d" ] || [ $1 = "a" ] || [ $1 = "z" ] || [ $1 = "m" ] || [ $1 = "up" ] || [ $1 = "down" ] || [ $1 = "s" ]; then
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

if [ $1 = "0" ] || [ $1 = "d" ] || [ $1 = "a" ]; then

  LAST=$(</dev/shm/date.txt)
  while true; do
    NOW=`date "+%s"`
    if (( "$LAST" + 10 < "$NOW" )); then
      break
    fi
    echo $(("$LAST" - "$NOW" + 10))
    sleep 1
  done

  rm -r $MYCAR/
  mkdir $MYCAR
  mkdir $MYCAR/data

  sudo pigpiod

  vcgencmd measure_clock arm
  vcgencmd measure_temp

  if [ $MYCONFIG != "" ]; then
    MYCONFIG="--myconfig "$MYCONFIG
  fi

  if [ $1 = "0" ] || [ $1 = "d" ]; then
    python manage.py drive $MYCONFIG --js
  else
    if [ "$2" = "" ]; then
      if [ $MODEL_FILE != "" ]; then
        MODEL_FILE="--model "$MODEL_FILE
      else
        MODEL_FILE="--model ./models/mypilot-aug.h5"
      fi
    else
      MODEL_FILE="--model "$2
    fi
    if [ $MODEL_TYPE != "" ]; then
      MODEL_TYPE="--type "$MODEL_TYPE
    fi
    python manage.py drive $MYCONFIG $MODEL_FILE $MODEL_TYPE --js
  fi
  sudo killall -9 pigpiod
  sudo rm -rf /var/run/pigpio.pid

  vcgencmd measure_clock arm
  vcgencmd measure_temp

  date "+%s" > /dev/shm/date.txt
fi

if [ $1 = "0" ] || [ $1 = "d" ] || [ $1 = "a" ] || [ $1 = "z" ]; then
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
    cp $MYCAR/data/log.csv $LOGS/log_${ymdhm}_drive.csv
  else
    sudo zip -rq $LOGS/log_${ymdhm}_auto.zip mycar
    sudo chown pi:pi $LOGS/log_${ymdhm}_auto.zip
    cp $MYCAR/data/log.csv $LOGS/log_${ymdhm}_auto.csv
  fi
  popd

  read -p "Hit enter: rsync log.csv"
  rsync -rtv --delete $MYCAR/data/log.csv work@$hostname.local:/Volumes/$ramdisk/
fi

if [ $1 = "0" ] || [ $1 = "d" ] || [ $1 = "a" ] || [ $1 = "z" ] || [ $1 = "m" ]; then
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

if [ $1 = "0" ] || [ $1 = "d" ] || [ $1 = "a" ] || [ $1 = "z" ] || [ $1 = "m" ] || [ $1 = "up" ]; then
  read -p "Hit enter: updown"
  echo -n "input path: "
  read str
  time rsync -rtz --compress-level=9 $MYCAR $TRAIN_URL:/run/shm/$str/
fi

if [ $1 = "0" ] || [ $1 = "d" ] || [ $1 = "a" ] || [ $1 = "z" ] || [ $1 = "m" ] || [ $1 = "up" ] || [ $1 = "down" ]; then
  echo $str
  read -p "Hit enter: get model file"
  if [ $1 = "down" ]; then
    echo -n "input path: "
    read str
  fi
  time rsync -rtz --compress-level=9 $TRAIN_URL:/run/shm/$str/mycar/models ./
  cp ./models/mypilot-aug.h5 ./models/mypilot-aug_${ymdhm}.h5
  cp ./models/mypilot-aug.tflite ./models/mypilot-aug_${ymdhm}.tflite
fi

if [ $1 = "s" ]; then
  read -p "Hit enter: makemovie salient"
  echo -n "input start: "
  read START
  echo -n "input end: "
  read END
  time donkey makemovie --type linear --tub $TUB/ --out $LOGS/log_${ymdhm}_salient.mp4 --scale 1 --salient --model ./models/mypilot-aug.h5 --start $START --end $END
  read -p "Hit enter: rsync salient"
  rsync -rtv $LOGS/log_${ymdhm}_salient.mp4 work@$hostname.local:/Volumes/$ramdisk/
fi

rm $DOUBLE

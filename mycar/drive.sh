#!/bin/bash

DOUBLE="/dev/shm/doublestart.txt"

if [ "$1" = "0" ]; then
  FILE="/dev/shm/autostart.txt"
  if [ ! -e $FILE ]; then
    echo -n > $FILE
    exit
  fi
else
  if [ "$1" = "d" ] || [ "$1" = "a" ] || [ "$1" = "z" ] || [ "$1" = "m" ] || [ "$1" = "up" ] || [ "$1" = "down" ] || [ "$1" = "s" ]; then
    rm $DOUBLE
  fi
fi

if [ -e $DOUBLE ]; then
  exit
fi
echo -n > $DOUBLE

MYCAR=/dev/shm/mycar
TUB=$MYCAR/data/tub*
LOGS=~/projects/my_donkeycar-v3/mycar/logs

ymdhm=`date "+%Y%m%d%H%M"`

RSYNC_OPT="-rv --progress --partial"

if [ "$1" = "0" ] || [ "$1" = "d" ] || [ "$1" = "a" ]; then

  rm -r $MYCAR/
  mkdir $MYCAR
  mkdir $MYCAR/data

  vcgencmd measure_clock arm
  vcgencmd measure_temp

  if [ ! -e "/dev/rfcomm0" ]; then
    sudo rfcomm --raw connect 0 $RFCOMM_MAC 1 &
  fi

  if [ "$1" = "0" ] || [ "$1" = "d" ]; then
    python manage.py drive --js
  else
    if [ "$2" = "" ]; then
      if [ $MODEL_FILE != "" ]; then
        MODEL_FILE="--model "$MODEL_FILE
      else
        #MODEL_FILE="--model ./models/mypilot.h5"
        MODEL_FILE="--model ./models/mypilot.tflite"
      fi
    else
      MODEL_FILE="--model "$2
    fi
    if [ $MODEL_TYPE != "" ]; then
      MODEL_TYPE="--type "$MODEL_TYPE
    fi
    python manage.py drive $MODEL_FILE $MODEL_TYPE --js
  fi

  vcgencmd measure_clock arm
  vcgencmd measure_temp

#  date "+%s" > /dev/shm/date.txt
fi

if [ "$1" = "0" ] || [ "$1" = "d" ] || [ "$1" = "a" ] || [ "$1" = "z" ]; then
  read -p "Hit enter: zip"

  cp config.py $MYCAR/
  cp myconfig.py $MYCAR/
  if [ "$1" = "a" ]; then
    cp -r ./models $MYCAR/
  fi

  pushd /dev/shm
  if [ "$1" == "d" ]; then
    zip -rq $LOGS/log_${ymdhm}_drive.zip mycar
    cp $MYCAR/data/log.csv $LOGS/log_${ymdhm}_drive.csv
  elif [ "$1" == "a" ]; then
    zip -rq $LOGS/log_${ymdhm}_auto.zip mycar
    cp $MYCAR/data/log.csv $LOGS/log_${ymdhm}_auto.csv
  else
    zip -rq $LOGS/log_${ymdhm}_.zip mycar
    cp $MYCAR/data/log.csv $LOGS/log_${ymdhm}_.csv
  fi
  popd

  read -p "Hit enter: rsync log.csv"
  rsync $RSYNC_OPT --delete $MYCAR/data/log.csv $HOSTNAME:$RAMDISK
fi

if [ "$1" = "0" ] || [ "$1" = "d" ] || [ "$1" = "a" ] || [ "$1" = "z" ] || [ "$1" = "m" ]; then
  read -p "Hit enter: makemovie"
  if [ "$1" == "d" ]; then
    donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_drive.mp4 --scale 1
    read -p "Hit enter: rsync movie"
    rsync $RSYNC_OPT $LOGS/log_${ymdhm}_drive.mp4 $HOSTNAME:$RAMDISK
  elif [ "$1" == "a" ]; then
    donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_auto.mp4 --scale 1
    read -p "Hit enter: rsync movie"
    rsync $RSYNC_OPT $LOGS/log_${ymdhm}_auto.mp4 $HOSTNAME:$RAMDISK
  else
    donkey makemovie --tub $TUB/ --out $LOGS/log_${ymdhm}_.mp4 --scale 1
    read -p "Hit enter: rsync movie"
    rsync $RSYNC_OPT $LOGS/log_${ymdhm}_.mp4 $HOSTNAME:$RAMDISK
  fi
fi

if [ "$1" = "0" ] || [ "$1" = "d" ] || [ "$1" = "a" ] || [ "$1" = "z" ] || [ "$1" = "m" ] || [ "$1" = "up" ]; then
  read -p "Hit enter: up"
  echo -n "input path: "
  read str
  time rsync $RSYNC_OPT $MYCAR $TRAIN_URL:/dev/shm/$str/
fi

if [ "$1" = "0" ] || [ "$1" = "d" ] || [ "$1" = "a" ] || [ "$1" = "z" ] || [ "$1" = "m" ] || [ "$1" = "up" ] || [ "$1" = "down" ]; then
  echo $str
  read -p "Hit enter: down"
  if [ "$1" = "down" ]; then
    echo -n "input path: "
    read str
  fi
  time rsync $RSYNC_OPT $TRAIN_URL:/dev/shm/$str/mycar/models ./
  cp ./models/mypilot-aug.h5 ./models/mypilot-aug_${ymdhm}.h5
  cp ./models/mypilot-aug.tflite ./models/mypilot-aug_${ymdhm}.tflite
fi

if [ "$1" = "s" ]; then
  read -p "Hit enter: makemovie salient"
  echo -n "input start: "
  read START
  echo -n "input end: "
  read END
  time donkey makemovie --type linear --tub $TUB/ --out $LOGS/log_${ymdhm}_salient.mp4 --scale 1 --salient --model ./models/mypilot-aug.h5 --start $START --end $END
  read -p "Hit enter: rsync salient"
  rsync $RSYNC_OPT $LOGS/log_${ymdhm}_salient.mp4 $HOSTNAME:$RAMDISK
fi

rm $DOUBLE

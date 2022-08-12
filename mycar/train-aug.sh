#!/bin/bash

if [ "$2" = "" ]; then
  echo "no offset"
  exit
fi

#rm -r /run/shm/$1x
#cp -r /run/shm/$1 /run/shm/$1x
rm -r /run/shm/$1/mycar/data/tubx$2
mkdir /run/shm/$1/mycar/data/tubx$2
#cp /run/shm/$1/mycar/data/tub/*.json /run/shm/$1/mycar/data/tubx/
python ./host_tools/offset.py /run/shm/$1/mycar/data/tub $2

#FPS
echo -n "input FPS: (50/sec)"
read FPS
if [ "$FPS" = "" ]; then
  FPS="50"
  echo "FPS: " $FPS
fi

#最初をカットするフレーム数
echo -n "input start frame num: (250=5sec)"
read START
if [ "$START" = "" ]; then
  START="250"
  echo "START: " $START
fi

#最後のカットするフレーム数
echo -n "input end frame num: (150=3sec)"
read END
if [ "$END" = "" ]; then
  END="150"
  echo "END: " $END
fi

#python ./host_tools/jpg2jpgx-s.py $1x $START $END $FPS $2
python ./host_tools/jpg2jpgx.py $1 $START $END 1 $2

read -p "Hit enter or ctrl + c"

#低速の値
echo -n "input throttle low: (-0.1)"
read LOW
if [ "$LOW" = "" ]; then
  LOW="-0.1"
  echo "LOW: " $LOW
fi

#低速の前後 n 秒をカット
echo -n "input cut length (sec): (3sec)"
read SEC
if [ "$SEC" = "" ]; then
  SEC="3"
  echo "SEC: " $SEC
fi

python ./host_tools/record_check.py /run/shm/$1/mycar/data/tubx $2 $FPS $LOW $SEC $START

export TF_FORCE_GPU_ALLOW_GROWTH=true

while true; do

  rm -r /run/shm/$1/mycar/models
  mkdir /run/shm/$1/mycar/models

  #time python manage.py train --tub /run/shm/$1/data/ --model /run/shm/$1/models/mypilot.h5
  #time python manage.py train --tub /run/shm/$1/mycar/data/ --model /run/shm/$1/mycar/models/mypilot-aug.tflite --type coral_tflite_linear --aug
  #time python manage.py train --tub /run/shm/$1x/mycar/data/ --model /run/shm/$1/mycar/models/mypilot-aug.tflite --type coral_tflite_linear --aug
  #time python manage.py train --tub /run/shm/$1x/mycar/data/tub/ --model /run/shm/$1/mycar/models/mypilot-aug.tflite --type coral_tflite_linear --aug
  time python manage.py train --tub /run/shm/$1/mycar/data/tubx$2/ --model /run/shm/$1/mycar/models/mypilot-aug.tflite --type coral_tflite_linear --aug

  read -p "Hit enter or ctrl + c"

done

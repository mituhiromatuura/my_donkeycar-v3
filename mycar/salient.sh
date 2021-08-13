#!/bin/bash

time donkey makemovie --type linear --tub /dev/shm/mycar/data/tub/ --out /dev/shm/mycar/data/movie.mp4 --salient --model ./models/mypilot-aug.h5 --start $1 --end $2

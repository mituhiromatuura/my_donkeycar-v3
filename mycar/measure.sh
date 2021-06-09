#!/bin/bash

while true;do vcgencmd measure_clock arm;vcgencmd measure_temp;sleep 2;done

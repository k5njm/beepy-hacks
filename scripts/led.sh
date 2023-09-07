#!/bin/bash
# Beepy led control

syspath="/sys/firmware/beepy/"
led="led"
led_red="led_red"
led_green="led_green"
led_blue="led_blue"

led_control () {
  echo $1 > $syspath$led
  if [[ $# -gt 1 ]]; then
    echo $2 > $syspath$led_red
    echo $3 > $syspath$led_green
    echo $4 > $syspath$led_blue
  fi
}

set_value () {
  if [[ $value -gt 0 ]]; then
    value=$value
  else
    value=255
  fi
}

pulse_func () {
  led_control $1 $2 $3 $4
  case $pulse in
    3[1-9]) sleep 0.01;;
    2[1-9]) sleep 0.02;;
    [1-9]) sleep 0.03;;
  esac
}

if [[ $# -gt 0 ]]; then
  if [[ $2 -gt 0 ]] && [[ $2 -lt 256 ]]; then
    value=$2
  fi
  case $1 in
    "on")
      set_value
      led_control 1 $value $value $value
      ;;
    "red")
      set_value
      led_control 1 $value 0 0
      ;; 
    "pulse")
      while true; do
        for pulse in {0..39}; do pulse_func 1 $pulse $pulse $pulse; done
        for pulse in {39..0}; do pulse_func 1 $pulse $pulse $pulse; done
        sleep 1.5
      done
      ;;
    "random")
      while true; do
        set_value
        red=`shuf -i 0-$value -n 1`       
        green=`shuf -i 0-$value -n 1`
        blue=`shuf -i 0-$value -n 1`
        led_control 1 $red $green $blue
        sleep 0.5
      done
      ;;
    "off")
      led_control 0
      ;;
    *)
      echo "Usage: sudo ./led.sh [option] [brightness]"
      echo "Options: on, off, red, random, pulse"
      echo "Brightness: 0-255"
    ;;
  esac
fi

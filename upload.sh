#!/bin/sh

IP=""
BAUD=9600
DEV=/dev/ttyUSB0

[ -e ./local.sh ] && . ./local.sh

upload_script ()
{
    SCRIPT="$1"
    shift
    echo "Checking $SCRIPT"
    if [ ! -e "$SCRIPT" ]; then
        return
    fi
    
    if [ ! -e $TS ] || [ "$SCRIPT" -nt $TS ]; then
        echo "Running '$LUATOOL -f $SCRIPT $@'"
        $LUATOOL -f "$SCRIPT" $@
        [ $? -ne 0 ] && exit 1
    fi
}

OPT=""
if [ ! -z "$IP" ] && ping -q -c1 -W3 "$IP" > /dev/null; then
    MAC=`arp -n | grep "$IP" | awk '{ print $3 }'`
    if echo "$MAC" | grep -q '^ac:d0:74\|^5c:cf:7f\|^18:fe:34'; then
        echo "Found ESP8266 with MAC address $MAC at $IP"
        if nc -z $IP 23; then
            echo "Using telnet connection"
            OPT="--ip $IP"
        else
            echo "Telnet not running, falling back to serial"
        fi
    else
        echo "$IP is not an Espressif device"
    fi
else
    [ ! -z "$IP" ] && echo "$IP is down"
fi
LUATOOL="luatool.py -p $DEV -b $BAUD $OPT"

TS=.timestamp
#[ ! -e $TS ] && touch $TS

upload_script local.lua -c
upload_script mpd.lua -c
upload_script remote.lua -c
upload_script network.lua -c
upload_script init.lua

touch $TS

echo "Restarting"
$LUATOOL -n

screen $DEV $BAUD
if [ $? -eq 0 ]; then
    exit 0
fi

for i in seq 5; do
    if nc -z $IP 23; then
        telnet $IP
        break
    fi
done

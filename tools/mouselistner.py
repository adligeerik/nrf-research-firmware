#https://thehackerdiary.wordpress.com/2017/04/21/exploring-devinput-1/
import struct

with open('/dev/input/mice', 'rb') as f:
    while 1:
        data = f.read(3)
        print(struct.unpack('3b', data))

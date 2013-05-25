
from time import sleep
import serial
import io

ser = serial.Serial('/dev/tty.rainduino-DevB', 9600, timeout=5, bytesize=8, parity='N', stopbits=1);
buf = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1))
print "Ready to read"
print ser.isOpen()

while True:
    try:
        print buf.readline()
    except serial.SerialException:
        try:
            ser.close()
            sleep(0.5)
            ser.open()
        except serial.SerialException:
            pass

    sleep(1)


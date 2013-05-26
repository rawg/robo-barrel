

from time import sleep
import serial
import io
import configuration
import dao

config = configuration.read()

conn = serial.Serial(config['serial']['device'], config['serial']['baud'], timeout=5, bytesize=config['serial']['bytesize'], parity=config['serial']['parity'], stopbits=config['serial']['stopbits'])

buf = io.TextIOWrapper(io.BufferedRWPair(conn, conn, 1))

while True:
    try:
        line = buf.readline()

        if line.startswith('='):
            values = line[1:].split(':')
            session_id = values.pop(0)
            millis = values.pop(0)

            for sensor_id, value in enumerate(values):
                reading = dao.Reading()
                reading.session_id = session_id
                reading.millis = millis
                reading.value = value
                reading.sensor_id = sensor_id + 1
                reading.save()
            
    except serial.SerialException:
        try:
            ser.close()
            sleep(0.5)
            ser.open()
        except serial.SerialException:
            pass

    sleep(1)


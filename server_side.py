import socket
from gpiozero import Motor
import psutil
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация моторов
motor_left = Motor(forward=25, backward=8)
motor_right = Motor(forward=7, backward=12)

# Настройка сокета
HOST = '192.168.8.112'  # IP-адрес Raspberry Pi
PORT = 65432

def get_cpu_temperature():
    temps = psutil.sensors_temperatures()
    if 'cpu_thermal' in temps:
        return temps['cpu_thermal'][0].current
    else:
        logging.warning("No temperature sensors found")
        return None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    logging.info(f"Server started on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            logging.info(f"Connected by {addr}")
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                logging.debug(f"Received command: {data}")

                if data == "forward":
                    motor_left.forward()
                    motor_right.forward()
                elif data == "backward":
                    motor_left.backward()
                    motor_right.backward()
                elif data == "left":
                    motor_left.backward()
                    motor_right.forward()
                elif data == "right":
                    motor_left.forward()
                    motor_right.backward()
                elif data == "stop":
                    motor_left.stop()
                    motor_right.stop()
                elif data == "get_temp":
                    temp = get_cpu_temperature()
                    if temp is not None:
                        response = json.dumps({"command": "temp", "value": temp})
                    else:
                        response = json.dumps({"command": "temp", "value": "Unknown"})
                    logging.debug(f"Sending response: {response}")
                    conn.sendall(response.encode('utf-8'))
                else:
                    logging.warning(f"Unknown command: {data}")



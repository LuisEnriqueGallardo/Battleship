import socket

def obtener_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

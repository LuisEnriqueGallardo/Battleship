import socket
import threading
import random
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

class QJugador(QWidget):
    """
    Administra los datos del cliente y el proceso de recepción y envío de datos desde y hacía el servidor.
    """
    conexion_no_exitosa = pyqtSignal()
    conexion_exitosa = pyqtSignal()
    servidor_caido = pyqtSignal()
    mensaje_recibido = pyqtSignal(str)

    habilidades = ['Acorazar','Ataque aereo', 'Bombardero', 'Cañon doble', 'Hackeo terminal', 'Llamado a refuerzos', 'Radar satelital', 'Reconocimiento aereo', 'Reposicionamiento']
    listaDeBarcos = ['Crucero de Asalto "Vanguardia"', 'Portaaviones "Tempestad"', 'Acorazado "Centurión']
    
    def __init__(self, parent=None, nombre = '', tablero = QWidget, ip_servidor = '', puerto = 0):
        super().__init__(parent)
        self.nombre = nombre
        self.habilidades = []
        self.barcos = []
        self.tablero = tablero

        self.nombre = nombre
        self.ip_servidor = ip_servidor
        self.puerto = puerto

        # Declaración de atributos que se utilizan posteriormente:
        self.conn = None
        self.flag_cancelar = None

    def conectar(self):
        """
        Gestiona la conexión con el servidor.
        """
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.ip_servidor, self.puerto))
        except ConnectionRefusedError:
            self.conexion_no_exitosa.emit()
            return

        self.enviar(self.nombre)
        bienvenida = self.recibir()
        print(bienvenida)
        self.iniciar_recepcion_continua()
        self.conexion_exitosa.emit()

    def enviar(self, mensaje):
        """
        Envía el mensaje al servidor.
        Args:
            mensaje: Texto del mensaje.
        """
        self.conn.send(mensaje.encode())

    def recibir(self):
        """
        Recibe un mensaje del servidor.
        Returns:
            Texto del mensaje.
        """
        try:
            mensaje = self.conn.recv(2048)
            self.mensaje_recibido.emit(mensaje.decode())
        except ConnectionResetError as e:
            raise RuntimeError("El servidor se desconectó")

    def iniciar_recepcion_continua(self):
        self.flag_cancelar = False
        self.hilo_lectura_continua = QThread()
        self.moveToThread(self.hilo_lectura_continua)
        self.hilo_lectura_continua.started.connect(self.recibir_continuamente)

        # Señal utilizada para gestionar la correcta terminación del hilo con quit:
        self.finished.connect(self.hilo_lectura_continua.quit)

        self.hilo_lectura_continua.start()

    def recibir_continuamente(self):
        while not self.flag_cancelar:
            try:
                mensaje = self.recibir()
                print(mensaje)
            except RuntimeError:
                self.flag_cancelar = True
                self.servidor_caido.emit()

    def asignarAtributos(self):
        self.habilidades = [random.choice(self.habilidades) for _ in range(3)]
        self.barcos = [random.choice(self.listaDeBarcos) for _ in range(7)]
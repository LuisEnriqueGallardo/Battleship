import socket
import threading
import random

from funciones import obtener_ip
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
        # self.finished.connect(self.hilo_lectura_continua.quit)

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

class Servidor():
    """
    Administra los datos del servidor y gestiona las conexiones y el envío de mensajes entre clientes.
    """
    def __init__(self, ip, puerto):
        self.ip = ip
        self.puerto = puerto

        # Señales a usar
        self.senalinicioExitoso = pyqtSignal()
        self.senalconexionNoExitosa = pyqtSignal()
        self.senalMensajeRecibido = pyqtSignal(str)
        self.clienteConectado = pyqtSignal()

        # Declaración de atributos que se utilizan posteriormente:
        self.server = None
        self.flag_desconectar = None
        self.hilo_aceptar_clientes = None
        self.lista_clientes = []
        self.nombre = None

    def iniciar(self, max_clientes=3):
        """
        Configura el servidor y gestiona el inicio de aceptación de clientes.
        Args:
            max_clientes: Máximo número de clientes (conexiones) permitidas.
        """
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.puerto))
        self.server.listen(max_clientes)
        self.senalinicioExitoso.emit()
        print(f"Servidor iniciado en {self.ip}:{self.puerto}")

        self.flag_desconectar = False
        self.hilo_aceptar_clientes = threading.Thread(target=self.aceptar_clientes, daemon=True)
        self.hilo_aceptar_clientes.start()

    def aceptar_clientes(self):
        """
        Implementa el proceso de aceptación de clientes dentro de un ciclo "infinito". Esta función debe ejecutarse en un
        hilo de ejecución independiente debido a que "accept()" es un método bloqueante.
        """
        while not self.flag_desconectar:
            conn, addr = self.server.accept()
            cliente = QJugador(conn, cliente.nombre, cliente.tablero, cliente.ip_servidor, cliente.puerto)
            self.lista_clientes.append(cliente)

            cliente.enviar(f"Bienvenido(a) {cliente.nombre}, contigo hay {len(self.lista_clientes)} clientes conectados.")
            self.procesar_mensaje(f"{cliente.nombre} se ha conectado.", cliente, esAvisoServidor=True)
            self.clienteConectado.emit()
            cliente.recibir_continuamente()

    def procesar_mensaje(self, mensaje, cliente, esAvisoServidor=False):
        """
        Utilizado por los objetos cliente para avisar al servidor cuando se recibe un mensaje. El servidor emite el
        mensaje a todos los clientes salvo al cliente que lo envió originalmente.
        Args:
            mensaje: Contenido del mensaje.
            cliente: Cliente que lo envió
        """
        if esAvisoServidor:
            mensaje = f"Servidor: {mensaje}"
        else:
            mensaje = f"{cliente.nombre}: {mensaje}"

        print(mensaje)
        for c in self.lista_clientes:
            if c != cliente:
                c.recibir(mensaje)

    def avisar_desconexion(self, cliente):
        """
        Gestiona la desconexión de un cliente.
        Args:
            cliente: Cliente desconectado
        """
        self.lista_clientes.remove(cliente)
        self.procesar_mensaje(f"{cliente.nombre} se ha desconectado", cliente, esAvisoServidor=True)


# Punto de inicio de ejecución del programa:
ip = obtener_ip()
# puerto = int(input("Puerto: "))

servidor = Servidor(ip, 3333)

# Se crea un ciclo infinito para que el hilo principal no finalice y continúen en ejecución el hilo de aceptación de
# clientes y los hilos de escucha de cada cliente conectado.
# NOTA: Esto no es necesario si los hilos se crean con daemon=False, sin embargo, podemos tener un comportamiento
# no deseado si finaliza el hilo principal y quedan otros hilos todavía en ejecución.
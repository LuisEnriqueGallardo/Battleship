import socket
import threading

from funciones import obtener_ip
from PyQt5.QtCore import pyqtSignal

class Cliente:
    """
    Administra los datos del cliente y el proceso de recepción y envío de datos desde y hacía él.
    """

    def __init__(self, conn, servidor):
        self.conn = conn
        self.servidor = servidor

        # Declaración de atributos que se utilizan posteriormente:
        self.flag_cancelar = None
        self.hilo_lectura_continua = None

    def escribir(self, mensaje):
        """
        Envía el mensaje al cliente.
        Args:
            mensaje: Texto del mensaje.
        """
        self.conn.send(mensaje.encode())

    def leer(self):
        """
        Recibe un mensaje del cliente.
        Returns:
            Texto del mensaje.
        """
        try:
            mensaje = self.conn.recv(2048)
            return mensaje.decode()
        except ConnectionResetError:
            raise RuntimeError("El cliente se desconectó")

    def leer_continuamente(self):
        """
        Implementa el proceso de lectura continua dentro de un ciclo "infinito". Esta función debe ejecutarse en un
        hilo de ejecución independiente debido a que "recv()" es un método bloqueante.
        """
        while not self.flag_cancelar:
            try:
                mensaje = self.leer()

                # Avisar al objeto servidor para que emita el mensaje al resto de los clientes:
                self.servidor.procesar_mensaje(mensaje, self)
            except RuntimeError:
                self.servidor.avisar_desconexion(self)
                self.flag_cancelar = True

    def iniciar_lectura_continua(self):
        """
        Gestiona la creación e inicio del hilo para la lectura continua de datos desde el cliente.
        """
        self.flag_cancelar = False
        self.hilo_lectura_continua = threading.Thread(target=self.leer_continuamente, daemon=True)
        self.hilo_lectura_continua.start()


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

    def iniciar(self, max_clientes=100):
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
            cliente = Cliente(conn, self)
            self.lista_clientes.append(cliente)

            cliente.nombre = cliente.leer()
            #print(f"Servidor: {cliente.nombre} se ha conectado")
            cliente.escribir(f"Bienvenido(a) {cliente.nombre}, contigo hay {len(self.lista_clientes)} clientes conectados.")
            self.procesar_mensaje(f"{cliente.nombre} se ha conectado.", cliente, esAvisoServidor=True)
            self.clienteConectado.emit()
            cliente.iniciar_lectura_continua()

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
                c.escribir(mensaje)

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
while True:
    pass
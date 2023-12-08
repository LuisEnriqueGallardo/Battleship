import json
import socket
import threading
import time
from Modulos import obtener_ip
from PyQt5.QtCore import pyqtSignal, QObject

class QJugador(QObject):
    """
    Administra los datos del cliente y el proceso de recepción y envío de datos desde y hacía el servidor.
    """
    clienteRecibeMensaje = pyqtSignal(str)
    mensajeEnviado = pyqtSignal(str)
    conexionperdida = pyqtSignal(str)
    clienteDesconectado = pyqtSignal(str)
    conexionExitosa = pyqtSignal(str)
    finished = pyqtSignal()
    inicioJuego = pyqtSignal()
    
    def __init__(self, nombre, ip_servidor, puerto):
        super().__init__()
        self.nombre = nombre
        self.ip_servidor = ip_servidor
        self.puerto = puerto

        # Declaración de atributos que se utilizan posteriormente:
        self.jugadoresLista = []
        self.conn = None
        self.flag_cancelar = None

    def conectar(self):
        try:
            self.conexion = socket.socket()
            self.conexion.connect((self.ip_servidor, self.puerto))
            self.escribir(self.nombre)
            self.hilo_de_escucha = threading.Thread(target=self.leer_continuamente, daemon=True)
            self.hilo_de_escucha.start()
            self.conexionExitosa.emit("Conexión exitosa")
        except ConnectionRefusedError:
            raise RuntimeError("No se pudo conectar al servidor")


    def leer(self):
        try:
            mensaje = self.conexion.recv(2048).decode()
            if mensaje.startswith("[") and mensaje.endswith("]"):
                self.jugadoresLista = json.loads(mensaje)
            return mensaje
        except ConnectionResetError:
            raise RuntimeError("El cliente se desconectó")
        except json.JSONDecodeError:
            return mensaje
    
    def leer_continuamente(self):
        """
        Implementa el proceso de lectura continua dentro de un ciclo "infinito". Esta función debe ejecutarse en un
        hilo de ejecución independiente debido a que "recv()" es un método bloqueante.
        """
        while not self.flag_cancelar:
            try:
                mensaje = self.leer()
                self.clienteRecibeMensaje.emit(mensaje)
            except RuntimeError:
                self.flag_cancelar = True
            except ConnectionAbortedError:
                self.flag_cancelar = True
                self.clienteDesconectado.emit('Desconectado')
            except ConnectionResetError:
                self.flag_cancelar = True
                self.conexionperdida.emit('Conexión perdida')
            except OSError:
                self.flag_cancelar = True
                self.conexionperdida.emit('Error de conexión')
    
    def escribir(self, mensaje):
        if mensaje != '' and mensaje != None:
            try:
                self.conexion.send(mensaje.encode())
                self.mensajeEnviado.emit(f"{self.nombre}: {mensaje}")            
            except ConnectionResetError:
                return print("Error de conexión")

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
            mensajenuevo = mensaje.decode()
            if isinstance(mensajenuevo, list):
                return json.loads(mensajenuevo)
            return mensajenuevo
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
        
    def to_dict(self):
        return {
            'nombre': self.nombre,
        }


class Servidor(QObject):
    servidorIniciado = pyqtSignal(str)
    mensajeServidor = pyqtSignal(str)
    jugadorConectado = pyqtSignal(str)
    jugadorCaido = pyqtSignal(str)
    listaDeJugadores = pyqtSignal(list)

    def __init__(self, ip, puerto):
        super().__init__()
        self.ip = ip
        self.puerto = puerto
        self.server = None
        self.flag_aceptar_clientes = None
        self.lista_clientes = []

    def iniciar(self, max_clientes=3):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.puerto))
        self.server.listen(max_clientes)
        self.servidorIniciado.emit(f"Servidor iniciado en {self.ip}:{self.puerto}")
        self.flag_desconectar = False
        self.hilo_aceptar_clientes = threading.Thread(target=self.aceptar_clientes, daemon=True)
        self.hilo_aceptar_clientes.start()

    def aceptar_clientes(self):
        while not self.flag_aceptar_clientes:
            try:
                conn, addr = self.server.accept()
                cliente = Cliente(conn, self)
                cliente.nombre = cliente.leer()

                self.lista_clientes.append(cliente)
                self.procesar_mensaje(f"{cliente.nombre} Conectado.", cliente, esAvisoServidor=True)
                self.jugadorConectado.emit(cliente.nombre)
                cliente.iniciar_lectura_continua()
            except OSError:
                self.flag_aceptar_clientes = True

    def procesar_mensaje(self, mensaje, cliente, esAvisoServidor=False):
        if esAvisoServidor:
            mensaje = f"Servidor: {mensaje}"
            self.mensajeServidor.emit(mensaje)
        else:
            if mensaje.startswith("//"):
                # Aquí puedes implementar la lógica para procesar comandos
                comando = mensaje[2:]
                self.procesar_comando(comando, cliente)
            else:
                mensaje = f"{cliente.nombre}: {mensaje}"
                self.mensajeServidor.emit(mensaje)

            for c in self.lista_clientes:
                if c != cliente:
                    c.escribir(mensaje)

    def procesar_comando(self, comando, cliente):
        if comando == "desconectar":
            self.avisar_desconexion(cliente)
        elif comando == "iniciarJuego":
            self.iniciarJuego()


    def avisar_desconexion(self, cliente):
        self.lista_clientes.remove(cliente)
        self.procesar_mensaje(f"{cliente.nombre} se ha desconectado", cliente, esAvisoServidor=True)
        self.jugadorCaido.emit(cliente.nombre)

    def iniciarJuego(self):
        """
        Inicia el juego y avisa a todos los clientes.
        """
        lista_nombres = [c.nombre for c in self.lista_clientes]
        mensaje = f"//iniciarJuego {json.dumps(lista_nombres)}"
        self.mensajeServidor.emit("El juego ha comenzado.")
        for c in self.lista_clientes:
            c.escribir(mensaje)
            c.escribir("//iniciarJuego")
            
            
ip = obtener_ip()

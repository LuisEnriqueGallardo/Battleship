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
        self.tablero = None

        # Declaración de atributos que se utilizan posteriormente:
        self.jugadoresLista = []
        self.conn = None
        self.flag_cancelar = None
        self.estadoDelTablero = []
        self.turno = False

    def conectar(self):
        """Gestiona la conexión del cliente con el servidor.

        Raises:
            RuntimeError: Si no se puede conectar con el servidor.
        """
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
        """Recibe un mensaje del servidor.

        Raises:
            RuntimeError: Si el cliente se desconecta.

        Returns:
            str: Texto del mensaje.
        """
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
        """Envía el mensaje al servidor.

        Args:
            mensaje (str): Texto del mensaje.

        Returns:
            error: Retorna un error de conexión si no se puede enviar el mensaje el cual va a la consola.
        """
        if mensaje != '' and mensaje != None:
            try:
                self.conexion.send(mensaje.encode())
                self.mensajeEnviado.emit(f"{self.nombre}: {mensaje}")            
            except ConnectionResetError:
                return print("Error de conexión")
        
    def enviar_tablero(self):
        """Envía el tablero al servidor. Para que el servidor lo envíe a los demás jugadores.
        """
        for renglon in range(10):
            for columna in range(10):
                contenido = self.tablero[renglon][columna]
                if contenido.disparado == True:
                    self.estadoDelTablero.append(contenido.row, contenido.column)

        mensaje = f"//actualizarTablero {self.nombre} {json.dumps(self.tablero)}"
        self.escribir(mensaje)

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
        """Inicia el servidor en la dirección IP y puerto especificados. para luego aceptar clientes.

        Args:
            max_clientes (int, optional): Valor de clientes a aceptar. Defaults to 3.
        """
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.puerto))
        self.server.listen(max_clientes)
        self.servidorIniciado.emit(f"Servidor iniciado en {self.ip}:{self.puerto}")
        self.flag_desconectar = False
        self.hilo_aceptar_clientes = threading.Thread(target=self.aceptar_clientes, daemon=True)
        self.hilo_aceptar_clientes.start()

    def aceptar_clientes(self):
        """Hilo de ejecución que acepta clientes y los agrega a la lista de clientes conectados.
        """
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
        """Procesa el mensaje recibido desde el cliente y lo envía a todos los clientes conectados. adenñas de validar si es un comando.

        Args:
            mensaje (str): Texto del mensaje.
            cliente (Cliente): Objeto cliente que envió el mensaje.
            esAvisoServidor (bool, optional): Defaults to False.
        """
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
        """Procesa un comando recibido desde el cliente y ejecuta la acción correspondiente.

        Args:
            comando (JSON): Texto del comando.
            cliente (Cliente): Objeto cliente que envió el comando.
        """
        if comando == "desconectar":
            self.avisar_desconexion(cliente)
        elif comando == "iniciarJuego":
            self.iniciarJuego()
        elif comando == "actualizarTablero":
            try:
                # tablero_json = comando.split(" ", 1)[1]
                # tablero = json.loads(tablero_json)
                self.actualizarTableros(comando)
            except Exception as e:
                print(f"Error al actualizar el tablero: {e}")


    def avisar_desconexion(self, cliente):
        """Avisa a todos los clientes que un cliente se ha desconectado y lo elimina de la lista de clientes conectados.

        Args:
            cliente (Cliente): Objeto cliente que se ha desconectado.
        """
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
            
    def actualizarTableros(self, tablero):
        """
        Actualiza el tablero de todos los clientes.
        """
        # Aqui, Tablero debe contener una lista con 2 valores: El primer valor es el nombre del jugador, El segundo valor es el tablero
        mensaje = f"//actualizarTablero {json.dumps(tablero)}"
        for c in self.lista_clientes:
            c.escribir(mensaje)

ip = obtener_ip()

import json
import random
import socket
import threading
import time

import requests
from Modulos import obtener_ip
from PyQt5.QtCore import pyqtSignal, QObject
from ColoresConsola import Colores
from datetime import datetime

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
                return print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}{Colores.RESET}: Error de conexión")

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
        self.juegoIniciado = False
        self.jugadoreslistos = 0

    def iniciar(self, max_clientes=3):
        """Inicia el servidor en la dirección IP y puerto especificados. para luego aceptar clientes.

        Args:
            max_clientes (int, optional): Valor de clientes a aceptar. Defaults to 3.
        """
        try:
            self.server = socket.socket()
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.ip, self.puerto))
            self.server.listen(max_clientes)
            self.servidorIniciado.emit(f"Servidor iniciado en {self.ip}:{self.puerto}")
            self.flag_desconectar = False
            self.hilo_aceptar_clientes = threading.Thread(target=self.aceptar_clientes, daemon=True)
            self.hilo_aceptar_clientes.start()
        except OSError:
            raise RuntimeError("No se pudo iniciar el servidor")

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
        """Procesa el mensaje recibido desde el cliente y lo envía a todos los clientes conectados. Además de validar si es un comando.

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
                if ";" in mensaje:
                    comandos = mensaje.split(";")
                    print(f"{Colores.NARANJA}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Mensaje recibido: {comandos}")
                    for c in comandos:
                        c = c[2:]
                        if c.strip() != "":
                            print(f"{Colores.BLANCO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Procesando comando: {c}.")
                            self.procesar_comando(c, cliente)
                    return
                comando = mensaje[2:]
                self.procesar_comando(comando, cliente)
            else:
                mensaje = f"{cliente.nombre}: {mensaje}"
                self.mensajeServidor.emit(mensaje)

            for c in self.lista_clientes:
                if c != cliente:
                    c.escribir(mensaje)

    def procesar_comando(self, mensaje, cliente):
        """Procesa un comando recibido desde el cliente y ejecuta la acción correspondiente.

        Args:
            comando (JSON): Texto del comando.
            cliente (Cliente): Objeto cliente que envió el comando.
        """
        try:
            if not self.juegoIniciado:
                self.jugador_actual = self.lista_clientes[0]
            # Extrae el comando y los datos del mensaje
            try:
                comando, datos = mensaje.split(" ", 1)
                print(f'{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime("%H:%M:%S")}{Colores.RESET}: Comando procesado: {comando} {datos}')
            except ValueError:
                comando = mensaje
                datos = ""
                print(f'{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime("%H:%M:%S")}{Colores.RESET}: No se pudo procesar el comando: {comando} {datos}')
                
            if comando.startswith("eleccionFinalizada"):
                self.eleccionFinalizada()
                for c in self.lista_clientes:
                    if c != cliente:
                        print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: {c.nombre} ha terminado su elección. Enviando aviso a {c.nombre}")
                        c.escribir(f"{datos} ha terminado su elección.")
                        
            if comando.startswith("finDelJuego"):
                for c in self.lista_clientes:
                    if c != cliente:
                        c.escribir(f"{datos} ha perdido.")
                        try:
                            self.lista_clientes.remove(cliente)
                        except ValueError:
                            pass
            
            if cliente.nombre == self.jugador_actual.nombre:
                if comando.startswith("iniciarJuego"):
                    if not self.juegoIniciado:
                        try:
                            # Si es el mensaje de inicio de juego, muestra el mensaje correcto
                            datos = datos.replace(";", '')
                            lista_nombres = json.loads(datos)
                            print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: El juego ha comenzado. Jugadores: {', '.join(lista_nombres)}")
                            for c in self.lista_clientes:
                                if c != cliente:
                                    c.escribir(f"//iniciarJuego {datos}")
                        except:
                            print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Error al cargar datos JSON en el juego")
                        
                elif comando.startswith("desconectar"):
                    # Si es un mensaje de desconexión, muestra el mensaje correcto
                    self.avisar_desconexion(cliente)
                    
                elif comando.startswith("actualizarTablero") or comando.startswith("//actualizarTablero"):
                    try:
                        if comando.startswith("//"):
                            comando = comando[2:]
                        datos = datos.replace(";", '')
                        nombreytablero = json.loads(datos)
                        self.actualizarTableros(nombreytablero)
                    except Exception as e:
                        print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Error al actualizar el tablero: {e}")
                        nombre = datos.split(" ", 1)[0]
                        datos = datos.split(" ", 1)[1]
                        self.actualizarTableros(nombre, datos)
                        
                elif comando.startswith("turno"):
                    if self.juegoIniciado:
                        print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Procesando turno....")
                        if cliente.nombre == self.jugador_actual.nombre:
                            self.cambiarTurno()
                else:
                    print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Comando desconocido: {comando}")
        except Exception as e:
            print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Error al procesar comando: {e}")
            return

    def avisar_desconexion(self, cliente):
        """Avisa a todos los clientes que un cliente se ha desconectado y lo elimina de la lista de clientes conectados.

        Args:
            cliente (Cliente): Objeto cliente que se ha desconectado.
        """
        self.lista_clientes.remove(cliente)
        self.procesar_mensaje(f"{cliente.nombre} se ha desconectado", cliente, esAvisoServidor=True)
        self.jugadorCaido.emit(cliente.nombre)
        self.evaluarJugadoresRestantes()
        print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: {cliente.nombre} se ha desconectado")
    
    def iniciarJuego(self):
        """
        Inicia el juego y avisa a todos los clientes.
        """
        for c in self.lista_clientes:
            c.escribir(f"//turno {self.jugador_actual.nombre}")
        self.juegoIniciado = True
        print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Enviando turno a los jugadores. Turno de {self.jugador_actual.nombre}")
            
    def actualizarTableros(self, nombre, tablero):
        """
        Actualiza el tablero de todos los clientes.
        """
        # Aqui, Tablero debe contener una lista con 2 valores: El primer valor es el nombre del jugador, El segundo valor es el tablero
        mensaje = f"//actualizarTablero {nombre} {tablero}"
        for c in self.lista_clientes:
            if c != self.jugador_actual:
                c.escribir(mensaje)
                print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Enviando tablero a {c.nombre}")
            
    def cambiarTurno(self):
        """
        Maneja los turnos de los jugadores.
        """
        turnoactual = self.lista_clientes.index(self.jugador_actual)
        turno = (turnoactual + 1) % len(self.lista_clientes)
        self.jugador_actual = self.lista_clientes[turno]
        
        for c in self.lista_clientes:
            c.escribir(f"//turno {self.jugador_actual.nombre}")

    def eleccionFinalizada(self):
        self.jugadoreslistos += 1
        if self.jugadoreslistos == len(self.lista_clientes):
            print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Todos los jugadores han terminado su elección. {self.jugadoreslistos,  len(self.lista_clientes)}")
            self.iniciarJuego()
            
    def evaluarJugadoresRestantes(self):
        """
        Evalua si quedan jugadores en la partida.
        """
        if len(self.lista_clientes) == 1:
            self.procesar_comando("finDelJuego", cliente=self.lista_clientes[0])
            self.procesar_mensaje("Juego finalizado por falta de jugadores", cliente=None, esAvisoServidor=True)
            self.lista_clientes.remove(self.lista_clientes[0])
            self.juegoIniciado = False
            self.jugadoreslistos = 0
            print(f"{Colores.ROJO}LOG SERVIDOR {datetime.now().strftime('%H:%M:%S')}{Colores.RESET}: Fin del juego")
            self.server.close()
            
ip = obtener_ip()

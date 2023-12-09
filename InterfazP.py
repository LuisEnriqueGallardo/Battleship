import json
import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QGridLayout, QScrollArea, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel, QStatusBar
from PyQt5.QtCore import Qt
from Modulos import QChat, QTableros, QNombreUsuario, QHabilidades, DialogoConexion, obtener_ip
from PyQt5.QtGui import QIcon
from JuegoServidor import Servidor, QJugador

class InterfazPrincipal(QMainWindow):
    """Interfaz Principal del juego donde se conectarán los modulos para iniciar el juego
    """
    servidor = Servidor(obtener_ip(), 3333)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship")
        self.setMinimumSize(1300, 800)
        self.widgetPrincipal = QWidget()
        self.setContentsMargins(10, 10, 10, 0)
        self.setStyleSheet('background-color: #FFFFE0; color: #B22222; font: Consolas;')
        self.setWindowIcon(QIcon('Icono.png'))
        
        # Señales del servidor
        self.servidor.servidorIniciado.connect(self.procesarMensaje)
        self.servidor.jugadorConectado.connect(self.jugadorEntrante)
        self.servidor.jugadorCaido.connect(self.eliminarJugador)

        # Barra de herramientas
        toolbar = self.addToolBar('Conexión')
        
        self.btnConectar = toolbar.addAction('Conectar', self.conectar)

        self.btnIniciarServidor = toolbar.addAction('Iniciar Servidor', self.iniciarServidor)

        self.btnCerrarServidor = toolbar.addAction('Cerrar servidor', self.cerrarServidor)
        self.btnCerrarServidor.setEnabled(False)

        self.btnIniciarJuego = toolbar.addAction('Iniciar Juego', self.iniciarJuego)
        self.btnIniciarJuego.setEnabled(False)
        
        # Estilos de los componentes
        self.setStyleSheet("""
                            QToolButton:enabled { background-color: #c0fcc5; }
                            QToolButton:disabled { background-color: #fcb1b4; }
                            QStatusBar { background: #FFFFE0; color: #B22222; font: Consolas; }
                            QMainWindow { background-color: #FFFFE0; color: #B22222; font: Consolas; }
                        """)

        # Lista para mantener los componentes del juego
        self.widgets = []
        self.jugadoresLista = [] #Lista de jugadores

        # Dialogo para ingresar el nombre de usuario
        self.nombreUsuario = QNombreUsuario().abrirDialogo() #Nombre de usuario

        self.contenedorPrincipal = QGridLayout(self.widgetPrincipal)

        # Contenedor donde se generan los cuadros enemigos
        contenedorEnemigos = QFrame()
        self.scrollEnemigos = QScrollArea(contenedorEnemigos)
        self.scrollEnemigos.setStyleSheet('background: SandyBrown;')
        self.scrollEnemigos.setWidgetResizable(True)
        self.scrollEnemigos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollEnemigos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.contenedorEnemigosH = QWidget()
        layoutEnemigos = QHBoxLayout(self.contenedorEnemigosH)
        self.scrollEnemigos.setWidget(self.contenedorEnemigosH)

        # Modulo del chat
        self.chat = QChat(None, self.nombreUsuario)
        self.chat.setEnabled(False)
        self.chat.setFixedSize(300, 300)

        # Tablero con las habilidades del jugador
        self.zonaHabilidades = QHabilidades()
        self.zonaHabilidades.senalDeHabilidad.connect(self.usoDeHabilidades)

        # Variables para operaciones futuras
        self.diccionarioDeJugadores = {}
        self.ventana_tablero_abierta = None

        # Creación de los nombres de los jugadores en el contenedor
        self.contenedorJugadores = QVBoxLayout()

        # Barra de estado para mostrar mensajes
        self.barraEstado = QStatusBar()
        self.barraEstado.showMessage(f'¡Bienvenido {self.nombreUsuario}!')

        self.guardarJugadores()
        self.crearEtiquetasDeJugadores()
        
        self.juegoIniciado = False
        

        #Componentes de los tableros e importación a la interfaz
        self.contenedorPrincipal.addLayout(self.contenedorJugadores, 0, 0)
        self.contenedorPrincipal.addWidget(self.chat, 1, 0)
        self.contenedorPrincipal.addWidget(self.scrollEnemigos, 0, 1)
        self.contenedorPrincipal.addWidget(self.zonaHabilidades, 0, 2, 2, 1, Qt.AlignCenter)
        self.contenedorPrincipal.addWidget(self.barraEstado, 2, 0, 1, 2)
        self.setCentralWidget(self.widgetPrincipal)

    def guardarJugadores(self):
        """Inicializa la lista vacía para que al iniciar el juego. Se construye la misma
        con los jugadores que se conecten al servidor.
        """
        # Creación de los jugadores en un diccionario
        for player in self.jugadoresLista:
            jugadoraIngresar = QJugador(player, None, None)
            self.diccionarioDeJugadores[player] = jugadoraIngresar
            
    def eliminarJugador(self, jugador):
        """Administra la eliminación de un jugador de la lista de jugadores y del diccionario de jugadores cuando
        el jugador es eliminado o se desconecta del servidor.

        Args:
            jugador (str): string con el nombre del jugador a eliminar
        """
        self.jugadoresLista.remove(jugador)
        self.diccionarioDeJugadores.pop(jugador)
        self.crearEtiquetasDeJugadores()        
            
    def eliminar_widgets(self, layout):
        """Funcion para eliminar widgets de un contenedor o layout. En este caso para eliminar las etiquetas y vaciar el contenedor
        para ser reconstruido al iniciar el juego y evitar acumulacion de etiquetas.

        Args:
            layout (layout): Recibe como argumento un layout o contenedor de widgets
        """
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()

    def crearEtiquetasDeJugadores(self):
        """Función para generar las etiquetas con los nombres de los jugadores. Se crea una etiqueta con diferente color por
        estetica en cada jugador. Además genera un background diferente para el jugador propio.
        """
        
        self.eliminar_widgets(self.contenedorJugadores)
        coloresNombres =  ["#1a1a1a", "#333333", "#4c4c4c", "#666666", "#808080", "#999999", "#b3b3b3", "#cccccc", "#666699", "#996666", "#666633", "#669966", "#6666cc", "#993366", "#cc6666"]
        for nombre in self.jugadoresLista:
            nuevoJugador = QLabel(nombre)
            nuevoJugador.setStyleSheet('font-size: 20px')
            nuevoJugador.setStyleSheet(f'font: Consolas; font-size: 40px; color: {random.choice(coloresNombres)};')
            if nombre == self.nombreUsuario:
                nuevoJugador.setStyleSheet(f'background-color: #feeabe; font: Consolas; font-size: 40px; color: {random.choice(coloresNombres)}')
            self.contenedorJugadores.addWidget(nuevoJugador)

    def jugadorEntrante(self, jugador):
        """Función para agregar un jugador a la lista de jugadores y al diccionario de jugadores cuando se conecta al servidor.

        Args:
            jugador (str): String con el nombre del jugador a agregar
        """
        self.jugadoresLista.append(jugador)
        self.diccionarioDeJugadores[jugador] = QJugador(jugador, None, None)
        self.crearEtiquetasDeJugadores()

    def actualizarTablerodeJugadores(self):
        """Función para actualizar los tableros de los jugadores enemigos y el propio. Se crea un tablero propio y se crean los tableros enemigos
        con el nombre de cada jugador en el contenedor de los mismos. Se crea una señal para mostrar el tablero en grande al hacer click en el nombre.
        """
        # Tablero propio del usuario
        self.tableroPropio = QTableros()
        self.tableroPropio.etNombre.setText(self.nombreUsuario)
        self.contenedorPrincipal.addWidget(self.tableroPropio, 1, 1, Qt.AlignCenter)
        
        # Creación de los tableros enemigos en el contenedor de los mismos
        try:
            for jugador in self.jugadoresLista:
                if self.nombreUsuario != self.diccionarioDeJugadores[jugador].nombre:
                    tableroEnemigo = QTableros(self.scrollEnemigos, False)
                    tableroEnemigo.etNombre.setText(self.diccionarioDeJugadores[jugador].nombre)
                    tableroEnemigo.etNombre.setToolTip(f'Click para ver el tablero de {tableroEnemigo.etNombre.text()}')
                    tableroEnemigo.etNombre.clicked.connect(lambda _, tablero=tableroEnemigo: self.mostrarTablero(tablero))
                    self.layout = self.contenedorEnemigosH.layout()
                    self.layout.insertWidget(0, tableroEnemigo)
        except Exception as e:
            self.procesarMensaje(f'No se pudo actualizar el tablero de {jugador}. {e}')

    def mostrarTablero(self, tablero):
        """Función para mostrar el tablero en grande al hacer click en el nombre del jugador enemigo.

        Args:
            tablero (QTablero): Tablero del jugador enemigo como objeto "QTablero"
        """
        if self.ventana_tablero_abierta is None:
            ventana_tablero = TableroEnGrande(self, tablero)
            self.ventana_tablero_abierta = ventana_tablero
            ventana_tablero.exec()

    def procesarMensaje(self, mensaje):
        """Función para procesar los mensajes recibidos por el servidor y el cliente. Se procesan los mensajes y realiza la comprobación en caso de ser un 
        comando iniciando por "//" y ejecuta la función correspondiente.

        Args:
            mensaje (str): Mensaje recibido por el servidor o el cliente
        """
        # Verificar si el mensaje es un comando especial
        mensaje = mensaje.strip()
        if mensaje.startswith('//'):
            comando = mensaje[2:]
            self.procesar_comando(comando)
        else:
            print(mensaje)
            self.chat.chat_texto.appendPlainText(mensaje)

    def procesar_comando(self, comando):
        """Función que procesa los comandos recibidos por el servidor. Para cada comando existe una función que se ejecuta al recibirlo.

        Args:
            comando (JSON): Comando recibido por el servidor, el cual llega como un JSON codificado en string.
        """
        if comando.startswith("iniciarJuego"):
            # Extraer la lista de jugadores del mensaje
            partes = comando.split(" ", 1)
            if len(partes) > 1:
                lista_json = partes[1]
                lista_nombres = json.loads(lista_json)
                self.jugadoresLista = lista_nombres
                self.guardarJugadores()
                self.iniciarJuego()
            else:
                print("Comando iniciarJuego sin lista de jugadores.")
        if comando.startswith("actualizarTablero"):
            try:
                tablero_json = comando.split(" ", 1)[1]
                nombreRemitente = comando.split(" ", 1)[0]
                tablero = json.loads(tablero_json)
                self.recibirTableros(nombreRemitente, tablero)
            except Exception as e:
                print(f"Error al actualizar el tablero: {e}")

    def conectar(self):
        """Función que gestiona toda la conexión al servidor. Se crea un cliente y se conecta al servidor. Se conectan las señales del cliente y se configura
        """
        self.dialogoConectar = DialogoConexion()
        self.dialogoConectar.exec()
        try:
            self.cliente = QJugador(self.nombreUsuario, self.dialogoConectar.ip, self.dialogoConectar.puerto)
            self.cliente.clienteRecibeMensaje.connect(self.procesarMensaje)
            self.cliente.conexionperdida.connect(self.procesarMensaje)
            self.cliente.clienteDesconectado.connect(self.procesarMensaje)
            self.cliente.conexionExitosa.connect(self.procesarMensaje)
            self.cliente.mensajeEnviado.connect(self.procesarMensaje)
            self.cliente.inicioJuego.connect(self.iniciarJuego)
            self.cliente.conectar()
            self.btnConectar.setEnabled(False)
            self.barraEstado.showMessage(f'Conectado al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto} como {self.nombreUsuario}')
            self.configuracionInterfazOnline()
            self.btnIniciarServidor.setEnabled(False)
        except Exception:
            self.barraEstado.showMessage(f'No se pudo conectar al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto}', 3000)
            self.barraEstado.showMessage(f'¡Bienvenido {self.nombreUsuario}!')
            
    def iniciarServidor(self):
        """Función para iniciar el servidor. El host se conecta como un cliente mas para facilitar la comunicación entre el servidor y el cliente.
        """
        self.btnConectar.setEnabled(False)
        self.btnIniciarServidor.setEnabled(False)
        self.servidor.mensajeServidor.connect(self.procesarMensaje)
        self.servidor.iniciar()
        self.cliente = QJugador(self.nombreUsuario, self.servidor.ip, self.servidor.puerto)
        self.cliente.inicioJuego.connect(self.servidor.iniciarJuego)
        self.cliente.conectar()
        self.btnIniciarJuego.setEnabled(True)
        self.configuracionInterfazOnline()
        
    def configuracionInterfazOnline(self):
        """Función para configurar la interfaz cuando se conecta al servidor. Se habilita el chat y se conecta la señal de enter para enviar mensajes.
        """
        self.chat.chat_escritura.returnPressed.connect(lambda: self.cliente.escribir(self.chat.chat_escritura.text()))
        self.chat.chat_escritura.returnPressed.connect(self.chat.chat_escritura.clear)
        self.chat.setEnabled(True)
        
    def construirJuego(self):
        """Función para arrancar el juego. Generalmente esta función es llamada por un comando recibido por el servidor.
        En caso de ser el host. Es llamada por el botón de iniciar juego.
        """
        if self.juegoIniciado:
            return
        
        if self.jugadoresLista == []:
            self.jugadoresLista = self.cliente.jugadoresLista
            
        self.actualizarTablerodeJugadores()
        self.zonaHabilidades.generarHabilidades()
        self.servidor.flag_aceptar_clientes = False
        self.juegoIniciado = True

    def iniciarJuego(self):
        """Función para iniciar el juego. Se envía un comando al servidor para que este lo reenvíe a los clientes y se inicie el juego.
        Este botón solo funciona para el host.
        """
        if not self.juegoIniciado:
            lista_json = json.dumps(self.jugadoresLista)
            self.cliente.escribir(f'//iniciarJuego {lista_json}')
            self.btnIniciarJuego.setEnabled(False)
            self.crearEtiquetasDeJugadores()
            self.construirJuego()
            self.cliente.tablero = self.tableroPropio
            self.tableroPropio.elegirBarcos()
            self.zonaHabilidades.alternarHabilidades(False)

    def cerrarServidor(self):
        """Función para cerrar el servidor. Se cierra el servidor y se habilitan los botones para iniciar el servidor y el juego.
        """
        self.servidor.server.close()
        self.btnIniciarServidor.setEnabled(True)
        self.btnConectar.setEnabled(True)
        self.procesarMensaje(f'Servidor cerrado')
        self.barraEstado.showMessage(f'¡Bienvenido {self.nombreUsuario}!')

    def recibirTableros(self, nombre, tablero):
        """Recibe el nombre de cada cliente y el tablero de estos luego de que el servidor los reenvío. En lugar de recibir el objeto completo
        recibe solamente el estado de los botones activos.

        Args:
            nombre (str): nombre del jugador que envía el tablero
            tablero (list): Lista de botones con contenido relevante para el jugador
        """
        for widget in self.contenedorEnemigosH.findChildren(QTableros):
            if widget.etNombre.text() == nombre:
                for botonActivo in tablero:
                    boton = widget[botonActivo]
                    boton.disparado = True
        if nombre == self.nombreUsuario:
            for botonActivo in tablero:
                boton = self.tableroPropio[botonActivo]
                boton.disparado = True
                if botonActivo in self.tableroPropio.barco:
                    boton.setStyleSheet('background-color: #B22222;')
                
    def usoDeHabilidades(self, habilidad):
        """Función para el uso de habilidades. 

        Args:
            habilidad (str): Nombre de la habilidad a ejecutar
        """
        if habilidad == 'Llamado a refuerzos':
            self.tableroPropio.obtenerbarco('Portaaviones')
        elif habilidad == 'Reposicionamiento':
            self.tableroPropio.reposicionamiento()

class TableroEnGrande(QDialog):
    """Creador de tablero en grande para manipularlo
    """
    def __init__(self, parent=None, tablero = QWidget):
        super().__init__(parent)
        self.setWindowTitle(f"Tablero de: {tablero.etNombre.text()}")
        self.setFixedSize(500, 500)
        self.tablero = tablero

        # Construcción del tablero en grande
        contenedor = QVBoxLayout()
        
        botonSalir = QPushButton("Volver")
        botonSalir.clicked.connect(self.cerrarDialogo)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        contenedor.addWidget(tablero)
        contenedor.addWidget(botonSalir)
        self.setLayout(contenedor)

    # Cerrar el tablero en grande
    def cerrarDialogo(self):
        """Función para cerrar el tablero en grande y volver al juego
        """
        self.close()
        self.parent().layout.insertWidget(0, self.tablero)
        self.parent().ventana_tablero_abierta = None

if __name__ == "__main__":
    ip = obtener_ip()
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())

# TODO:
# - Configurar el uso de habilidades
# - Configurar los turnos de los jugadores
# - Configurar la eliminación de los jugadores al perder
# - Administrar excepciones y errores
# - Configurar el chat para evitar que se envíen mensajes comandos manualmente
# - Comprobar si realmente es necesaria la validación de comandos por el servidor o solo mantener una retransmisión.
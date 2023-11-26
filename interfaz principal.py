import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QGridLayout, QScrollArea, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel, QStatusBar, QMenu, QToolBar
from PyQt5.QtCore import Qt
from Modulos import QChat, QTableros, QNombreUsuario, QHabilidades, DialogoConexion, obtener_ip
from cliente_ui import QJugador
from servidor import Servidor
from PyQt5.QtGui import QIcon


class InterfazPrincipal(QMainWindow):
    servidor = Servidor
    """Interfaz Principal del juego donde se conectarán los modulos para iniciar el juego
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship")
        self.setMinimumSize(1300, 800)
        self.widgetPrincipal = QWidget()
        self.setContentsMargins(10, 10, 10, 0)
        self.setStyleSheet('background-color: LightYellow; color: FireBrick; font: Consolas;')
        self.setWindowIcon(QIcon('Icono.png'))

        botonMenu = QPushButton('Conexión')
        botonMenu.setFlat(True)
        listaDeMenu = QMenu()
        botonMenu.setMenu(listaDeMenu)
        menu = QToolBar()
        menu.addWidget(botonMenu)
        menu.setStyleSheet('background-color: LightYellow; font: Consolas; font-size: 20px;')
        self.addToolBar(menu)
        self.btnconectar = listaDeMenu.addAction('Conectar')
        self.btnconectar.triggered.connect(self.conectar)
        self.btndesconectar = listaDeMenu.addAction('Desconectar')
        self.btndesconectar.setEnabled(False)
        salir = listaDeMenu.addAction('Salir')
        salir.triggered.connect(self.close)

        # Lista para mantener los componentes del juego
        self.widgets = []

        # Dialogo para ingresar el nombre de usuario
        self.nombreUsuario = QNombreUsuario().abrirDialogo() #Nombre de usuario
        print(self.nombreUsuario)
        
        # Lista de los jugadores activos que pertenecerán al juego.
        self.jugadoresLista = ['Mario']
        self.jugadoresLista.append(self.nombreUsuario)

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

        # Tablero propio del usuario
        self.tableroPropio = QTableros()
        self.tableroPropio.etNombre.setText(self.nombreUsuario)

        # Tablero con las habilidades del jugador
        zonaHabilidades = QHabilidades()

        # Variables para operaciones futuras
        self.diccionarioDeJugadores = {}
        self.ventana_tablero_abierta = None

        # Creación de los nombres de los jugadores en el contenedor
        self.contenedorJugadores = QVBoxLayout()

        # Barra de estado para mostrar mensajes
        self.barraEstado = QStatusBar()
        self.barraEstado.setStyleSheet('background: LightYellow; color: FireBrick; font: Consolas;')
        self.barraEstado.showMessage(f'¡Bienvenido {self.nombreUsuario}!')

        self.guardarJugadores()
        self.crearEtiquetasDeJugadores()
        self.actualizarTablerodeJugadores()

        #Componentes de los tableros e importación a la interfaz
        self.contenedorPrincipal.addLayout(self.contenedorJugadores, 0, 0)
        self.contenedorPrincipal.addWidget(self.chat, 1, 0)
        self.contenedorPrincipal.addWidget(self.tableroPropio, 1, 1, Qt.AlignCenter)
        self.contenedorPrincipal.addWidget(self.scrollEnemigos, 0, 1)
        self.contenedorPrincipal.addWidget(zonaHabilidades, 0, 2, 2, 1, Qt.AlignCenter)
        self.contenedorPrincipal.addWidget(self.barraEstado, 2, 0, 1, 2)
        self.setCentralWidget(self.widgetPrincipal)

    def guardarJugadores(self):
        # Creación de los jugadores en un diccionario
        for player in self.jugadoresLista:
            jugadoraIngresar = QJugador(None, player, QTableros(None, False))
            self.diccionarioDeJugadores[player] = jugadoraIngresar

    def crearEtiquetasDeJugadores(self):
        coloresNombres = ['red', 'MidnightBlue', 'YellowGreen', 'Gold', 'Indigo', 'Orange', 'PaleVioletRed', 'SaddleBrown', 'SlateGray', 'Teal', 'Tomato', 'Turquoise', 'Violet', 'Yellow']
        for nombre in self.jugadoresLista:
            nuevoJugador = QLabel(nombre)
            nuevoJugador.setStyleSheet('font-size: 20px')
            nuevoJugador.setStyleSheet(f'font: Consolas; font-size: 40px; color: {random.choice(coloresNombres)};')
            self.contenedorJugadores.addWidget(nuevoJugador)

    def actualizarTablerodeJugadores(self):
        # Creación de los tableros enemigos en el contenedor de los mismos
        for jugador in self.diccionarioDeJugadores:
            if self.nombreUsuario != self.diccionarioDeJugadores[jugador].nombre:
                tableroEnemigo = QTableros(self.scrollEnemigos, False)
                tableroEnemigo.etNombre.setText(self.diccionarioDeJugadores[jugador].nombre)
                tableroEnemigo.etNombre.setToolTip(f'Click para ver el tablero de {tableroEnemigo.etNombre.text()}')
                tableroEnemigo.etNombre.clicked.connect(lambda tablero=tableroEnemigo: self.mostrarTablero(tablero))
                self.layout = self.contenedorEnemigosH.layout()
                self.layout.insertWidget(0, tableroEnemigo)
                # tableroEnemigo.boton.clicked.connect(lambda checked, tablero=tableroEnemigo: self.mostrarTablero(tablero))


    # Abrir un tablero en grande para operar en el mismo y evitar mas de una apertura de este
    def mostrarTablero(self, tablero):
        if self.ventana_tablero_abierta is None:
            ventana_tablero = TableroEnGrande(self, tablero)
            self.ventana_tablero_abierta = ventana_tablero
            ventana_tablero.exec()

    def actualizarChat(self, mensaje):
        self.chat.chat_texto.appendPlainText(mensaje)

    def conectar(self):
        self.ip = obtener_ip()
        self.dialogoConectar = DialogoConexion()
        self.dialogoConectar.exec()
        try:
            self.cliente = QJugador(None, self.nombreUsuario, self.tableroPropio, self.dialogoConectar.ip, self.dialogoConectar.puerto)
            self.cliente.conectar()
            self.cliente.mensaje_recibido.connect(self.actualizarChat)
            self.cliente.conexion_exitosa.connect(self.actualizarChat)
            self.cliente.conexion_no_exitosa.connect(self.actualizarChat)
            self.cliente.servidor_caido.connect(self.actualizarChat)
            self.chat.chat_texto.appendPlainText(f'Conectado al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto} como {self.nombreUsuario}')
            self.btnconectar.setEnabled(False)
            self.btndesconectar.setEnabled(True)
            self.barraEstado.showMessage(f'Conectado al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto} como {self.nombreUsuario}')
            self.chat.setEnabled(True)
        except RuntimeError:
            self.chat.chat_texto.appendPlainText(f'No se pudo conectar al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto}')
            self.barraEstado.showMessage(f'No se pudo conectar al servidor {self.dialogoConectar.ip}:{self.dialogoConectar.puerto}', 3000)
        except OSError:
            self.chat.chat_texto.appendPlainText('No se pudo conectar al servidor')
            self.barraEstado.showMessage('No se pudo conectar al servidor', 3000)

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
        self.close()
        self.parent().layout.insertWidget(0, self.tablero)
        self.parent().ventana_tablero_abierta = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())
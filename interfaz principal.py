import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QGridLayout, QScrollArea, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from Modulos import QChat, QTableros, QNombreUsuario, QHabilidades
from cliente_ui import QJugador
from PyQt5.QtGui import QIcon

class InterfazPrincipal(QMainWindow):
    """Interfaz Principal del juego donde se conectarán los modulos para iniciar el juego
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship")
        self.setMinimumSize(1300, 800)
        self.widgetPrincipal = QWidget()
        self.setContentsMargins(10, 10, 10, 20)
        self.setStyleSheet('background-color: LightYellow; color: FireBrick; font: Consolas;')
        self.setWindowIcon(QIcon('Icono.png'))

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
        self.chat.setFixedSize(300, 300)

        # Tablero propio del usuario
        tableroPropio = QTableros()
        tableroPropio.etNombre.setText(self.nombreUsuario)

        # Tablero con las habilidades del jugador
        zonaHabilidades = QHabilidades()

        # Variables para operaciones futuras
        self.diccionarioDeJugadores = {}
        self.ventana_tablero_abierta = None

        # Creación de los nombres de los jugadores en el contenedor
        self.contenedorJugadores = QVBoxLayout()

        self.guardarJugadores()
        self.crearEtiquetasDeJugadores()
        self.actualizarTablerodeJugadores()

        #Componentes de los tableros e importación a la interfaz
        self.contenedorPrincipal.addLayout(self.contenedorJugadores, 0, 0)
        self.contenedorPrincipal.addWidget(self.chat, 1, 0)
        self.contenedorPrincipal.addWidget(tableroPropio, 1, 1, Qt.AlignCenter)
        self.contenedorPrincipal.addWidget(self.scrollEnemigos, 0, 1)
        self.contenedorPrincipal.addWidget(zonaHabilidades, 0, 2, 2, 1, Qt.AlignCenter)
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
            nuevoJugador.setStyleSheet(f'font: Consolas; font-size: 40px; color: {random.choice(coloresNombres)};')
            self.contenedorJugadores.addWidget(nuevoJugador)

    def actualizarTablerodeJugadores(self):
        # Creación de los tableros enemigos en el contenedor de los mismos
        for jugador in self.diccionarioDeJugadores:
            if self.nombreUsuario != self.diccionarioDeJugadores[jugador].nombre:
                tableroEnemigo = QTableros(self.scrollEnemigos, False)
                tableroEnemigo.etNombre.setText(self.diccionarioDeJugadores[jugador].nombre)
                tableroEnemigo.etNombre.setToolTip(f'Click para ver el tablero de {tableroEnemigo.etNombre.text()}')
                tableroEnemigo.etNombre.clicked.connect(lambda checked, tablero=tableroEnemigo: self.mostrarTablero(tablero))
                self.layout = self.contenedorEnemigosH.layout()
                self.layout.insertWidget(0, tableroEnemigo)
                # tableroEnemigo.boton.clicked.connect(lambda checked, tablero=tableroEnemigo: self.mostrarTablero(tablero))


    # Abrir un tablero en grande para operar en el mismo y evitar mas de una apertura de este
    def mostrarTablero(self, tablero):
        if self.ventana_tablero_abierta is None:
            ventana_tablero = TableroEnGrande(self, tablero)
            self.ventana_tablero_abierta = ventana_tablero
            ventana_tablero.exec()


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
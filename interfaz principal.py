import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QGridLayout, QScrollArea, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from Modulos import QChat, QTableros, QJugador, QNombreUsuario, QHabilidades

class InterfazPrincipal(QMainWindow):
    """Interfaz Principal del juego donde se conectarán los modulos para iniciar el juego
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship")
        self.setMinimumSize(1300, 800)
        self.widgetPrincipal = QWidget()
        self.setContentsMargins(10, 10, 10, 20)
        self.widgets = [] # Lista para mantener los componentes del juego
        self.setStyleSheet('background-color: LightYellow; color: FireBrick; font: Consolas;')

        nombreUsuario = QNombreUsuario().abrirDialogo() #Nombre de usuario
        jugadoresLista = ["kike", "Jugador 2", "Jugador 3"]

        self.contenedorPrincipal = QGridLayout(self.widgetPrincipal)

        contenedorEnemigos = QFrame()
        scrollEnemigos = QScrollArea(contenedorEnemigos)
        scrollEnemigos.setStyleSheet('background: SandyBrown;')
        scrollEnemigos.setWidgetResizable(True)
        scrollEnemigos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollEnemigos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        contenedorEnemigosH = QWidget()
        layoutEnemigos = QHBoxLayout(contenedorEnemigosH)
        scrollEnemigos.setWidget(contenedorEnemigosH)

        self.chat = QChat(None, nombreUsuario)
        self.chat.setFixedSize(300, 300)

        tableroPropio = QTableros()
        tableroPropio.etNombre.setText(nombreUsuario)

        zonaHabilidades = QHabilidades()

        self.diccionarioDeJugadores = {}
        self.ventana_tablero_abierta = None

        for player in jugadoresLista:
            jugadoraIngresar = QJugador(None, player, QTableros(None, False))
            self.diccionarioDeJugadores[player] = jugadoraIngresar

        for jugador in self.diccionarioDeJugadores:
            if nombreUsuario != self.diccionarioDeJugadores[jugador].nombre:
                tableroEnemigo = QTableros(scrollEnemigos, False)
                tableroEnemigo.etNombre.setText(self.diccionarioDeJugadores[jugador].nombre)
                tableroEnemigo.etNombre.clicked.connect(lambda checked, tablero=tableroEnemigo: self.mostrarTablero(tablero))
                self.layout = contenedorEnemigosH.layout()
                self.layout.insertWidget(0, tableroEnemigo)
                # tableroEnemigo.boton.clicked.connect(lambda checked, tablero=tableroEnemigo: self.mostrarTablero(tablero))

        contenedorJugadores = QVBoxLayout()
        for i in jugadoresLista:
            nuevoJugador = QLabel(i)
            nuevoJugador.setStyleSheet('border: 1px solid green; font: Consolas;')
            contenedorJugadores.addWidget(nuevoJugador)

        #Componentes de los tableros
        self.contenedorPrincipal.addLayout(contenedorJugadores, 0, 0)
        self.contenedorPrincipal.addWidget(self.chat, 1, 0)
        self.contenedorPrincipal.addWidget(tableroPropio, 1, 1, Qt.AlignCenter)
        self.contenedorPrincipal.addWidget(scrollEnemigos, 0, 1)
        self.contenedorPrincipal.addWidget(zonaHabilidades, 0, 2)
        self.widgets.append(jugador)
        self.widgets.append(tableroPropio)
        self.widgets.append(scrollEnemigos)
        self.widgets.append(zonaHabilidades)
        self.setCentralWidget(self.widgetPrincipal)

    def mostrarTablero(self, tablero):
        if self.ventana_tablero_abierta is None:
            ventana_tablero = TableroEnGrande(self, tablero)
            self.ventana_tablero_abierta = ventana_tablero
            ventana_tablero.exec()

class TableroEnGrande(QDialog):
    """Creador de tablero en grande para manipular el mismo
    """
    def __init__(self, parent=None, tablero = QWidget):
        super().__init__(parent)
        self.setWindowTitle(f"Tablero de: {tablero.etNombre.text()}")
        self.setFixedSize(500, 500)
        self.tablero = tablero
        contenedor = QVBoxLayout()
        
        botonSalir = QPushButton("Volver")
        botonSalir.clicked.connect(self.cerrarDialogo)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        contenedor.addWidget(tablero)
        contenedor.addWidget(botonSalir)
        self.setLayout(contenedor)

    def cerrarDialogo(self):
        self.close()
        self.parent().layout.insertWidget(0, self.tablero)
        self.parent().ventana_tablero_abierta = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())
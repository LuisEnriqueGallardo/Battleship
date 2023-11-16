import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit, QLineEdit, QGridLayout, QPushButton, QSizePolicy, QLabel, QDialog, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

fuente = QFont('Consolas', 12)

class QTableros(QWidget):
    """Tableros para cada jugador con los parametros y configuraciones de cada uno.

    Args:
        parent = None
        botonesActivos = True (Activa los botones del tablero)
        barcosActivos = [] (Lista con los barcos de cada jugador (QJugador.barcos))
    """
    def __init__(self, parent=None, botonesActivos = True, barcosActivos = []):
        super().__init__(parent)
        self.activarBotones = botonesActivos
        self.barcosActivos = barcosActivos
        self.casillas = []
        self.etNombre = QLabel('Jugador X')
        self.etNombre.setFont(fuente)
        self.nombre = self.etNombre.text()
        contenedorTitulo = QVBoxLayout(self)

        contenedorPrincipal = QPushButton()
        contenedorPrincipal.setFixedSize(400, 400)

        contenedorTitulo.addWidget(self.etNombre)
        contenedorTitulo.addWidget(contenedorPrincipal)

        cuadricula = QGridLayout(contenedorPrincipal)
        cuadricula.setSpacing(0)

        self.boton = contenedorPrincipal
        for i in range(10):
            for j in range(10):
                botonC = QPushButton()
                # botonC.setText(f"{chr(ord('A') + i)}{j}")
                botonC.setStyleSheet("background-color: CornFlowerBlue; font-size: 20px; color: white; font-family: Calibri; border: 1px solid BurlyWood")
                botonC.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                if botonesActivos == False:
                    botonC.setEnabled(False)
                botonC.clicked.connect(lambda state, i=i, j=j: self.botonClick(i, j))
                cuadricula.addWidget(botonC, i, j)
                self.casillas.append(botonC)
    
    def elegirBarcos(self):
        numero = 0
        for i in self.casillas:
            print(numero)
        for i in range(len(self.barcosActivos)):
            pass

    def botonClick(self, i, j):
        print(f"Hola {chr(ord('A') + i)}{j}")

class QJugador(QWidget):
    """Objeto para los jugadores y sus atributos

    Args:
        jugador: Nombre
        QWidget: QTablero
    """
    def __init__(self, parent=None, jugador = '', tablero = QWidget):
        super().__init__(parent)
        self.nombre = jugador
        self.habilidades = []
        self.barcos = []
        self.tablero = tablero

class QHabilidades(QWidget):
    """Habilidades de los jugadores definidas con una descripción en cada una

    Args:
        parent = None
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        contenedorEnemigos = QFrame()
        scrollEnemigos = QScrollArea(contenedorEnemigos)
        scrollEnemigos.setWidgetResizable(True)
        scrollEnemigos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollEnemigos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layoutEnemigos = QVBoxLayout(self)
        añadir = layoutEnemigos.layout()

        variablesDePrueba = ['Carta 1', 'Carta 2', 'Carta 3']
        for i in variablesDePrueba:
            asd = QLabel(i)
            asd.setPixmap(QPixmap('CuadroHabilidades.png'))
            asd.setFixedSize(200, 200)
            añadir.addWidget(asd)

class QChat(QWidget):
    """Chat para la interacción entre jugadores

    Args:
        parent: None
        nombreDeUsuario: '' (Nombre del jugador)
    """
    def __init__(self, parent=None, nombreDeUsuario = ''):
        super().__init__(parent)
        self.nombreDeUsuario = nombreDeUsuario
        
        contenedor = QVBoxLayout(self)
        self.chat_escritura = QLineEdit()
        self.chat_texto = QTextEdit()
        self.chat_texto.setReadOnly(True)

        boton_enviar = QPushButton()
        boton_enviar.setText("Enviar")
        boton_enviar.clicked.connect(self.enviarMensaje)

        contenedor.addWidget(self.chat_texto)
        contenedor.addWidget(self.chat_escritura)
        contenedor.addWidget(boton_enviar)

    def enviarMensaje(self):
        # nombre = QNombreUsuario().entradaNombre.text()
        mensaje = self.chat_escritura.text()
        self.chat_escritura.clear()
        if mensaje != "":
            self.chat_texto.append(f"\n {self.nombreDeUsuario}: {mensaje}")


class QNombreUsuario(QDialog):
    """Ventana para el ingreso del nombre de usuario

    Args:
        parent: None
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entradaNombre = QLineEdit()

    def abrirDialogo(self):
        dialogo = QDialog(self)
        dialogo.setWindowFlag(Qt.WindowCloseButtonHint, False)
        dialogo.setFont(fuente)
        dialogo.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialogo.setWindowTitle("Nombre de Usuario")
        dialogo.setFixedSize(300, 100)

        layout = QVBoxLayout(dialogo)

        layout.addWidget(self.entradaNombre)

        btnAgregar = QPushButton("Aceptar")
        layout.addWidget(btnAgregar)
        btnAgregar.clicked.connect(dialogo.accept)
        self.text = self.entradaNombre.text()

        result = dialogo.exec_()
        return self.entradaNombre.text()
        
import random
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QWidget, QPlainTextEdit, QLineEdit, QGridLayout, QPushButton, QSizePolicy, QDialog, QScrollArea, QFrame, QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize
import socket

def obtener_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

fuente = QFont('Consolas', 12)

class QTableros(QWidget):
    """Tableros para cada jugador con los parametros y configuraciones de cada uno.

    Args:
        parent = None
        botonesActivos = True (Activa los botones del tablero)
        barcosActivos = [] (Lista con los barcos de cada jugador (QJugador.barcos))
    """
    def __init__(self, parent=None, botonesActivos = True, barcosActivos = ['Acorazar', 'Ataque aereo', 'Bombardero', 'Cañon doble']):
        super().__init__(parent)
        # Variables para operaciones futuras
        self.activarBotones = botonesActivos
        self.barcosActivos = barcosActivos
        self.casillas = []
        self.etNombre = QPushButton('Jugador X')
        self.etNombre.setFlat(True)
        self.etNombre.setFont(fuente)
        self.nombre = self.etNombre.text()
        contenedorTitulo = QVBoxLayout(self)

        contenedorPrincipal = QFrame()
        # contenedorPrincipal.setDisabled(True)
        contenedorPrincipal.setFixedSize(390, 390)

        contenedorTitulo.addWidget(self.etNombre)
        contenedorTitulo.addWidget(contenedorPrincipal)

        self.cuadricula = QGridLayout(contenedorPrincipal)
        self.cuadricula.setSpacing(0)

        self.boton = contenedorPrincipal

        # Creación de los botones para el tablero y la self.cuadricula, además de la configuración individual de cada uno
        for i in range(10):
            for j in range(10):
                botonC = QPushButton()
                # botonC.setText(f"{chr(ord('A') + i)}{j}")
                botonC.setStyleSheet("background-color: CornFlowerBlue; border: 1px solid BurlyWood")
                botonC.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                if botonesActivos == False:
                    botonC.setEnabled(False)
                # botonC.clicked.connect(lambda state, i=i, j=j: self.elegirBarcos(i, j))
                botonC.clicked.connect(lambda checked, barcosDisponibles = self.barcosActivos: self.elegirBarcos(barcosDisponibles))
                self.cuadricula.addWidget(botonC, i, j)
                self.casillas.append(botonC)

    def elegirBarcos(self, barcosDisponibles):
        # BarcosDisponibles es la Lista de Barcos que tiene el jugador
        for casilla in self.casillas:
            casilla.setStyleSheet("background-color: Red; border: 1px solid BurlyWood")
            casilla.setEnabled(True)
            casilla.clicked.connect(lambda _, casilla=casilla: self.colocarBarcos(casilla))
    
    def colocarBarcos(self, botonElegido):
        barcosElegidos = []
        barcosElegidos.append(botonElegido)
        for casilla in self.casillas:
            if casilla != botonElegido:
                casilla.setEnabled(False)

        botonElegido.setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
        botonElegido.setEnabled(True)
        coord = self.casillas.index(botonElegido)
        self.configurar_casilla(coord)

    def configurar_casilla(self, coord):
        # Habilita la casilla en la posición actual
        self.casillas[coord].setEnabled(True)
        self.casillas[coord].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
        self.casillas[coord].clicked.connect(lambda _, casilla=self.casillas[coord]: self.guardarPosicionesDeBarcos(casilla))

        # Calcula la fila y columna de la casilla
        fila = coord // 10
        columna = coord % 10

        # Habilita la casilla hacia arriba si no está en la primera fila
        if fila > 0:
            coord_arriba = coord - 10
            self.casillas[coord_arriba].setEnabled(True)
            self.casillas[coord_arriba].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
            self.casillas[coord_arriba].clicked.connect(lambda _, casilla=self.casillas[coord_arriba]: self.guardarPosicionesDeBarcos(casilla))

        # Habilita la casilla hacia abajo si no está en la última fila
        if fila < 9:
            coord_abajo = coord + 10
            self.casillas[coord_abajo].setEnabled(True)
            self.casillas[coord_abajo].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
            self.casillas[coord_abajo].clicked.connect(lambda _, casilla=self.casillas[coord_abajo]: self.guardarPosicionesDeBarcos(casilla))

        # Habilita la casilla hacia la izquierda si no está en la primera columna
        if columna > 0:
            coord_izquierda = coord - 1
            self.casillas[coord_izquierda].setEnabled(True)
            self.casillas[coord_izquierda].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
            self.casillas[coord_izquierda].clicked.connect(lambda _, casilla=self.casillas[coord_izquierda]: self.guardarPosicionesDeBarcos(casilla))

        # Habilita la casilla hacia la derecha si no está en la última columna
        if columna < 9:
            coord_derecha = coord + 1
            self.casillas[coord_derecha].setEnabled(True)
            self.casillas[coord_derecha].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
            self.casillas[coord_derecha].clicked.connect(lambda _, casilla=self.casillas[coord_derecha]: self.guardarPosicionesDeBarcos(casilla))


    def guardarPosicionesDeBarcos(self, barcoGuardado):
        pass


class QHabilidades(QWidget):
    """Contenedor de las habilidades de cada jugador
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(380, 900)
        self.habilidades = {}

        # Contenedor donde se generaran las habilidades
        contenedorEnemigos = QFrame()
        scrollEnemigos = QScrollArea()
        scrollEnemigos.setWidgetResizable(True)
        scrollEnemigos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollEnemigos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)


        layoutEnemigos = QVBoxLayout(contenedorEnemigos)
        self.añadir = layoutEnemigos.layout()

        # Creación de los botones para las habilidades y inicialización de 3 habilidades por defecto

        scrollEnemigos.setWidget(contenedorEnemigos)

        layoutPrincipal = QVBoxLayout(self)
        layoutPrincipal.addWidget(scrollEnemigos)

        self.ventana_habilidad_abierta = None
        
    def generarHabilidades(self):
        variablesDePrueba = ['Acorazar','Ataque aereo', 'Bombardero', 'Cañon doble', 'Hackeo terminal', 'Llamado a refuerzos', 'Radar satelital', 'Reconocimiento aereo', 'Reposicionamiento']
        for _ in range(3):
            botonDeHabilidad = QPushButton()
            # botonDeHabilidad.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            eleccionAleatoria = random.choice(variablesDePrueba)
            botonDeHabilidad.setIcon(QIcon(f'Habilidades/{eleccionAleatoria}.png'))
            botonDeHabilidad.setIconSize(QSize(300, 400))
            self.habilidades[eleccionAleatoria] = (botonDeHabilidad, eleccionAleatoria)
            botonDeHabilidad.clicked.connect(lambda _, habilidad=botonDeHabilidad, nombre=eleccionAleatoria: self.mostrarHabilidad(habilidad, nombre=nombre))
            self.añadir.addWidget(botonDeHabilidad)

    # Función para mostrar la habilidad en grande y evitar una segunda apertura de la misma
    def mostrarHabilidad(self, habilidad, nombre):
        if self.ventana_habilidad_abierta is None:
            nombreIcono = self.habilidades[nombre][1]
            self.HabilidadMaximizada = HabilidadEnGrande(self, habilidad, nombreIcono)
            self.ventana_habilidad_abierta = self.HabilidadMaximizada
            self.HabilidadMaximizada.exec()

class HabilidadEnGrande(QDialog):
    """Creador de tablero en grande para manipular el mismo
    """
    def __init__(self, parent=None, habilidad = QWidget, nombre = ''):
        super().__init__(parent)
        self.setWindowTitle(str(nombre))
        self.setFixedSize(500, 500)
        self.habilidad = habilidad
        
        self.habilidad.setStyleSheet("background-color: WhiteSmoke;")
        contenedor = QVBoxLayout()
        
        # Botones para salir y usar la habilidad
        botonSalir = QPushButton("Volver")
        botonSalir.clicked.connect(self.cerrarDialogo)

        botonUsar = QPushButton("Usar")
        botonUsar.clicked.connect(self.usarHabilidad)

        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        contenedor.addWidget(habilidad)
        contenedor.addWidget(botonUsar)
        contenedor.addWidget(botonSalir)
        self.setLayout(contenedor)

    # Cerrar la habilidad en grande
    def cerrarDialogo(self):
        self.habilidad.setStyleSheet(None)
        self.close()
        self.parent().añadir.insertWidget(0, self.habilidad)
        self.parent().ventana_habilidad_abierta = None

    # TODO Crear la función para usar la habilidad
    def usarHabilidad(self):
        print("Usar habilidad")

class QChat(QWidget):
    """Chat para la interacción entre jugadores

    Args:
        parent: QWidget
        nombreDeUsuario: '' (Nombre del jugador)
    """
    def __init__(self, parent=None, nombreDeUsuario = ''):
        super().__init__(parent)
        self.setStyleSheet("background-color: WhiteSmoke;")
        self.nombreDeUsuario = nombreDeUsuario
        
        # Creación de los componentes del chat
        contenedor = QVBoxLayout(self)
        self.chat_escritura = QLineEdit()
        self.chat_texto = QPlainTextEdit()
        self.chat_escritura.setFocus()
        self.chat_texto.setReadOnly(True)
        self.chat_escritura.setPlaceholderText("Escribe tu mensaje aquí")


        contenedor.addWidget(self.chat_texto)
        contenedor.addWidget(self.chat_escritura)

class QNombreUsuario(QDialog):
    """Ventana para el ingreso del nombre de usuario

    Args:
        parent: QWidget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entradaNombre = QLineEdit()
        self.setWindowIcon(QIcon('Icono.png'))

    # Función para abrir el dialogo y obtener el nombre de usuario
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

        result = dialogo.exec_()
        return self.entradaNombre.text().strip()
    
class DialogoConexion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Conectar')
        self.setFixedSize(300, 200)
        
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.direccion = QLineEdit()
        self.direccion.setPlaceholderText('Dirección a conectar: ' + obtener_ip())
        self.direccion.setFocus()
        self.ip = self.direccion.text()
        
        self.puertoElegido = QLineEdit()
        self.puertoElegido.setPlaceholderText('Puerto: 3333')
        self.puerto = self.puertoElegido.text()


        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.cancelar)

        contenedor = QVBoxLayout()
        contenedor.addWidget(self.direccion)
        contenedor.addWidget(self.puertoElegido)
        contenedor.addWidget(botones)
        self.setLayout(contenedor)

    def aceptar(self):
        try:
            self.ip = self.direccion.text()
            self.puerto = int(self.puertoElegido.text())
            self.close()
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Verifica los datos ingresados')

    def cancelar(self):
        self.close()
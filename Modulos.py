import random
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit, QLineEdit, QGridLayout, QPushButton, QSizePolicy, QDialog, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize

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
        print(coord)

        self.configurar_casilla(coord, 10, 0)
        self.configurar_casilla(coord, 1, 1)
        self.configurar_casilla(coord, -10, 2)
        self.configurar_casilla(coord, -1, 3)

    def configurar_casilla(self, coord, desplazamiento, direccion):
        nueva_coord = coord + desplazamiento
        if 0 <= nueva_coord <= 99 and (direccion == 0 or nueva_coord % 10 != 0) and (direccion == 1 or nueva_coord % 10 != 9):
            self.casillas[nueva_coord].setEnabled(True)
            self.casillas[nueva_coord].setStyleSheet("background-color: Green; border: 1px solid BurlyWood")
            self.casillas[nueva_coord].clicked.connect(lambda _, casilla=self.casillas[nueva_coord]: self.guardarPosicionesDeBarcos(casilla))

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
        variablesDePrueba = ['Acorazar','Ataque aereo', 'Bombardero', 'Cañon doble', 'Hackeo terminal', 'Llamado a refuerzos', 'Radar satelital', 'Reconocimiento aereo', 'Reposicionamiento']
        for i in range(3):
            botonDeHabilidad = QPushButton()
            # botonDeHabilidad.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            eleccionAleatoria = random.choice(variablesDePrueba)
            botonDeHabilidad.setIcon(QIcon(f'Habilidades/{eleccionAleatoria}.png'))
            botonDeHabilidad.setIconSize(QSize(300, 400))
            self.habilidades[eleccionAleatoria] = (botonDeHabilidad, eleccionAleatoria)
            botonDeHabilidad.clicked.connect(lambda checked, habilidad=botonDeHabilidad, nombre=eleccionAleatoria: self.mostrarHabilidad(habilidad, nombre=nombre))
            self.añadir.addWidget(botonDeHabilidad)

        scrollEnemigos.setWidget(contenedorEnemigos)

        layoutPrincipal = QVBoxLayout(self)
        layoutPrincipal.addWidget(scrollEnemigos)

        self.ventana_habilidad_abierta = None

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
        self.chat_texto = QTextEdit()
        self.chat_texto.setReadOnly(True)
        self.chat_escritura.setPlaceholderText("Escribe tu mensaje aquí")
        self.chat_escritura.returnPressed.connect(self.enviarMensaje)

        boton_enviar = QPushButton()
        boton_enviar.setText("Enviar")
        boton_enviar.clicked.connect(self.enviarMensaje)

        contenedor.addWidget(self.chat_texto)
        contenedor.addWidget(self.chat_escritura)
        contenedor.addWidget(boton_enviar)

    # Función para enviar mensajes
    def enviarMensaje(self):
        # nombre = QNombreUsuario().entradaNombre.text()
        mensaje = self.chat_escritura.text()
        self.chat_escritura.clear()
        if mensaje != "":
            self.chat_texto.append(f"\n {self.nombreDeUsuario}: {mensaje}")


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
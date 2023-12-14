import random
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QWidget, QPlainTextEdit, QLineEdit, QGridLayout, QPushButton, QSizePolicy, QDialog, QScrollArea, QFrame, QDialogButtonBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize
import socket

def obtener_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

fuente = QFont('Consolas', 12)

class QTableros(QWidget):
    barcosElegidos = pyqtSignal()
    """Tableros para cada jugador con los parametros y configuraciones de cada uno.

    Args:
        parent = None
        botonesActivos = Booleano (Activa los botones del tablero)
        barcosActivos = List (Lista con los barcos de cada jugador (QJugador.barcos))
    """
    def __init__(self, parent=None, botonesActivos = True, barcosActivos = ['CruceroDeAsalto', 'CruceroDeAsalto', 'Portaaviones','Portaaviones', 'Acorazado',  'Acorazado', 'Acorazado']):
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
        self.listaDePosiciones = []

        contenedorPrincipal = QFrame()
        # contenedorPrincipal.setDisabled(True)
        contenedorPrincipal.setFixedSize(390, 390)

        contenedorTitulo.addWidget(self.etNombre)
        contenedorTitulo.addWidget(contenedorPrincipal) 

        self.cuadricula = QGridLayout(contenedorPrincipal)
        self.cuadricula.setSpacing(0)

        self.orientacion = QPushButton('⇀')
        self.orientacion.setFixedSize(30, 30)
        self.orientacion.setToolTip('Horizontal')
        self.orientacion.clicked.connect(self.cambiarOrientacion)
        contenedorTitulo.addWidget(self.orientacion)
        
        self.barcosDisponibles = []
        
        # Creación de los botones para el tablero y la self.cuadricula, además de la configuración individual de cada uno
        for i in range(10):
            for j in range(10):
                botonC = BotonBattleship(i, j)
                # botonC.setText(f"{chr(ord('A') + i)}{j}")
                botonC.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                if botonesActivos == False:
                    botonC.setEnabled(False)
                self.cuadricula.addWidget(botonC, i, j)
                self.casillas.append(botonC)

    def cambiarOrientacion(self):
        """Alterna la orientación de colocación de los barcos en el tablero.
        """
        if self.orientacion.text() == '⇂':
            self.orientacion.setText('⇀')
            self.orientacion.setToolTip('Horizontal')
        else:
            self.orientacion.setText('⇂')
            self.orientacion.setToolTip('Vertical')

    def elegirBarcos(self):
        """Función desencadenadora para la elección de barcos donde se generan los botones para cada barco.
        """
        for i in range(len(self.barcosActivos)):
            # Agrega el nombre del barco a la posición 11 de la fila correspondiente
            barcoButton = QPushButton(f'{i}')
            barcoButton.setToolTip(f'{self.barcosActivos[i]}. \n "CruceroDeAsalto" = 3 Espacios \n "Portaaviones" = 2 Espacios \n "Acorazado" = 1 Espacio')
            self.cuadricula.addWidget(barcoButton, i, 11)
            barco = self.barcosActivos[i]
            barcoButton.clicked.connect(lambda: self.alternarBotones(False))
            barcoButton.clicked.connect(lambda _, barco=barco: self.seleccionarTipoBarco(barco))
            barcoButton.clicked.connect(lambda _, barco=barcoButton: barco.setVisible(False))
            barcoButton.setStyleSheet("background-color: #ec9b9d;")
            self.barcosDisponibles.append(barcoButton)
        print(len(self.barcosDisponibles))
    
    def alternarBotones(self, estado = bool):
        """Función para alternar el estado de los botones del tablero.

        Args:
            estado (boolean, optional): Recibe un booleano para realizar la activación o viceversa del botón. Defaults to bool.
        """
        for boton in range(self.barcosDisponibles.__len__()):
            self.cuadricula.itemAtPosition(boton, 11).widget().setEnabled(estado)
    
    def seleccionarTipoBarco(self, barco):
        """Función para la elección del tipo de barco a colocar en el tablero

        Args:
            barco (str): Es el nombre del barco a colocar. El nombre se usa para conocer su tamaño.
        """
        for casilla in self.casillas:
            if casilla.barco is None:
                casilla.setEnabled(True)
                casilla.setStyleSheet("background-color: #b3f795;")
                # Desconecta la señal clicked de cualquier función a la que esté conectada
                try:
                    casilla.clicked.disconnect()
                except TypeError:
                    pass
                # Conecta la señal clicked a colocarBarcos
                casilla.clicked.connect(lambda _, casilla=casilla, barco=barco: self.colocarBarcos(botonElegido=casilla, tipoBarco=barco , orientacion=self.orientacion.toolTip()))
                
    def colocarBarcos(self, botonElegido, tipoBarco, orientacion):
        """Función para colocar los barcos en el tablero haciendo una validación tanto del espacio en el tablero como el tamaño del barco

        Args:
            botonElegido (BotonBattleship): Boton personalizado para el tablero, contiene las coordenadas de la casilla.
            tipoBarco (str): Nombre del barco a colocar.
            orientacion (str): La orientación es una variable que contiene la orientación del barco a colocar.
        """
        try:
            # Determina el tamaño del barco basado en el tipo de barco
            if tipoBarco == "CruceroDeAsalto":
                self.tamanoBarco = 3
                self.barcoActivo = 'CruceroDeAsalto'
            elif tipoBarco == "Portaaviones":
                self.tamanoBarco = 2
                self.barcoActivo = 'Portaaviones'
            elif tipoBarco == "Acorazado":
                self.tamanoBarco = 1
                self.barcoActivo = 'Acorazado'

            # Obtiene la fila y la columna de la casilla seleccionada
            fila = botonElegido.row % 10
            columna = botonElegido.col % 10

        # Verifica si hay suficientes casillas libres en la dirección deseada
            if self.verificarCasillasLibres(fila, columna, orientacion):
                listaProvisionalDePosiciones = []
                # Coloca el barco en las casillas correspondientes
                if orientacion == "Horizontal":
                    for i in range(self.tamanoBarco):
                        self.casillas[fila * 10 + columna + i].barco = True
                        self.casillas[fila * 10 + columna + i].setStyleSheet("background-color: #0000ff;")
                        botonElegido.extensiones.append(self.casillas[fila * 10 + columna + i])
                        
                        listaProvisionalDePosiciones.append([self.casillas[fila * 10 + columna + i].row,  self.casillas[fila * 10 + columna + i].col])
                        self.eleccionFinalizada()
                    self.listaDePosiciones.append(listaProvisionalDePosiciones)
                    self.barcosDisponibles.pop(0)

                    
                elif orientacion == "Vertical":
                    for i in range(self.tamanoBarco):                    
                        self.casillas[(fila + i) * 10 + columna].barco = True
                        self.casillas[(fila + i) * 10 + columna].setStyleSheet("background-color: #0000ff;")
                        botonElegido.extensiones.append(self.casillas[(fila + i) * 10 + columna])
                        
                        listaProvisionalDePosiciones.append([  self.casillas[(fila + i) * 10 + columna].row,   self.casillas[(fila + i) * 10 + columna].col])
                        self.eleccionFinalizada()
                        self.listaDePosiciones.append(listaProvisionalDePosiciones)
                    self.barcosDisponibles.pop(0)
                    
                if self.barcosDisponibles.__len__() == 0:
                    self.alternarTablero(False)
                    self.barcosElegidos.emit()
            else:
                pass
        except Exception as e:
            print(f'Se produjo un error: {e}')
            
    def verificarCasillasLibres(self, fila, columna, orientacion):
        """Función para verificar si las casillas están libres para colocar el barco y caben en el tablero.

        Args:
            fila (int): Contiene la fila de la casilla seleccionada.
            columna (int): Contiene la columna de la casilla seleccionada.
            orientacion (str): Contiene la orientación del barco a colocar.

        Returns:
            False: Retorna False si el barco no cabe en el tablero o si las casillas no están libres.
        """
        # Verifica si el barco cabe en el tablero
        if orientacion == "Horizontal" and columna + self.tamanoBarco > 10:
            return False
        elif orientacion == "Vertical" and fila + self.tamanoBarco > 10:
            return False

        # Verifica si las casillas están libres
        if orientacion == "Horizontal":
            for i in range(self.tamanoBarco):
                if self.casillas[fila * 10 + columna + i].barco is not None:
                    return False
        elif orientacion == "Vertical":
            for i in range(self.tamanoBarco):
                if self.casillas[(fila + i) * 10 + columna].barco is not None:
                    return False

        # Si todas las casillas están libres, retorna True
        return True
    
    def eleccionFinalizada(self):
        """Función para desactivar los botones de elección de barcos y cambiar el color de las casillas que no contienen barcos.
        """
        # Este ciclo deja el tablero en un estado de solo lectura
        for casilla in self.casillas:
            casilla.setEnabled(False)
            if casilla.barco is None:
                casilla.setStyleSheet("background-color: #85C1E9")
            if casilla.barco:
                casilla.setStyleSheet("background-color: #0000ff")
        self.alternarBotones(True)
                
    def obtenerbarco(self, barco = None):
        """Función para otorgar un barco a un jugador.

        Args:
            barco (str, optional): Nombre del barco, en caso de que se requiera dar un barco en específico. Defaults to None.
        """
        # Agrega el nombre del barco a la posición 11 de la fila correspondiente
        barcoButton = QPushButton('1')
        if barco is None:
            aleatorio = random.randint(0, len(self.barcosActivos) - 1)
        else:
            if barco == 'CruceroDeAsalto':
                aleatorio = 0
            elif barco == 'Portaaviones':
                aleatorio = 2
            elif barco == 'Acorazado':
                aleatorio = 4
        barcoButton.setToolTip(f'{self.barcosActivos[aleatorio]}. \n "CruceroDeAsalto" = 3 Espacios \n "Portaaviones" = 2 Espacios \n "Acorazado" = 1 Espacio')
        self.cuadricula.addWidget(barcoButton, 0, 11)
        barco = self.barcosActivos[aleatorio]
        barcoButton.clicked.connect(lambda _, barco = barcoButton: self.barcosDisponibles.append(barco))
        barcoButton.clicked.connect(lambda _, barco=barco: self.seleccionarTipoBarco(barco))        
        barcoButton.clicked.connect(lambda _, barco=barcoButton: barco.setVisible(False))
            
    def reposicionamiento(self):
        """Función para reposicionar un barco a selección del usuario. Se activan los botones de los barcos y se cambia el color de las casillas que contienen barcos.
        """
        # Ciclo para activar los botones de los barcos y cambiar el color de las casillas que contienen barcos.
        for boton in self.casillas:
            if boton.barco:
                boton.setStyleSheet('background-color: #ffff00;')
                boton.setEnabled(True)
                coordenadas = [boton.row, boton.col]
                boton.clicked.connect(lambda _, coordenadas=coordenadas: self.buscarBarco(coordenadas))
            
    def buscarBarco(self, coordenada):
        """Recorre la lista de botones donde se encuentran los barcos y los activa para que el usuario pueda elegir el barco a mover.

        Args:
            coordenada (list): Lista donde está almacenada la coordenada del barco elegido para reposicionar.
        """
        # Desactiva los botones de los barcos y cambia el color de las casillas que no contienen barcos.
        for boton in self.casillas:
            boton.setDisabled(True)
            if boton.barco is None:
                boton.setStyleSheet('background-color: #85C1E9;')

        # Recorre la lista de posiciones de los barcos y busca la coordenada coincidente con la elegida por el usuario.
        for barco in self.listaDePosiciones:
            if coordenada in barco:
                barcoAMover = self.listaDePosiciones[self.listaDePosiciones.index(barco)]
                self.tamanoBarco = len(barco)
                for casilla in barco:
                    self.casillas[casilla[0] * 10 + casilla[1]].setEnabled(True)
                    self.casillas[casilla[0] * 10 + casilla[1]].barco = None

        # Otorga un nuevo barco al jugador de la misma longitud del elegido para reposicionar.
        if self.tamanoBarco == 3:
            self.obtenerbarco('CruceroDeAsalto')
        elif self.tamanoBarco == 2:
            self.obtenerbarco('Portaaviones')
        elif self.tamanoBarco == 1:
            self.obtenerbarco('Acorazado')
        self.eleccionFinalizada()

    def disparoOrdinario(self, coordenadas):
        for boton in self.casillas:
            if boton.row == coordenadas[0] and boton.col == coordenadas[1]:
                boton.setStyleSheet('background-color: #E74C3C;')
                boton.disparado = True
        self.alternarTablero(False)

    def tiroDoble(self, coordenadas):
        """Función para activar el tiro doble en el tablero del jugador oponente.

        Args:
            coordenadas (list): Lista con las coordenadas del tiro doble.
        """
        for boton in self.casillas:
            if boton.row == coordenadas[0] and boton.col == coordenadas[1]:
                if self.orientacion.toolTip() == 'Horizontal':
                    coordenadaBoton = self.casillas.index(boton) + 1
                else:
                    coordenadaBoton = self.casillas.index(boton) + 10
                self.alternarTablero(False)

                boton.disparado = True
                self.casillas[coordenadaBoton].disparado = True
                
                self.casillas[coordenadaBoton].setStyleSheet("background-color: #E74C3C")
                boton.setStyleSheet('background-color: #E74C3C;')
                
                for boton in self.casillas:
                    if boton.disparado is None:
                        boton.setStyleSheet("background-color: #85C1E9")

                return
            
    def tiroCuadruple(self, coordenadas):
        for boton in self.casillas:
            if boton.row == coordenadas[0] and boton.col == coordenadas[1]:
                try:
                    coordenadaBoton2 = self.casillas.index(boton) + 1
                    coordenadaBoton3 = self.casillas.index(boton) + 10
                    coordenadaBoton4 = self.casillas.index(boton) + 11
                    self.alternarTablero(False)
                    
                    boton.setStyleSheet('background-color: #E74C3C;')
                    boton.disparado = True
                    
                    self.casillas[coordenadaBoton2].disparado = True
                    self.casillas[coordenadaBoton2].setStyleSheet("background-color: #E74C3C")
                    
                    self.casillas[coordenadaBoton3].disparado = True
                    self.casillas[coordenadaBoton3].setStyleSheet("background-color: #E74C3C")
                    
                    self.casillas[coordenadaBoton4].disparado = True
                    self.casillas[coordenadaBoton4].setStyleSheet("background-color: #E74C3C")
                    
                    for boton in self.casillas:
                        if boton.disparado is None:
                            boton.setStyleSheet("background-color: #85C1E9")

                    return   
                except:
                    pass

    def alternarTablero(self, estado = bool, validarBarcos = None):
        """Función para deshabilitar el tablero del jugador.
        """
        for boton in self.casillas:
            boton.setEnabled(estado)

class QHabilidades(QWidget):
    """Contenedor de las habilidades de cada jugador
    """
    senalDeHabilidad = pyqtSignal(str)
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
        
    def alternarHabilidades(self, estado = bool):
        """Funcion que alterna el estado de las habilidades para evitar que se usen en el turno del oponente.

        Args:
            estado (boolean, optional): Recibe un booleano para realizar la activación o viceversa del botón. Defaults to bool.
        """
        for habilidad in range(self.añadir.count()):
            self.añadir.itemAt(habilidad).widget().setEnabled(estado)
        
    def generarHabilidades(self):
        """Algoritmo para generar las habilidades de forma aleatoria en base a la lista de habilidades existentes.
        """
        # listaHabilidades = ['Acorazar','Ataque aereo', 'Bombardero', 'Cañon doble', 'Hackeo terminal', 'Llamado a refuerzos', 'Radar satelital', 'Reconocimiento aereo', 'Reposicionamiento']
        listaHabilidades = ['Llamado a refuerzos', 'Reposicionamiento']
        for _ in range(3):
            botonDeHabilidad = QPushButton()
            # botonDeHabilidad.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            eleccionAleatoria = random.choice(listaHabilidades)
            botonDeHabilidad.setIcon(QIcon(f'Habilidades/{eleccionAleatoria}.png'))
            botonDeHabilidad.setIconSize(QSize(300, 400))
            self.habilidades[eleccionAleatoria] = (botonDeHabilidad, eleccionAleatoria)
            botonDeHabilidad.clicked.connect(lambda _, habilidad=botonDeHabilidad, nombre=eleccionAleatoria: self.mostrarHabilidad(habilidad, nombre=nombre))
            self.añadir.addWidget(botonDeHabilidad)

    def mostrarHabilidad(self, habilidad, nombre):
        """Función para mostrar la habilidad en grande y evitar una segunda apertura de la misma

        Args:
            habilidad (QWidget): Recibe un Widget, en este caso el botón de la habilidad.
            nombre (str): Recibe el nombre de la habilidad para trabajar con el.
        """
        if self.ventana_habilidad_abierta is None:
            nombreIcono = self.habilidades[nombre][1]
            self.HabilidadMaximizada = HabilidadEnGrande(self, habilidad, nombreIcono)
            self.HabilidadMaximizada.senalUsarHabilidad.connect(lambda n=nombre: self.avisarUsodeSenal(n))
            self.ventana_habilidad_abierta = self.HabilidadMaximizada
            self.HabilidadMaximizada.show()
            
    def avisarUsodeSenal(self, nombre):
        """Función para avisar que se usó la señal de habilidad

        Args:
            nombre (str): Recibe el nombre de la habilidad.
        """
        botonHabilidad = self.habilidades[nombre][0]
        try:
            self.añadir.removeWidget(botonHabilidad)
            botonHabilidad.setParent(None)
            botonHabilidad.deleteLater()
        except RuntimeError:
            print('LOG: No se pudo eliminar el widget')
        self.senalDeHabilidad.emit(nombre)

class HabilidadEnGrande(QDialog):
    """Creador de tablero en grande para manipular el mismo
    """
    senalUsarHabilidad = pyqtSignal()
    def __init__(self, parent=None, habilidad = QWidget, nombre = ''):
        super().__init__(parent)
        self.setWindowTitle(str(nombre))
        self.setFixedSize(500, 500)
        self.habilidad = habilidad
        self.nombre = nombre
        
        self.habilidad.setStyleSheet("background-color: WhiteSmoke;")
        contenedor = QVBoxLayout()
        
        # Botones para salir y usar la habilidad
        botonSalir = QPushButton("Volver")
        botonSalir.clicked.connect(self.cerrarDialogo)

        self.botonUsar = QPushButton("Usar")
        self.botonUsar.clicked.connect(self.usarHabilidad)
        
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        contenedor.addWidget(habilidad)
        contenedor.addWidget(self.botonUsar)
        contenedor.addWidget(botonSalir)
        self.setLayout(contenedor)

    # Cerrar la habilidad en grande
    def cerrarDialogo(self):
        """Función para cerrar la habilidad en grande
        """
        self.close()
        try:
            self.parent().añadir.insertWidget(0, self.habilidad)
        except RuntimeError:
            pass
        self.parent().ventana_habilidad_abierta = None
        
    def usarHabilidad(self):
        """Función para usar la habilidad
        """
        self.senalUsarHabilidad.emit()
        self.botonUsar.setEnabled(False)
        self.botonUsar.setText('HABILIDAD USADA')
        self.close()

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
        
        self.chat_escritura.textChanged.connect(self.controlarEnvioDeComandos)

    def controlarEnvioDeComandos(self):
        """Función para controlar el envío de mensajes en el chat evitando comandos no deseados.
        """
        if self.chat_escritura.text().strip() != '//':
            self.chat_escritura.replace('/', '')

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
        botones.rejected.connect(self.reject)

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
            
class BotonBattleship(QPushButton):
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.disparado = None  # Bandera para rastrear si se disparó en esta casilla
        self.barco = None
        self.hundido = None
        self.extensiones = []
        self.setStyleSheet("background-color: #85C1E9")
import json
import random
import sys
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow, QWidget, QFrame, QGridLayout, QScrollArea, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel, QStatusBar
from PyQt5.QtCore import Qt
from Modulos import QChat, QTableros, QNombreUsuario, QHabilidades, DialogoConexion, obtener_ip, BotonBattleship
from PyQt5.QtGui import QIcon
from JuegoServidor import Servidor, QJugador
from ColoresConsola import Colores

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
        self.listaTableros = [] #Lista de tableros

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
        self.tiroDobleActivo = None
        self.tiroCuadrupleActivo = None
        self.turnoActivo = None
        self.estadoDelTablero = []

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
        self.tableroPropio.barcosElegidos.connect(self.eleccionFinalizada)
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
                    self.layouta = self.contenedorEnemigosH.layout()
                    self.layouta.insertWidget(0, tableroEnemigo)
                    if not self.juegoIniciado:
                        self.listaTableros.append(tableroEnemigo)
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
        if mensaje.startswith("//"):
            # Aquí puedes implementar la lógica para procesar comandos
            comando = mensaje[2:]
            if ";" in comando:
                comando = comando.split(";")
                print(f'{Colores.VERDE}DIVIDIENDO COMANDO{Colores.RESET}: {comando}')
                for c in comando:
                    comando = c[2:]
                    self.procesar_comando(c)
            else:
                self.procesar_comando(comando)
        for letra in mensaje:
            if letra == '/':
                return
        self.chat.chat_texto.appendPlainText(mensaje)

    def procesar_comando(self, comando):
        """Función que procesa los comandos recibidos por el servidor. Para cada comando existe una función que se ejecuta al recibirlo.

        Args:
            comando (JSON): Comando recibido por el servidor, el cual llega como un JSON codificado en string.
        """
        print(f'{Colores.AZUL}LOG INTERFAZ{Colores.RESET}: Comando recibido: {comando}')
        
        try:
            comando, datos = comando.split(" ", 1)
        except ValueError:
            comando = comando
            datos = ""
            print(f'{Colores.ROJO}LOG INTERFAZ{Colores.RESET}: {comando} {datos}')
            
        if comando.startswith("iniciarJuego"):
            # Extraer la lista de jugadores del mensaje
            try:
                datos = datos.replace(";", '')
                lista_nombres = json.loads(datos)
                self.jugadoresLista = lista_nombres
                print(f'{Colores.AZUL}LOG INTERFAZ{Colores.RESET}: Iniciando juego con jugadores: {lista_nombres}')
            except:
                print(f'{Colores.ROJO}LOG INTERFAZ{Colores.RESET}: Error al cargar datos de jugadores')            
            self.guardarJugadores()
            self.iniciarJuego()
        
        if comando.startswith("actualizarTablero"):
            print(f'{Colores.NARANJA}LOG INTERFAZ{Colores.RESET}: {datos}')
            try:
                tablero_json = datos.split(" ", 1)[1]
                tablero = json.loads(tablero_json)
                nombreRemitente = datos.split(" ", 1)[0]
                self.recibirTableros(nombreRemitente, tablero)
            except Exception as e:
                print(f"{Colores.AZUL}LOG INTERFAZ{Colores.RESET} {self.nombreUsuario}: Error al actualizar el tablero: {e}")
                
        if comando.startswith("turno"):
            datos = datos.replace(";", '')
            if datos == self.nombreUsuario:
                print(f'{Colores.AZUL}LOG INTERFAZ{Colores.RESET}: Turno recibido')
                self.turnoActivo = True
                self.evaluarTurno()

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
        self.cliente.clienteRecibeMensaje.connect(self.procesarMensaje)
        self.cliente.conexionperdida.connect(self.procesarMensaje)
        self.cliente.clienteDesconectado.connect(self.procesarMensaje)
        self.cliente.conexionExitosa.connect(self.procesarMensaje)
        self.cliente.mensajeEnviado.connect(self.procesarMensaje)
        self.cliente.inicioJuego.connect(self.iniciarJuego)
        self.cliente.inicioJuego.connect(self.servidor.iniciarJuego)
        self.cliente.conectar()
        self.barraEstado.showMessage(f'Conectado al servidor como {self.nombreUsuario}(HOST)')
        self.btnIniciarJuego.setEnabled(True)
        self.configuracionInterfazOnline()
        
    def configuracionInterfazOnline(self):
        """Función para configurar la interfaz cuando se conecta al servidor. Se habilita el chat y se conecta la señal de enter para enviar mensajes.
        """
        mensaje = self.chat.controlarEnvioDeComandos
        self.chat.chat_escritura.returnPressed.connect(lambda: self.enviarComando(self.chat.chat_escritura.text()))
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
            self.enviarComando(f'//iniciarJuego {lista_json};')
            self.btnIniciarJuego.setEnabled(False)
            self.construirJuego()
            self.crearEtiquetasDeJugadores()
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

    def recibirTableros(self, nombre, tableroRecibido):
        """Recibe el nombre de cada cliente y el tablero de estos luego de que el servidor los reenvío. En lugar de recibir el objeto completo
        recibe solamente el estado de los botones activos.

        Args:
            nombre (str): nombre del jugador que envía el tablero
            tablero (list): Lista de botones con contenido relevante para el jugador
        """
        
        for tableroJugador in self.listaTableros:
            if tableroJugador.etNombre.text() == nombre:
                for botonViejo in tableroJugador.casillas:
                    for parametros in tableroRecibido:
                        botonNuevo = BotonBattleship(parametros[0], parametros[1])
                        botonNuevo.barco = parametros[2]
                        botonNuevo.hundido = parametros[3]
                        botonNuevo.disparado = parametros[4]
                        if botonViejo.row == botonNuevo.row and botonViejo.col == botonNuevo.col:
                            if botonNuevo.disparado:
                                botonViejo.setStyleSheet('background-color: #B22222;')
                            if botonNuevo.hundido:
                                botonViejo.setStyleSheet('background-color: #000000;')

        if nombre == self.nombreUsuario:
            for botonViejo in tableroJugador.casillas:
                    for parametros in tableroRecibido:
                        botonNuevo = BotonBattleship(parametros[0], parametros[1])
                        botonNuevo.barco = parametros[2]
                        botonNuevo.hundido = parametros[3]
                        botonNuevo.disparado = parametros[4]
                        if botonViejo.row == botonNuevo.row and botonViejo.col == botonNuevo.col:
                            if botonNuevo.disparado:
                                if botonViejo.barco:
                                    botonViejo.hundido = True
                                    botonViejo.setStyleSheet('background-color: #000000;')
                                else:
                                    botonViejo.disparado = True

    def enviar_tablero(self, habilidadUsada = None):
            """Envía el tablero al servidor. Para que el servidor lo envíe a los demás jugadores.
            """
            for boton in self.cliente.tablero.casillas:
                if boton.disparado:
                    self.estadoDelTablero.append([boton.row, boton.col, boton.barco, boton.hundido, boton.disparado])
                if boton.disparado and boton.barco:
                    boton.hundido = True
                    self.estadoDelTablero.append([boton.row, boton.col, boton.barco, boton.hundido, boton.disparado])

            mensaje = f"//actualizarTablero {self.nombreUsuario} {json.dumps(self.estadoDelTablero)};"
            self.enviarComando(mensaje)
            
            for tablero in self.listaTableros:
                self.estadoDelTablero = []
                for boton in tablero.casillas:
                    if boton.disparado:
                        self.estadoDelTablero.append([boton.row, boton.col, boton.barco, boton.hundido, boton.disparado])
                    if boton.disparado and boton.barco:
                        boton.hundido = True
                        boton.setStyleSheet("background-color: #000000")
                        self.estadoDelTablero.append([boton.row, boton.col, boton.barco, boton.hundido, boton.disparado])
                        
                mensaje = f"//actualizarTablero {tablero.etNombre.text()} {json.dumps(self.estadoDelTablero)};"
                self.enviarComando(mensaje)
                
    def usoDeHabilidades(self, habilidad):
        """Función para el uso de habilidades. 

        Args:
            habilidad (str): Nombre de la habilidad a ejecutar
        """
        if habilidad == 'Llamado a refuerzos':
            self.tableroPropio.obtenerbarco('Portaaviones')
        elif habilidad == 'Reposicionamiento':
            self.tableroPropio.reposicionamiento()
        elif habilidad == 'Cañon doble':
            self.tiroDobleActivo = True
            QMessageBox.information(self, 'Cañon doble', 'Seleccione un jugador para atacarlo.')
        elif habilidad == 'Ataque Aereo':
            self.tiroCuadrupleActivo = True
            QMessageBox.information(self, 'Ataque Aereo', 'Seleccione un jugador para atacarlo.')

    def evaluarTurno(self):
        """Función para evaluar el turno del jugador. Se evalúa si el turno es del jugador propio o de un jugador enemigo.
        """
        print(f'{Colores.AZUL}LOG INTERFAZ{Colores.RESET}: Evaluando turno')
        if self.turnoActivo:
            self.zonaHabilidades.alternarHabilidades(True)
            for tablero in self.contenedorEnemigosH.findChildren(QTableros):
                for i in range(tablero.cuadricula.count()):
                    boton = tablero.cuadricula.itemAt(i).widget()
                    boton.setStyleSheet('background-color: #80ff80')
                    boton.clicked.connect(lambda _, coordenadas=[boton.row, boton.col]:tablero.disparoOrdinario(coordenadas))
                    boton.clicked.connect(self.finalizarTurno)
        
    def finalizarTurno(self):
        """Función para finalizar el turno del jugador. Se evalúa si el turno es del jugador propio o de un jugador enemigo.
        """
        for tablero in self.listaTableros:
            tablero.alternarTablero(False)
            for i in range(tablero.cuadricula.count()):
                boton = tablero.casillas[i]
                if boton.disparado:
                    boton.setStyleSheet('background-color: #B22222')
                else:
                    boton.setStyleSheet('background-color: #85C1E9')
        self.enviarComando(f'//turno {self.nombreUsuario};')
        self.enviar_tablero()
        print(f'{Colores.AZUL}LOG INTERFAZ{Colores.RESET}: Turno finalizado')

    def eleccionFinalizada(self):
        """Función para finalizar la elección de barcos. Se envía un comando al servidor para que este lo reenvíe a los clientes y se finalice la elección de barcos.
        """
        self.enviarComando(f'//eleccionFinalizada {self.nombreUsuario};')
        self.tableroPropio.alternarTablero(False)
        self.zonaHabilidades.alternarHabilidades(False)
        self.chat.chat_texto.appendPlainText('<span style="color: #45a5f5;">Esperando a que los demás jugadores elijan sus barcos...</span>')

    def enviarComando(self, comando):
        """Función para enviar comandos al servidor. Se envía un comando al servidor para que este lo reenvíe a los clientes.

        Args:
            comando (str): Comando a enviar
        """
        self.cliente.escribir(comando)
        
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
        
        if self.parent().turnoActivo:
            self.parent().turnoActivo = None
            tablero.alternarTablero(True)
            for i in range(tablero.cuadricula.count()):
                boton = tablero.cuadricula.itemAt(i).widget()
                boton.setStyleSheet('background-color: #80ff80')
                boton.clicked.connect(lambda _, coordenadas=[boton.row, boton.col]:tablero.disparoOrdinario(coordenadas))
                boton.clicked.connect(lambda: print(f'{Colores.CYAN}LOG ACCION{Colores.RESET}: DISPARO ORDINARIO'))
                boton.clicked.connect(self.parent().finalizarTurno)
                boton.clicked.connect(self.cerrarDialogo)
                
        if self.parent().tiroDobleActivo:
            self.parent().tiroDobleActivo = None
            tablero.alternarTablero(True)
            for i in range(tablero.cuadricula.count()):
                boton = tablero.cuadricula.itemAt(i).widget()
                boton.setStyleSheet('background-color: #80ff80')
                boton.clicked.connect(lambda _, coordenadas=[boton.row, boton.col]:tablero.tiroDoble(coordenadas))
                boton.clicked.connect(lambda: print(f'{Colores.CYAN}LOG ACCION{Colores.RESET}: DISPARO DOBLE'))
                boton.clicked.connect(self.parent().finalizarTurno)
                boton.clicked.connect(self.cerrarDialogo)
                
        elif self.parent().tiroCuadrupleActivo:
            self.parent().tiroCuadrupleActivo = None
            tablero.alternarTablero(True)
            for i in range(tablero.cuadricula.count()):
                boton = tablero.cuadricula.itemAt(i).widget()
                boton.setStyleSheet('background-color: #80ff80')
                boton.clicked.connect(lambda _, coordenadas=[boton.row, boton.col]:tablero.tiroCuadruple(coordenadas))
                boton.clicked.connect(lambda: print(f'{Colores.CYAN}LOG ACCION{Colores.RESET}: DISPARO CUADRUPLE'))
                boton.clicked.connect(self.parent().finalizarTurno)
                boton.clicked.connect(self.cerrarDialogo)

    # Cerrar el tablero en grande
    def cerrarDialogo(self):
        """Función para cerrar el tablero en grande y volver al juego
        """
        self.close()
        self.parent().layouta.insertWidget(0, self.tablero)
        self.parent().ventana_tablero_abierta = None

if __name__ == "__main__":
    ip = obtener_ip()
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())

# TODO:
# - Configurar los tableros para recibirlos y configurar los Hits y Misses
# - Configurar el uso de habilidades 4/9
# - Administrar excepciones y errores

# TODO:
# - Testear el juego para evitar bugs.

# - RESOLVER RECEPCIÓN DE COMANDOS EN FUNCION PROCESAR MENSAJES
import json
import random
import sys
import time
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
        
        self.servidor.servidorIniciado.connect(self.procesarMensaje)
        self.servidor.jugadorConectado.connect(self.jugadorEntrante)
        self.servidor.jugadorCaido.connect(self.eliminarJugador)
        # self.servidor.listaDeJugadores.connect(self.generarNuevosJugadores)

        # Barra de herramientas
        toolbar = self.addToolBar('Conexión')
        
        self.btnConectar = toolbar.addAction('Conectar', self.conectar)

        self.btnIniciarServidor = toolbar.addAction('Iniciar Servidor', self.iniciarServidor)

        self.btnCerrarServidor = toolbar.addAction('Cerrar servidor', self.cerrarServidor)
        self.btnCerrarServidor.setEnabled(False)

        self.btnIniciarJuego = toolbar.addAction('Iniciar Juego', self.iniciarJuego)
        self.btnIniciarJuego.setEnabled(False)
        
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
        """Inicializa la lista vacía para que al iniciar el juego. Se construya la misma
        con los jugadores que se conecten al servidor.
        """
        # Creación de los jugadores en un diccionario
        for player in self.jugadoresLista:
            jugadoraIngresar = QJugador(player, None, QTableros(None, False))
            self.diccionarioDeJugadores[player] = jugadoraIngresar
            
    def eliminarJugador(self, jugador):
        self.jugadoresLista.remove(jugador)
        self.diccionarioDeJugadores.pop(jugador)
        self.crearEtiquetasDeJugadores()        
            
    def eliminar_widgets(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()

    def crearEtiquetasDeJugadores(self):
        self.eliminar_widgets(self.contenedorJugadores)
        coloresNombres =  ["#1a1a1a", "#333333", "#4c4c4c", "#666666", "#808080", "#999999", "#b3b3b3", "#cccccc", "#666699", "#996666", "#666633", "#669966", "#6666cc", "#993366", "#cc6666"]
        for nombre in self.jugadoresLista:
            nuevoJugador = QLabel(nombre)
            nuevoJugador.setStyleSheet('font-size: 20px')
            nuevoJugador.setStyleSheet(f'font: Consolas; font-size: 40px; color: {random.choice(coloresNombres)};')
            if nombre == self.nombreUsuario:
                nuevoJugador.setStyleSheet('background-color: #feeabe;')
            self.contenedorJugadores.addWidget(nuevoJugador)

    def jugadorEntrante(self, jugador):
        self.jugadoresLista.append(jugador)
        self.diccionarioDeJugadores[jugador] = QJugador(jugador, None, QTableros(None, False))
        self.crearEtiquetasDeJugadores()

    def actualizarTablerodeJugadores(self):
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
        if self.ventana_tablero_abierta is None:
            ventana_tablero = TableroEnGrande(self, tablero)
            self.ventana_tablero_abierta = ventana_tablero
            ventana_tablero.exec()

    def procesarMensaje(self, mensaje):
        """
        Procesa mensajes recibidos, incluyendo comandos especiales.
        """
        # Verificar si el mensaje es un comando especial
        mensaje = mensaje.strip()
        if mensaje.startswith('//') or mensaje.startswith('"//'):
            comando = mensaje[2:]
            self.procesar_comando(comando)
        else:
            print(mensaje)
            self.chat.chat_texto.appendPlainText(mensaje)

    def procesar_comando(self, comando):
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
            

    def conectar(self):
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
        self.chat.chat_escritura.returnPressed.connect(lambda: self.cliente.escribir(self.chat.chat_escritura.text()))
        self.chat.setEnabled(True)
        
    def construirJuego(self):
        if self.juegoIniciado:
            return
        if self.jugadoresLista == []:
            self.jugadoresLista = self.cliente.jugadoresLista
        self.actualizarTablerodeJugadores()
        self.zonaHabilidades.generarHabilidades()
        self.servidor.flag_aceptar_clientes = False
        self.juegoIniciado = True

    def iniciarJuego(self):
        if not self.juegoIniciado:
            lista_json = json.dumps(self.jugadoresLista)
            self.cliente.escribir(f'//iniciarJuego {lista_json}')
            self.btnIniciarJuego.setEnabled(False)
            self.crearEtiquetasDeJugadores()
            self.construirJuego()

    def cerrarServidor(self):
        self.servidor.server.close()
        self.btnIniciarServidor.setEnabled(True)
        self.btnIniciarJuego.setEnabled(False)
        self.btnConectar.setEnabled(True)
        self.procesarMensaje(f'Servidor cerrado')
        self.barraEstado.showMessage(f'¡Bienvenido {self.nombreUsuario}!')

    def recibirTableros(self):
        pass
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
    ip = obtener_ip()
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())
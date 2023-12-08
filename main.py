#main.py
import sys
from PyQt5.QtWidgets import QApplication
from InterfazP import InterfazPrincipal

cña

def main():
    app = QApplication(sys.argv)
    window = InterfazPrincipal()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
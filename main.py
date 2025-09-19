import sys
from PyQt5.QtWidgets import QApplication
from interfaz import GestorArticulosWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestorArticulosWindow()
    ventana.show()
    sys.exit(app.exec_())

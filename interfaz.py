import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QInputDialog, QDesktopWidget,
    QPlainTextEdit
)
from PyQt5.QtCore import Qt

from modelo import Articulo, TablaHashArticulos, BaseDatosArticulos, fnv1_64

class GestorArticulosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Artículos Científicos")
        self.setGeometry(100, 100, 900, 600)
        self.center()  # Centrar ventana

        self.base_datos = BaseDatosArticulos()
        self.tabla_hash = self.base_datos.cargar()

        self.initUI()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        form_layout = QHBoxLayout()

        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Título")
        form_layout.addWidget(self.input_titulo)

        self.input_autores = QLineEdit()
        self.input_autores.setPlaceholderText("Autor(es) separados por coma")
        form_layout.addWidget(self.input_autores)

        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("Año de publicación")
        form_layout.addWidget(self.input_anio)

        self.btn_seleccionar_archivo = QPushButton("Seleccionar archivo .txt")
        self.btn_seleccionar_archivo.clicked.connect(self.seleccionar_archivo)
        form_layout.addWidget(self.btn_seleccionar_archivo)

        self.btn_agregar = QPushButton("Agregar Artículo")
        self.btn_agregar.clicked.connect(self.agregar_articulo)
        form_layout.addWidget(self.btn_agregar)

        layout.addLayout(form_layout)

        self.tabla_articulos = QTableWidget(0, 5)
        self.tabla_articulos.setHorizontalHeaderLabels(["Hash", "Título", "Autor(es)", "Año", "Archivo"])
        self.tabla_articulos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_articulos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_articulos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_articulos)

        acciones_layout = QHBoxLayout()

        self.btn_modificar = QPushButton("Modificar Autor/Año")
        self.btn_modificar.clicked.connect(self.modificar_articulo)
        acciones_layout.addWidget(self.btn_modificar)

        self.btn_eliminar = QPushButton("Eliminar Artículo")
        self.btn_eliminar.clicked.connect(self.eliminar_articulo)
        acciones_layout.addWidget(self.btn_eliminar)

        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Listar todos", "Filtrar por autor", "Filtrar por año"])
        self.combo_filtro.currentIndexChanged.connect(self.actualizar_filtro)
        acciones_layout.addWidget(self.combo_filtro)

        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Ingrese autor o año")
        self.input_filtro.textChanged.connect(self.actualizar_filtro)
        self.input_filtro.setEnabled(False)
        acciones_layout.addWidget(self.input_filtro)

        layout.addLayout(acciones_layout)

        # Vista previa del contenido del archivo seleccionado
        self.vista_previa = QPlainTextEdit()
        self.vista_previa.setReadOnly(True)
        self.vista_previa.setPlaceholderText("Vista previa del contenido del archivo seleccionado...")
        layout.addWidget(self.vista_previa)

        self.archivo_seleccionado = None

        self.cargar_tabla()
        self.aplicar_estilos_botones()

    def aplicar_estilos_botones(self):
        estilo = """
            QPushButton {
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 10px;
                border: 2px solid #555;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #66e, stop:1 #44a);
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #88f, stop:1 #66c);
            }
            QPushButton:pressed {
                background-color: #224488;
            }
        """
        botones = [
            self.btn_seleccionar_archivo,
            self.btn_agregar,
            self.btn_modificar,
            self.btn_eliminar
        ]
        for btn in botones:
            btn.setStyleSheet(estilo)

    def seleccionar_archivo(self):
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de artículo",
            "",
            "Archivos de texto (*.txt);;Todos los archivos (*)",
            options=opciones
        )
        if archivo:
            self.archivo_seleccionado = archivo
            self.btn_seleccionar_archivo.setText(os.path.basename(archivo))
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.vista_previa.setPlainText(contenido)
            except Exception as e:
                self.vista_previa.setPlainText(f"No se pudo cargar el archivo:\n{str(e)}")

    def agregar_articulo(self):
        titulo = self.input_titulo.text().strip()
        autores = self.input_autores.text().strip()
        anio = self.input_anio.text().strip()
        archivo = self.archivo_seleccionado

        if not (titulo and autores and anio and archivo):
            QMessageBox.warning(self, "Error", "Complete todos los campos y seleccione un archivo.")
            return

        if not anio.isdigit():
            QMessageBox.warning(self, "Error", "El año debe ser un número válido.")
            return

        try:
            with open(archivo, 'rb') as f:
                contenido = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo leer el archivo: {str(e)}")
            return

        hash_id = fnv1_64(contenido)

        if self.tabla_hash.buscar_por_hash(hash_id):
            QMessageBox.information(self, "Duplicado", "El artículo ya está almacenado.")
            return

        nombre_archivo_guardado = f"{hash_id}.txt"
        try:
            with open(nombre_archivo_guardado, 'wb') as f:
                f.write(contenido)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
            return

        articulo = Articulo(hash_id, titulo, autores, anio, nombre_archivo_guardado)
        self.tabla_hash.agregar_articulo(articulo)
        self.base_datos.guardar(self.tabla_hash)

        QMessageBox.information(self, "Éxito", "Artículo agregado correctamente.")
        self.limpiar_formulario()
        self.cargar_tabla()

    def limpiar_formulario(self):
        self.input_titulo.clear()
        self.input_autores.clear()
        self.input_anio.clear()
        self.archivo_seleccionado = None
        self.btn_seleccionar_archivo.setText("Seleccionar archivo .txt")
        self.vista_previa.clear()

    def cargar_tabla(self, articulos=None):
        if articulos is None:
            articulos = self.tabla_hash.listar_todos()
        self.tabla_articulos.setRowCount(0)
        for articulo in sorted(articulos, key=lambda x: x.titulo.lower()):
            fila = self.tabla_articulos.rowCount()
            self.tabla_articulos.insertRow(fila)
            self.tabla_articulos.setItem(fila, 0, QTableWidgetItem(articulo.hash_id))
            self.tabla_articulos.setItem(fila, 1, QTableWidgetItem(articulo.titulo))
            self.tabla_articulos.setItem(fila, 2, QTableWidgetItem(articulo.autores))
            self.tabla_articulos.setItem(fila, 3, QTableWidgetItem(articulo.anio))
            self.tabla_articulos.setItem(fila, 4, QTableWidgetItem(articulo.nombre_archivo))

    def modificar_articulo(self):
        filas = self.tabla_articulos.selectionModel().selectedRows()
        if not filas:
            QMessageBox.warning(self, "Error", "Seleccione un artículo para modificar.")
            return
        fila = filas[0].row()
        hash_id = self.tabla_articulos.item(fila, 0).text()
        articulo = self.tabla_hash.buscar_por_hash(hash_id)
        if not articulo:
            QMessageBox.warning(self, "Error", "Artículo no encontrado.")
            return

        nuevo_autores, ok1 = QInputDialog.getText(
            self, "Modificar Autor(es)", "Ingrese nuevo autor(es):", QLineEdit.Normal, articulo.autores
        )
        if not ok1:
            return
        nuevo_anio, ok2 = QInputDialog.getText(
            self, "Modificar Año", "Ingrese nuevo año:", QLineEdit.Normal, articulo.anio
        )
        if not ok2:
            return
        if nuevo_anio and not nuevo_anio.isdigit():
            QMessageBox.warning(self, "Error", "El año debe ser un número válido.")
            return

        modificado = self.tabla_hash.modificar_articulo(
            hash_id, nuevos_autores=nuevo_autores.strip(), nuevo_anio=nuevo_anio.strip()
        )
        if modificado:
            self.base_datos.guardar(self.tabla_hash)
            QMessageBox.information(self, "Éxito", "Artículo modificado correctamente.")
            self.cargar_tabla()
        else:
            QMessageBox.warning(self, "Error", "No se pudo modificar el artículo.")

    def eliminar_articulo(self):
        filas = self.tabla_articulos.selectionModel().selectedRows()
        if not filas:
            QMessageBox.warning(self, "Error", "Seleccione un artículo para eliminar.")
            return
        fila = filas[0].row()
        hash_id = self.tabla_articulos.item(fila, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar el artículo seleccionado?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        eliminado = self.tabla_hash.eliminar_articulo(hash_id)
        if eliminado:
            self.base_datos.guardar(self.tabla_hash)
            QMessageBox.information(self, "Éxito", "Artículo eliminado correctamente.")
            self.cargar_tabla()
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar el artículo.")

    def actualizar_filtro(self):
        opcion = self.combo_filtro.currentText()
        texto = self.input_filtro.text().strip()
        if opcion == "Listar todos":
            self.input_filtro.setEnabled(False)
            self.cargar_tabla()
        elif opcion == "Filtrar por autor":
            self.input_filtro.setEnabled(True)
            if texto:
                articulos = self.tabla_hash.listar_por_autor(texto)
                self.cargar_tabla(articulos)
            else:
                self.cargar_tabla([])
        elif opcion == "Filtrar por año":
            self.input_filtro.setEnabled(True)
            if texto and texto.isdigit():
                articulos = self.tabla_hash.listar_por_anio(texto)
                self.cargar_tabla(articulos)
            else:
                self.cargar_tabla([])

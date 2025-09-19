# Gestor de Artículos Científicos con PyQt y Tablas Hash

## Descripción

Este proyecto es una aplicación de escritorio desarrollada en Python con PyQt que permite gestionar artículos científicos en formato de texto plano (.txt). Utiliza tablas hash con encadenamiento para almacenar y acceder eficientemente a los artículos en memoria, y sincroniza los datos con un archivo de base de datos persistente.

La aplicación facilita la carga, almacenamiento, verificación de duplicados, consulta, edición y eliminación de artículos científicos, además de ofrecer índices secundarios para búsquedas rápidas por autor y año.

---

## Características principales

- **Interfaz gráfica moderna y amigable** desarrollada con PyQt5.
- **Carga de artículos** con metadatos: título, autor(es), año de publicación y contenido desde archivo `.txt`.
- **Identificación única mediante hash FNV-1 64 bits** calculado sobre el contenido del artículo.
- **Almacenamiento eficiente en memoria** usando tablas hash con encadenamiento para evitar colisiones.
- **Base de datos persistente** en archivo `articulos_db.txt` que se sincroniza automáticamente.
- **Detección rápida de duplicados** mediante hash sin necesidad de recorrer toda la base.
- **Índices secundarios** para búsquedas rápidas por autor y año.
- **Operaciones de gestión**: modificar autor o año, eliminar artículos (registro y archivo asociado).
- **Listados ordenados** y filtrados por autor o año.
- **Ventana centrada y botones con diseño llamativo** para mejor experiencia de usuario.

---

## Requisitos

- Python 3.7 o superior
- PyQt5

Puedes instalar PyQt5 con pip:

```bash
pip install PyQt5
---

### Bloque 3: Cómo funciona internamente

```markdown
## Cómo funciona internamente

- Al agregar un artículo, se calcula un hash único del contenido usando FNV-1 64 bits.
- El artículo se guarda en un archivo con nombre `<hash>.txt`.
- Se almacena un registro en memoria en una tabla hash para acceso rápido.
- Los índices secundarios permiten búsquedas eficientes por autor y año.
- Al cerrar o modificar, la base de datos se sincroniza con el archivo `articulos_db.txt`.
## Contribuciones

Las contribuciones son bienvenidas. Puedes abrir issues o pull requests para mejorar la aplicación.

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

---

## Autor

Tu Nombre - [Tu GitHub](https://github.com/tu_usuario)

---

¡Gracias por usar el Gestor de Artículos Científicos!

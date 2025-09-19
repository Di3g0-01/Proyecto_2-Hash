import os

class Articulo:
    def __init__(self, hash_id, titulo, autores, anio, nombre_archivo):
        self.hash_id = hash_id
        self.titulo = titulo
        self.autores = autores
        self.anio = anio
        self.nombre_archivo = nombre_archivo
        self.siguiente = None

class TablaHashArticulos:
    def __init__(self, tamano=100):
        self.tamano = tamano
        self.tabla = [None] * tamano
        self.indice_autor = {}
        self.indice_anio = {}

    def fnv1_32(self, clave):
        FNV_prime = 16777619
        offset_basis = 2166136261
        hash = offset_basis
        for c in clave:
            hash = hash * FNV_prime
            hash = hash ^ ord(c)
            hash = hash & 0xffffffff
        return hash

    def hash_function(self, hash_id):
        return int(hash_id, 16) % self.tamano if isinstance(hash_id, str) else hash_id % self.tamano

    def agregar_articulo(self, articulo):
        pos = self.hash_function(articulo.hash_id)
        nodo_actual = self.tabla[pos]
        while nodo_actual:
            if nodo_actual.hash_id == articulo.hash_id:
                return False
            nodo_actual = nodo_actual.siguiente
        articulo.siguiente = self.tabla[pos]
        self.tabla[pos] = articulo
        for autor in [a.strip().lower() for a in articulo.autores.split(',')]:
            self.indice_autor.setdefault(autor, set()).add(articulo.hash_id)
        self.indice_anio.setdefault(articulo.anio, set()).add(articulo.hash_id)
        return True

    def buscar_por_hash(self, hash_id):
        pos = self.hash_function(hash_id)
        nodo_actual = self.tabla[pos]
        while nodo_actual:
            if nodo_actual.hash_id == hash_id:
                return nodo_actual
            nodo_actual = nodo_actual.siguiente
        return None

    def modificar_articulo(self, hash_id, nuevos_autores=None, nuevo_anio=None):
        articulo = self.buscar_por_hash(hash_id)
        if not articulo:
            return False
        if nuevos_autores is not None and nuevos_autores != articulo.autores:
            for autor in [a.strip().lower() for a in articulo.autores.split(',')]:
                if autor in self.indice_autor:
                    self.indice_autor[autor].discard(hash_id)
                    if not self.indice_autor[autor]:
                        del self.indice_autor[autor]
            for autor in [a.strip().lower() for a in nuevos_autores.split(',')]:
                self.indice_autor.setdefault(autor, set()).add(hash_id)
            articulo.autores = nuevos_autores
        if nuevo_anio is not None and nuevo_anio != articulo.anio:
            if articulo.anio in self.indice_anio:
                self.indice_anio[articulo.anio].discard(hash_id)
                if not self.indice_anio[articulo.anio]:
                    del self.indice_anio[articulo.anio]
            self.indice_anio.setdefault(nuevo_anio, set()).add(hash_id)
            articulo.anio = nuevo_anio
        return True

    def eliminar_articulo(self, hash_id):
        pos = self.hash_function(hash_id)
        nodo_actual = self.tabla[pos]
        prev = None
        while nodo_actual:
            if nodo_actual.hash_id == hash_id:
                if prev is None:
                    self.tabla[pos] = nodo_actual.siguiente
                else:
                    prev.siguiente = nodo_actual.siguiente
                for autor in [a.strip().lower() for a in nodo_actual.autores.split(',')]:
                    if autor in self.indice_autor:
                        self.indice_autor[autor].discard(hash_id)
                        if not self.indice_autor[autor]:
                            del self.indice_autor[autor]
                if nodo_actual.anio in self.indice_anio:
                    self.indice_anio[nodo_actual.anio].discard(hash_id)
                    if not self.indice_anio[nodo_actual.anio]:
                        del self.indice_anio[nodo_actual.anio]
                if os.path.exists(nodo_actual.nombre_archivo):
                    os.remove(nodo_actual.nombre_archivo)
                return True
            prev = nodo_actual
            nodo_actual = nodo_actual.siguiente
        return False

    def listar_todos(self):
        articulos = []
        for pos in range(self.tamano):
            nodo_actual = self.tabla[pos]
            while nodo_actual:
                articulos.append(nodo_actual)
                nodo_actual = nodo_actual.siguiente
        return articulos

    def listar_por_autor(self, autor):
        autor = autor.strip().lower()
        if autor not in self.indice_autor:
            return []
        return [self.buscar_por_hash(h) for h in self.indice_autor[autor]]

    def listar_por_anio(self, anio):
        if anio not in self.indice_anio:
            return []
        return [self.buscar_por_hash(h) for h in self.indice_anio[anio]]

class BaseDatosArticulos:
    def __init__(self, archivo_db='articulos_db.txt'):
        self.archivo_db = archivo_db

    def cargar(self):
        tabla = TablaHashArticulos()
        if not os.path.exists(self.archivo_db):
            return tabla
        with open(self.archivo_db, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split('|')
                if len(partes) != 5:
                    continue
                hash_id, titulo, autores, anio, nombre_archivo = partes
                articulo = Articulo(hash_id, titulo, autores, anio, nombre_archivo)
                tabla.agregar_articulo(articulo)
        return tabla

    def guardar(self, tabla):
        with open(self.archivo_db, 'w', encoding='utf-8') as f:
            for articulo in tabla.listar_todos():
                linea = '|'.join([articulo.hash_id, articulo.titulo, articulo.autores, articulo.anio, articulo.nombre_archivo])
                f.write(linea + '\n')

def fnv1_64(data):
    FNV_prime = 1099511628211
    offset_basis = 14695981039346656037
    hash = offset_basis
    for b in data:
        hash = hash * FNV_prime
        hash = hash ^ b
        hash = hash & 0xffffffffffffffff
    return format(hash, '016x')

"""
database/db_manager.py
-------------------------
Gestiona la persistencia del historial de análisis en SQLite:
inserción, búsqueda y borrado de registros.
"""

import sqlite3
import os
import json
from utils.logger import get_logger
from utils.paths import app_base_dir

logger = get_logger(__name__)

BASE_DIR = app_base_dir()
DB_DIR = os.path.join(BASE_DIR, "database")
DB_FILE = os.path.join(DB_DIR, "history.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    url TEXT NOT NULL,
    ip TEXT,
    puntaje INTEGER,
    nivel TEXT,
    pais TEXT,
    estado_http INTEGER,
    detalle_json TEXT
);
"""


class DBManager:
    """Encapsula todas las operaciones sobre la base de datos de historial."""

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(DB_FILE)

    def _init_db(self):
        try:
            with self._connect() as conn:
                conn.execute(SCHEMA)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"No se pudo inicializar la base de datos: {e}")

    def insert_record(self, fecha, hora, url, ip, puntaje, nivel, pais, estado_http, detalle: dict):
        """Inserta un nuevo registro de análisis en el historial."""
        try:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO history
                       (fecha, hora, url, ip, puntaje, nivel, pais, estado_http, detalle_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (fecha, hora, url, ip, puntaje, nivel, pais, estado_http,
                     json.dumps(detalle, ensure_ascii=False)),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error insertando registro en historial: {e}")

    def get_all(self, limit: int = 500):
        """Devuelve todos los registros, más recientes primero."""
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
                )
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error leyendo historial: {e}")
            return []

    def search(self, keyword: str):
        """Busca registros cuya URL, IP o país contengan la palabra clave."""
        like = f"%{keyword}%"
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    """SELECT * FROM history
                       WHERE url LIKE ? OR ip LIKE ? OR pais LIKE ?
                       ORDER BY id DESC""",
                    (like, like, like),
                )
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error buscando en historial: {e}")
            return []

    def delete_record(self, record_id: int):
        """Elimina un registro específico por su id."""
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error eliminando registro {record_id}: {e}")

    def clear_all(self):
        """Elimina todos los registros del historial."""
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM history")
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error limpiando historial: {e}")

    def get_detail(self, record_id: int):
        """Devuelve el detalle completo (JSON deserializado) de un registro."""
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT detalle_json FROM history WHERE id = ?", (record_id,)
                )
                row = cur.fetchone()
                if row and row["detalle_json"]:
                    return json.loads(row["detalle_json"])
                return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Error leyendo detalle de registro {record_id}: {e}")
            return None


# Instancia única compartida por toda la app
db = DBManager()

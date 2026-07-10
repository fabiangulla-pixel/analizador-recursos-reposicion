"""
main.py
Punto de entrada de la aplicación.
Añade el directorio raíz al sys.path para que los imports funcionen
tanto en modo desarrollo como empaquetado con PyInstaller.
"""

import os
import sys

# Asegurar que el directorio raíz esté en el path (necesario para PyInstaller)
_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from app.gui import AplicacionRecursos


def main():
    app = AplicacionRecursos()
    app.mainloop()


if __name__ == "__main__":
    main()

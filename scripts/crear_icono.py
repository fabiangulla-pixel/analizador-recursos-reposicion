"""
Genera el ícono .ico de la aplicación usando solo la librería estándar (tkinter + PIL si está).
Diseño: escudo/carpeta jurídica con letras "RR" (Recursos de Reposición).
"""

from PIL import Image, ImageDraw, ImageFont
import os

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icono.ico")

def crear_icono():
    sizes = [256, 128, 64, 48, 32, 16]
    imagenes = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # ── Fondo: escudo redondeado ──────────────────────────────────────
        margen = size // 12
        # Sombra suave
        draw.rounded_rectangle(
            [margen + 2, margen + 2, size - margen + 2, size - margen + 2],
            radius=size // 6,
            fill=(0, 0, 0, 60),
        )
        # Gradiente simulado con dos rectángulos
        draw.rounded_rectangle(
            [margen, margen, size - margen, size - margen],
            radius=size // 6,
            fill=(30, 80, 140),       # azul oscuro
        )
        draw.rounded_rectangle(
            [margen + size//20, margen + size//20,
             size - margen - size//20, size - margen - size//20],
            radius=size // 7,
            fill=(44, 95, 138),       # azul medio
        )

        # ── Línea superior dorada ─────────────────────────────────────────
        borde_y = margen + size // 8
        draw.rectangle(
            [margen + size//10, borde_y,
             size - margen - size//10, borde_y + max(2, size//32)],
            fill=(212, 175, 55),
        )

        # ── Texto "RR" ────────────────────────────────────────────────────
        if size >= 48:
            font_size = int(size * 0.38)
            try:
                font = ImageFont.truetype("arialbd.ttf", font_size)
            except Exception:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

            texto = "RR"
            bbox = draw.textbbox((0, 0), texto, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (size - tw) // 2 - bbox[0]
            ty = (size - th) // 2 - bbox[1] + size // 18

            # Sombra del texto
            draw.text((tx + max(1, size//64), ty + max(1, size//64)),
                      texto, font=font, fill=(0, 0, 0, 120))
            # Texto blanco
            draw.text((tx, ty), texto, font=font, fill=(255, 255, 255, 255))

        # ── Línea inferior dorada ─────────────────────────────────────────
        borde_y2 = size - margen - size // 8 - max(2, size//32)
        draw.rectangle(
            [margen + size//10, borde_y2,
             size - margen - size//10, borde_y2 + max(2, size//32)],
            fill=(212, 175, 55),
        )

        imagenes.append(img)

    # Guardar como .ico con todos los tamaños
    imagenes[0].save(
        RUTA,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=imagenes[1:],
    )
    print(f"Ícono creado: {RUTA}")

if __name__ == "__main__":
    crear_icono()

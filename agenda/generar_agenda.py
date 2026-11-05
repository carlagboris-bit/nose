"""
Agenda semanal digital (PDF con enlaces) para GoodNotes.
Colores pastel, pestañas laterales por mes, vista anual, mensual, semanal y notas.

Uso:  python3 generar_agenda.py            -> Agenda_Pastel_2026-2027.pdf
Cambia INICIO / FIN abajo para otro periodo.
"""
import calendar
import datetime as dt
import os

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color

# ------------------------------------------------------------------ ajustes
INICIO = (2026, 11)   # año, mes
FIN = (2027, 12)
NUM_NOTAS = 6
SALIDA = "Agenda_Pastel_2026-2027.pdf"

W, H = 1024, 768      # proporción iPad 4:3 en horizontal
HERE = os.path.dirname(os.path.abspath(__file__))

for name, file in [("Q", "Quicksand-Regular.ttf"), ("QB", "Quicksand-Bold.ttf"),
                   ("Serif", "Playfair-Italic.ttf"), ("Script", "Dancing.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", file)))

PAPEL = HexColor("#FFFBF6")
TINTA = HexColor("#5E4E55")
SUAVE = HexColor("#A3949A")
LINEA = HexColor("#EDE3DC")
BLANCO = HexColor("#FFFFFF")

# un pastel por mes (ene..dic)
PASTEL = ["#C8DDF0", "#F6C6CF", "#CDE8D5", "#E3CCEB", "#F6E7B0", "#F9D5BB",
          "#C4E6E3", "#F8C8BC", "#D6E2C4", "#F3D6AE", "#DCD2F0", "#EFC1C8"]
PASTEL = [HexColor(c) for c in PASTEL]

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
INI = ["L", "M", "X", "J", "V", "S", "D"]


def oscuro(c, k=0.45):
    """Versión más oscura del pastel (mezcla con la tinta) para textos."""
    return Color(c.red * (1 - k) + TINTA.red * k,
                 c.green * (1 - k) + TINTA.green * k,
                 c.blue * (1 - k) + TINTA.blue * k)


def claro(c, k=0.6):
    return Color(c.red + (1 - c.red) * k, c.green + (1 - c.green) * k,
                 c.blue + (1 - c.blue) * k)


# ------------------------------------------------------------------ fechas
def meses():
    y, m = INICIO
    while (y, m) <= FIN:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


MESES_LISTA = list(meses())


def lunes(d):
    return d - dt.timedelta(days=d.weekday())


PRIMER_LUNES = lunes(dt.date(*INICIO, 1))
ULT_DIA = dt.date(FIN[0], FIN[1], calendar.monthrange(*FIN)[1])
SEMANAS = []
d = PRIMER_LUNES
while d <= ULT_DIA:
    SEMANAS.append(d)
    d += dt.timedelta(days=7)


def dest_mes(y, m):
    return f"m-{y}-{m:02d}"


def dest_sem(lun):
    return f"w-{lun.isoformat()}"


def semanas_de_mes(y, m):
    primero = dt.date(y, m, 1)
    ultimo = dt.date(y, m, calendar.monthrange(y, m)[1])
    return [s for s in SEMANAS if s <= ultimo and s + dt.timedelta(days=6) >= primero]


def mes_de_semana(lun):
    """Mes al que 'pertenece' una semana (para la pestaña activa y el orden)."""
    jueves = lun + dt.timedelta(days=3)
    ym = (jueves.year, jueves.month)
    if ym < MESES_LISTA[0]:
        return MESES_LISTA[0]
    if ym > MESES_LISTA[-1]:
        return MESES_LISTA[-1]
    return ym


def fecha_corta(d):
    return f"{d.day} {MESES[d.month - 1][:3].lower()}"


# ------------------------------------------------------------------ dibujo
class Agenda:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(W, H))
        self.c.setTitle("Agenda pastel")
        self.c.setAuthor("Agenda digital")

    # utilidades -----------------------------------------------------------
    def link(self, dest, x, y, w, h):
        self.c.linkAbsolute("", dest, (x, y, x + w, y + h), thickness=0)

    def rrect(self, x, y, w, h, r, fill=None, stroke=None, lw=1):
        c = self.c
        c.setLineWidth(lw)
        if fill is not None:
            c.setFillColor(fill)
        if stroke is not None:
            c.setStrokeColor(stroke)
        c.roundRect(x, y, w, h, r, stroke=1 if stroke is not None else 0,
                    fill=1 if fill is not None else 0)

    def texto(self, s, x, y, font="Q", size=11, color=TINTA, align="l"):
        c = self.c
        c.setFont(font, size)
        c.setFillColor(color)
        if align == "c":
            c.drawCentredString(x, y, s)
        elif align == "r":
            c.drawRightString(x, y, s)
        else:
            c.drawString(x, y, s)

    def corazon(self, x, y, s, color):
        c = self.c
        p = c.beginPath()
        p.moveTo(x, y)
        p.curveTo(x - s * 1.1, y + s * 0.6, x - s * 0.55, y + s * 1.45, x, y + s * 0.95)
        p.curveTo(x + s * 0.55, y + s * 1.45, x + s * 1.1, y + s * 0.6, x, y)
        p.close()
        c.setFillColor(color)
        c.drawPath(p, stroke=0, fill=1)

    def destello(self, x, y, s, color):
        c = self.c
        p = c.beginPath()
        p.moveTo(x, y + s)
        p.curveTo(x + s * .15, y + s * .15, x + s * .15, y + s * .15, x + s, y)
        p.curveTo(x + s * .15, y - s * .15, x + s * .15, y - s * .15, x, y - s)
        p.curveTo(x - s * .15, y - s * .15, x - s * .15, y - s * .15, x - s, y)
        p.curveTo(x - s * .15, y + s * .15, x - s * .15, y + s * .15, x, y + s)
        p.close()
        c.setFillColor(color)
        c.drawPath(p, stroke=0, fill=1)

    def lineas(self, x, y_top, w, y_bottom, paso=22, color=LINEA, punteado=False):
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(0.8)
        if punteado:
            c.setDash(1, 4)
        yy = y_top - paso
        while yy > y_bottom + 4:
            c.line(x, yy, x + w, yy)
            yy -= paso
        c.setDash()

    def check(self, x, y, color):
        self.rrect(x, y, 9, 9, 2.5, stroke=color, lw=1)

    def fondo(self):
        c = self.c
        c.setFillColor(PAPEL)
        c.rect(0, 0, W, H, stroke=0, fill=1)

    # pestañas laterales + navegación superior -----------------------------
    def pestanas(self, activo=None):
        c = self.c
        n = len(MESES_LISTA) + 1
        top, bottom = H - 22, 22
        gap = 4
        th = (top - bottom - gap * (n - 1)) / n
        for i, (y, m) in enumerate(MESES_LISTA):
            col = PASTEL[m - 1]
            ty = top - (i + 1) * th - i * gap
            act = (y, m) == activo
            x0 = W - (60 if act else 48)
            self.rrect(x0, ty, 80, th, 9, fill=col)
            if act:
                self.corazon(x0 + 12, ty + th / 2 - 4, 6, BLANCO)
            c.saveState()
            c.translate(W - 22, ty + th / 2)
            c.rotate(90)
            c.setFont("QB" if act else "Q", 9.5)
            c.setFillColor(oscuro(col, 0.8) if act else oscuro(col, 0.72))
            c.drawCentredString(0, 0, f"{MESES[m - 1][:3].upper()} {str(y)[2:]}")
            c.restoreState()
            self.link(dest_mes(y, m), x0, ty, W - x0, th)
        # pestaña notas
        ty = bottom
        act = activo == "notas"
        x0 = W - (60 if act else 48)
        self.rrect(x0, ty, 80, th, 9, fill=HexColor("#E9E1DA"))
        c.saveState()
        c.translate(W - 22, ty + th / 2)
        c.rotate(90)
        c.setFont("QB" if act else "Q", 9.5)
        c.setFillColor(TINTA)
        c.drawCentredString(0, 0, "NOTAS")
        c.restoreState()
        self.link("notas-1", x0, ty, W - x0, th)

    def nav(self, color):
        """Botones arriba a la derecha: Portada · Año · Notas."""
        x = W - 80
        for etiqueta, dest in [("Notas", "notas-1"), ("Año", "anual"), ("Portada", "portada")]:
            tw = pdfmetrics.stringWidth(etiqueta, "QB", 10) + 22
            x -= tw
            self.rrect(x, H - 50, tw, 22, 11, fill=claro(color, 0.35))
            self.texto(etiqueta, x + tw / 2, H - 43, "QB", 10, oscuro(color, 0.7), "c")
            self.link(dest, x, H - 50, tw, 22)
            x -= 8

    # páginas --------------------------------------------------------------
    def portada(self):
        c = self.c
        self.fondo()
        c.bookmarkPage("portada", fit="Fit")
        c.addOutlineEntry("Portada", "portada", 0)
        # manchas pastel
        for (x, y, r, col) in [(140, 640, 170, PASTEL[1]), (880, 120, 200, PASTEL[2]),
                               (820, 690, 110, PASTEL[4]), (90, 110, 120, PASTEL[3]),
                               (520, 60, 70, PASTEL[0])]:
            c.setFillColor(claro(col, 0.25))
            c.circle(x, y, r, stroke=0, fill=1)
        # tarjeta central
        self.rrect(232, 190, 560, 390, 28, fill=BLANCO)
        self.rrect(244, 202, 536, 366, 22, stroke=PASTEL[1], lw=1.2)
        self.texto("mi agenda", W / 2, 455, "Script", 82, TINTA, "c")
        self.corazon(W / 2 + 175, 500, 11, PASTEL[1])
        self.destello(W / 2 - 190, 505, 12, PASTEL[4])
        self.destello(W / 2 - 165, 480, 6, PASTEL[3])
        a, b = MESES_LISTA[0], MESES_LISTA[-1]
        self.texto(f"{MESES[a[1]-1].lower()} {a[0]}  ·  {MESES[b[1]-1].lower()} {b[0]}",
                   W / 2, 405, "Q", 17, SUAVE, "c")
        self.texto("esta agenda pertenece a", W / 2, 330, "Q", 11, SUAVE, "c")
        c.setStrokeColor(LINEA)
        c.setLineWidth(1)
        c.line(W / 2 - 150, 296, W / 2 + 150, 296)
        # botones
        bx = W / 2 - 160
        for etiqueta, dest, col in [("Vista anual", "anual", PASTEL[0]),
                                    ("Este mes", dest_mes(*MESES_LISTA[0]), PASTEL[1]),
                                    ("Notas", "notas-1", PASTEL[2])]:
            self.rrect(bx, 232, 100, 30, 15, fill=col)
            self.texto(etiqueta, bx + 50, 242, "QB", 11, oscuro(col, 0.8), "c")
            self.link(dest, bx, 232, 100, 30)
            bx += 110
        self.pestanas()
        c.showPage()

    def anual(self):
        c = self.c
        self.fondo()
        c.bookmarkPage("anual", fit="Fit")
        c.addOutlineEntry("Vista anual", "anual", 0)
        self.texto("Vista anual", 40, H - 62, "Serif", 34, TINTA)
        self.corazon(232, H - 52, 8, PASTEL[1])
        self.nav(PASTEL[0])
        cols, rows = 5, 3
        x0, ytop = 40, H - 92
        gw, gh = 20, 18
        cw = (W - 80 - x0 - gw * (cols - 1)) / cols
        ch = (ytop - 28 - gh * (rows - 1)) / rows
        slots = MESES_LISTA + [None] * (cols * rows - len(MESES_LISTA))
        for i, ym in enumerate(slots[:cols * rows]):
            cx = x0 + (i % cols) * (cw + gw)
            cy = ytop - (i // cols + 1) * ch - (i // cols) * gh
            if ym is None:
                self.rrect(cx, cy, cw, ch, 14, fill=BLANCO, stroke=LINEA)
                self.texto("metas del año", cx + 14, cy + ch - 24, "QB", 11, TINTA)
                self.corazon(cx + cw - 20, cy + ch - 24, 5, PASTEL[1])
                for k in range(5):
                    yy = cy + ch - 50 - k * 22
                    self.check(cx + 14, yy, SUAVE)
                    c.setStrokeColor(LINEA)
                    c.line(cx + 30, yy, cx + cw - 14, yy)
                continue
            y, m = ym
            col = PASTEL[m - 1]
            self.rrect(cx, cy, cw, ch, 14, fill=BLANCO, stroke=claro(col, 0.1))
            self.rrect(cx + 8, cy + ch - 30, cw - 16, 22, 11, fill=col)
            self.texto(f"{MESES[m-1]} {y}", cx + cw / 2, cy + ch - 23, "QB", 10.5,
                       oscuro(col, 0.8), "c")
            self.link(dest_mes(y, m), cx + 8, cy + ch - 30, cw - 16, 22)
            dw = (cw - 16) / 7
            for k, l in enumerate(INI):
                self.texto(l, cx + 8 + dw * k + dw / 2, cy + ch - 46, "QB", 7.5, SUAVE, "c")
            semanas = semanas_de_mes(y, m)
            rh = (ch - 58) / 6
            for r, lun in enumerate(semanas):
                for k in range(7):
                    d = lun + dt.timedelta(days=k)
                    if d.month != m:
                        continue
                    tx = cx + 8 + dw * k
                    ty = cy + ch - 52 - (r + 1) * rh
                    self.texto(str(d.day), tx + dw / 2, ty + rh / 2 - 3, "Q", 8.5,
                               TINTA if k < 5 else oscuro(col, 0.5), "c")
                    self.link(dest_sem(lun), tx, ty, dw, rh)
        self.pestanas()
        c.showPage()

    def mensual(self, y, m):
        c = self.c
        col = PASTEL[m - 1]
        self.fondo()
        c.bookmarkPage(dest_mes(y, m), fit="Fit")
        c.addOutlineEntry(f"{MESES[m-1]} {y}", dest_mes(y, m), 0)
        # cabecera
        self.texto(MESES[m - 1], 40, H - 64, "Serif", 40, TINTA)
        tw = pdfmetrics.stringWidth(MESES[m - 1], "Serif", 40)
        self.texto(str(y), 50 + tw, H - 64, "Q", 18, oscuro(col, 0.45))
        self.corazon(50 + tw + 52, H - 56, 7, col)
        self.nav(col)
        # calendario
        x0, ytop = 40, H - 98
        side = 250
        gx = W - 80 - side - 20
        wkcol = 34
        cw = (gx - x0 - wkcol) / 7
        self.rrect(x0 + wkcol, ytop - 26, cw * 7, 26, 13, fill=col)
        for k, dname in enumerate(DIAS):
            self.texto(dname[:3].upper(), x0 + wkcol + cw * k + cw / 2, ytop - 17, "QB",
                       9.5, oscuro(col, 0.8), "c")
        semanas = semanas_de_mes(y, m)
        area = ytop - 34 - 30
        rh = area / len(semanas)
        for r, lun in enumerate(semanas):
            ry = ytop - 34 - (r + 1) * rh
            # botón semana
            iso = lun.isocalendar()[1]
            self.rrect(x0, ry + rh / 2 - 22, 26, 44, 13, fill=claro(col, 0.35))
            c.saveState()
            c.translate(x0 + 13, ry + rh / 2)
            c.rotate(90)
            c.setFont("QB", 8.5)
            c.setFillColor(oscuro(col, 0.8))
            c.drawCentredString(0, -3, f"SEM {iso}")
            c.restoreState()
            self.link(dest_sem(lun), x0, ry + rh / 2 - 22, 26, 44)
            for k in range(7):
                d = lun + dt.timedelta(days=k)
                cx = x0 + wkcol + cw * k
                fuera = d.month != m
                self.rrect(cx + 2, ry + 2, cw - 4, rh - 4, 9,
                           fill=PAPEL if fuera else BLANCO,
                           stroke=LINEA if fuera else claro(col, 0.15), lw=0.8)
                self.texto(str(d.day), cx + 9, ry + rh - 17, "QB" if not fuera else "Q", 11,
                           LINEA if fuera else (TINTA if k < 5 else oscuro(col, 0.5)))
                self.link(dest_sem(lun), cx + 2, ry + rh - 24, 30, 22)
        # panel lateral
        px = W - 80 - side
        def caja(titulo, ytop_, alto, checks):
            self.rrect(px, ytop_ - alto, side, alto, 14, fill=BLANCO, stroke=claro(col, 0.15))
            self.rrect(px + 10, ytop_ - 30, pdfmetrics.stringWidth(titulo, "QB", 10.5) + 24,
                       21, 10.5, fill=claro(col, 0.3))
            self.texto(titulo, px + 22, ytop_ - 23, "QB", 10.5, oscuro(col, 0.8))
            yy = ytop_ - 54
            while yy > ytop_ - alto + 12:
                if checks:
                    self.check(px + 14, yy - 1, oscuro(col, 0.3))
                c.setStrokeColor(LINEA)
                c.setLineWidth(0.8)
                c.line(px + (30 if checks else 14), yy - 2, px + side - 14, yy - 2)
                yy -= 24
        caja("objetivos del mes", ytop, 210, True)
        caja("fechas importantes", ytop - 222, 170, False)
        caja("notas", ytop - 404, ytop - 404 - 30, False)
        self.pestanas((y, m))
        c.showPage()

    def semanal(self, lun):
        c = self.c
        y, m = mes_de_semana(lun)
        col = PASTEL[m - 1]
        self.fondo()
        c.bookmarkPage(dest_sem(lun), fit="Fit")
        dom = lun + dt.timedelta(days=6)
        iso = lun.isocalendar()[1]
        # cabecera
        self.texto(f"Semana {iso}", 40, H - 62, "Serif", 32, TINTA)
        tw = pdfmetrics.stringWidth(f"Semana {iso}", "Serif", 32)
        rango = f"{fecha_corta(lun)} – {fecha_corta(dom)} {dom.year}"
        self.texto(rango, 52 + tw, H - 62, "Q", 15, oscuro(col, 0.45))
        tw2 = pdfmetrics.stringWidth(rango, "Q", 15)
        self.destello(66 + tw + tw2, H - 56, 7, col)
        # flechas semana anterior / siguiente
        i = SEMANAS.index(lun)
        ax = 40
        if i > 0:
            self.rrect(ax, H - 92, 92, 20, 10, fill=claro(col, 0.35))
            self.texto("‹ anterior", ax + 46, H - 86, "QB", 9.5, oscuro(col, 0.8), "c")
            self.link(dest_sem(SEMANAS[i - 1]), ax, H - 92, 92, 20)
        self.rrect(ax + 100, H - 92, 92, 20, 10, fill=claro(col, 0.35))
        self.texto(f"{MESES[m-1].lower()}", ax + 146, H - 86, "QB", 9.5, oscuro(col, 0.8), "c")
        self.link(dest_mes(y, m), ax + 100, H - 92, 92, 20)
        if i < len(SEMANAS) - 1:
            self.rrect(ax + 200, H - 92, 92, 20, 10, fill=claro(col, 0.35))
            self.texto("siguiente ›", ax + 246, H - 86, "QB", 9.5, oscuro(col, 0.8), "c")
            self.link(dest_sem(SEMANAS[i + 1]), ax + 200, H - 92, 92, 20)
        self.nav(col)
        # cuadrícula 4x2
        x0, ytop, ybot = 40, H - 106, 26
        gap = 12
        bw = (W - 80 - x0 - gap * 3) / 4
        bh = (ytop - ybot - gap) / 2
        for k in range(8):
            bx = x0 + (k % 4) * (bw + gap)
            by = ytop - (k // 4 + 1) * bh - (k // 4) * gap
            if k < 7:
                d = lun + dt.timedelta(days=k)
                dcol = PASTEL[d.month - 1]
                self.rrect(bx, by, bw, bh, 14, fill=BLANCO, stroke=claro(dcol, 0.1))
                self.rrect(bx + 8, by + bh - 32, bw - 16, 24, 12, fill=dcol if k < 5 else claro(dcol, 0.3))
                self.texto(DIAS[k], bx + 20, by + bh - 24, "QB", 11, oscuro(dcol, 0.8))
                self.texto(str(d.day), bx + bw - 20, by + bh - 25, "QB", 13, oscuro(dcol, 0.8), "r")
                if d.month != m:
                    self.texto(MESES[d.month - 1][:3].lower(), bx + bw - 22 -
                               pdfmetrics.stringWidth(str(d.day), "QB", 13) - 4,
                               by + bh - 24, "Q", 8.5, oscuro(dcol, 0.55), "r")
                self.lineas(bx + 12, by + bh - 36, bw - 24, by, paso=23)
            else:
                # prioridades + hábitos
                self.rrect(bx, by, bw, bh, 14, fill=claro(col, 0.55))
                self.texto("prioridades", bx + 14, by + bh - 24, "QB", 11, oscuro(col, 0.8))
                self.corazon(bx + bw - 20, by + bh - 24, 5, col)
                yy = by + bh - 48
                for _ in range(5):
                    self.check(bx + 14, yy - 1, oscuro(col, 0.35))
                    c.setStrokeColor(BLANCO)
                    c.setLineWidth(1)
                    c.line(bx + 30, yy - 2, bx + bw - 14, yy - 2)
                    yy -= 21
                self.texto("hábitos", bx + 14, yy - 10, "QB", 11, oscuro(col, 0.8))
                hx = bx + 84
                dw = (bw - 84 - 10) / 7
                for j, l in enumerate(INI):
                    self.texto(l, hx + dw * j + dw / 2, yy - 10, "QB", 7.5, oscuro(col, 0.5), "c")
                hy = yy - 30
                for _ in range(4):
                    c.setStrokeColor(BLANCO)
                    c.line(bx + 14, hy - 3, bx + 80, hy - 3)
                    for j in range(7):
                        c.setFillColor(BLANCO)
                        c.circle(hx + dw * j + dw / 2, hy + 1, 5, stroke=0, fill=1)
                    hy -= 19
        self.pestanas((y, m))
        c.showPage()

    def notas(self, n):
        c = self.c
        self.fondo()
        c.bookmarkPage(f"notas-{n}", fit="Fit")
        if n == 1:
            c.addOutlineEntry("Notas", "notas-1", 0)
        col = HexColor("#E9E1DA")
        self.texto("Notas", 40, H - 62, "Serif", 34, TINTA)
        self.texto(f"{n} / {NUM_NOTAS}", 150, H - 62, "Q", 14, SUAVE)
        self.nav(PASTEL[(n * 3) % 12])
        if n > 1:
            self.texto("‹", 40, 34, "QB", 16, SUAVE)
            self.link(f"notas-{n-1}", 34, 26, 24, 26)
        if n < NUM_NOTAS:
            self.texto("›", W - 100, 34, "QB", 16, SUAVE, "r")
            self.link(f"notas-{n+1}", W - 112, 26, 24, 26)
        self.rrect(40, 60, W - 160, H - 150, 16, fill=BLANCO, stroke=col)
        # cuadrícula de puntos
        c.setFillColor(HexColor("#DCCFC8"))
        x = 60
        while x < W - 130:
            yy = H - 112
            while yy > 76:
                c.circle(x, yy, 0.9, stroke=0, fill=1)
                yy -= 18
            x += 18
        self.pestanas("notas")
        c.showPage()

    def generar(self):
        self.portada()
        self.anual()
        hechas = set()
        for (y, m) in MESES_LISTA:
            self.mensual(y, m)
            for lun in SEMANAS:
                if mes_de_semana(lun) == (y, m) and lun not in hechas:
                    self.semanal(lun)
                    hechas.add(lun)
        for n in range(1, NUM_NOTAS + 1):
            self.notas(n)
        self.c.showOutline()
        self.c.save()


if __name__ == "__main__":
    out = os.path.join(HERE, SALIDA)
    Agenda(out).generar()
    print("Listo:", out)

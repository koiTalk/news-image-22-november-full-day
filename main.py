#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026: 54 stories from one day.

Pure Python 3 stdlib, no network, no clock, no randomness: fully deterministic.
Draws a 1024x1024 newspaper front page and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font (5x7)
# Each glyph: 7 rows of 5 bits, '#' = ink, '.' = blank.
FONT = {
    'A': "01110/10001/10001/11111/10001/10001/10001",
    'B': "11110/10001/10001/11110/10001/10001/11110",
    'C': "01110/10001/10000/10000/10000/10001/01110",
    'D': "11110/10001/10001/10001/10001/10001/11110",
    'E': "11111/10000/10000/11110/10000/10000/11111",
    'F': "11111/10000/10000/11110/10000/10000/10000",
    'G': "01110/10001/10000/10111/10001/10001/01111",
    'H': "10001/10001/10001/11111/10001/10001/10001",
    'I': "01110/00100/00100/00100/00100/00100/01110",
    'J': "00111/00010/00010/00010/00010/10010/01100",
    'K': "10001/10010/10100/11000/10100/10010/10001",
    'L': "10000/10000/10000/10000/10000/10000/11111",
    'M': "10001/11011/10101/10101/10001/10001/10001",
    'N': "10001/11001/10101/10011/10001/10001/10001",
    'O': "01110/10001/10001/10001/10001/10001/01110",
    'P': "11110/10001/10001/11110/10000/10000/10000",
    'Q': "01110/10001/10001/10001/10101/10010/01101",
    'R': "11110/10001/10001/11110/10100/10010/10001",
    'S': "01111/10000/10000/01110/00001/00001/11110",
    'T': "11111/00100/00100/00100/00100/00100/00100",
    'U': "10001/10001/10001/10001/10001/10001/01110",
    'V': "10001/10001/10001/10001/10001/01010/00100",
    'W': "10001/10001/10001/10101/10101/10101/01010",
    'X': "10001/10001/01010/00100/01010/10001/10001",
    'Y': "10001/10001/01010/00100/00100/00100/00100",
    'Z': "11111/00001/00010/00100/01000/10000/11111",
    'a': "00000/00000/01110/00001/01111/10001/01111",
    'b': "10000/10000/10110/11001/10001/10001/11110",
    'c': "00000/00000/01110/10000/10000/10001/01110",
    'd': "00001/00001/01101/10011/10001/10001/01111",
    'e': "00000/00000/01110/10001/11111/10000/01110",
    'f': "00110/01001/01000/11110/01000/01000/01000",
    'g': "00000/01111/10001/10001/01111/00001/01110",
    'h': "10000/10000/10110/11001/10001/10001/10001",
    'i': "00100/00000/01100/00100/00100/00100/01110",
    'j': "00010/00000/00110/00010/00010/10010/01100",
    'k': "10000/10000/10010/10100/11000/10100/10010",
    'l': "01100/00100/00100/00100/00100/00100/01110",
    'm': "00000/00000/11010/10101/10101/10101/10101",
    'n': "00000/00000/10110/11001/10001/10001/10001",
    'o': "00000/00000/01110/10001/10001/10001/01110",
    'p': "00000/00000/10110/11001/10001/11110/10000",
    'q': "00000/00000/01101/10011/10001/01111/00001",
    'r': "00000/00000/10110/11001/10000/10000/10000",
    's': "00000/00000/01111/10000/01110/00001/11110",
    't': "01000/01000/11110/01000/01000/01001/00110",
    'u': "00000/00000/10001/10001/10001/10011/01101",
    'v': "00000/00000/10001/10001/10001/01010/00100",
    'w': "00000/00000/10001/10101/10101/10101/01010",
    'x': "00000/00000/10001/01010/00100/01010/10001",
    'y': "00000/00000/10001/10001/01111/00001/01110",
    'z': "00000/00000/11111/00010/00100/01000/11111",
    '0': "01110/10001/10011/10101/11001/10001/01110",
    '1': "00100/01100/00100/00100/00100/00100/01110",
    '2': "01110/10001/00001/00110/01000/10000/11111",
    '3': "11111/00010/00100/00010/00001/10001/01110",
    '4': "00010/00110/01010/10010/11111/00010/00010",
    '5': "11111/10000/11110/00001/00001/10001/01110",
    '6': "00110/01000/10000/11110/10001/10001/01110",
    '7': "11111/00001/00010/00100/01000/01000/01000",
    '8': "01110/10001/10001/01110/10001/10001/01110",
    '9': "01110/10001/10001/01111/00001/00010/01100",
    ' ': "...../...../...../...../...../...../.....",
    '.': "...../...../...../...../...../01100/01100",
    ',': "...../...../...../...../01100/00100/01000",
    ':': "...../01100/01100/...../01100/01100/.....",
    ';': "...../01100/01100/...../01100/00100/01000",
    '!': "00100/00100/00100/00100/00100/...../00100",
    '?': "01110/10001/00001/00110/00100/...../00100",
    '-': "...../...../...../01110/...../...../.....",
    "'": "00100/00100/01000/...../...../...../.....",
    '"': "01010/01010/...../...../...../...../.....",
    '(': "00010/00100/01000/01000/01000/00100/00010",
    ')': "01000/00100/00010/00010/00010/00100/01000",
    '/': "00001/00010/00010/00100/01000/01000/10000",
    '%': "11001/11010/00010/00100/01000/01011/10011",
    '$': "00100/01111/10100/01110/00101/11110/00100",
    '&': "01100/10010/10100/01000/10101/10010/01101",
    '+': "...../00100/00100/01110/00100/00100/.....",
    '=': "...../...../11111/...../11111/...../.....",
    '*': "...../10101/01110/11111/01110/10101/.....",
    '#': "01010/01010/11111/01010/11111/01010/01010",
    '@': "01110/10001/10111/10101/10110/10000/01110",
    '_': "...../...../...../...../...../...../11111",
    '<': "00010/00100/01000/10000/01000/00100/00010",
    '>': "01000/00100/00010/00001/00010/00100/01000",
    '•': "...../00100/01110/01110/01110/00100/.....",
    '×': "...../10001/01010/00100/01010/10001/.....",
    '°': "00100/01010/00100/...../...../...../.....",
}
GLYPHS = {ch: tuple(r == '1' for row in g.split('/') for r in row)
          for ch, g in FONT.items()}

NORMALIZE = {
    '—': '-', '–': '-', '‘': "'", '’': "'", '“': '"', '”': '"',
    '…': '...', '–': '-', '‑': '-', ' ': ' ',
}
for _k in list(NORMALIZE):
    pass


def norm(s):
    return ''.join(NORMALIZE.get(c, c) for c in s)


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 38, 74)
NAVY2 = (28, 52, 96)
RED = (178, 39, 30)
TEAL = (14, 107, 107)
GOLD = (184, 138, 44)
GREY = (110, 108, 100)
LIGHT = (232, 226, 214)
WHITE = (255, 255, 255)
SKY = (178, 208, 224)
SEA = (120, 168, 196)
LAND = (196, 196, 158)
GREEN = (46, 125, 50)
ORANGE = (214, 110, 20)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        else:
            n = max(24, int(2 * 3.14159 * r))
            for k in range(n):
                a = 2 * 3.14159 * k / n
                self.px(int(cx + r * _cos(a)), int(cy + r * _sin(a)), c)

    def poly(self, pts, c):
        # scanline fill
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, 1, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        self.poly([(x0, y0), (x1, y1), (x2, y2)], c)

    # ---- text ----
    def char(self, x, y, ch, s, c):
        g = GLYPHS.get(ch)
        if g is None:
            return
        for r in range(7):
            for col in range(5):
                if g[r * 5 + col]:
                    self.rect(x + col * s, y + r * s, s, s, c)

    def text(self, x, y, s, sc, c):
        s = norm(s)
        cx = x
        for ch in s:
            self.char(cx, y, ch, sc, c)
            cx += 6 * sc
        return cx

    def text_w(self, s, sc):
        return len(norm(s)) * 6 * sc

    def text_c(self, cx, y, s, sc, c):
        self.text(cx - self.text_w(s, sc) // 2, y, s, sc, c)

    def wrap(self, s, maxchars):
        s = norm(s)
        lines, cur = [], ''
        for word in s.split(' '):
            if cur and len(cur) + 1 + len(word) > maxchars:
                lines.append(cur)
                cur = word
            else:
                cur = (cur + ' ' + word).strip()
        if cur:
            lines.append(cur)
        return lines


def _cos(a):
    return __import__('math').cos(a)


def _sin(a):
    return __import__('math').sin(a)


def write_png(path, cv):
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- illustrations
def draw_globe(cv, x, y, r):
    cv.circle(x, y, r, SKY, True)
    cv.circle(x, y, r, NAVY, False)
    cv.poly([(x - r + 6, y - 8), (x - r + 16, y - 14), (x - r + 22, y - 4),
             (x - r + 12, y + 2)], GREEN)
    cv.poly([(x + 2, y - 12), (x + 14, y - 16), (x + r - 6, y - 6),
             (x + 8, y - 2)], GREEN)
    cv.poly([(x - 10, y + 8), (x + 4, y + 6), (x + 10, y + 14),
             (x - 4, y + r - 4)], GREEN)
    cv.line(x - r, y, x + r, y, NAVY)
    cv.line(x, y - r, x, y + r, NAVY)


def draw_cop(cv, x, y, w, h):
    # conference hall: globe left, broken pact document right, big red X
    cv.rect(x, y, w, h, (224, 236, 240))
    draw_globe(cv, x + 52, y + h // 2 + 4, 34)
    cv.rect(x + 104, y + 14, 96, 66, WHITE)
    cv.frame(x + 104, y + 14, 96, 66, NAVY)
    for k in range(4):
        cv.rect(x + 112, y + 24 + k * 12, 80 - k * 12, 4, GREY)
    cv.line(x + 108, y + 18, x + 196, y + 76, RED)
    cv.line(x + 196, y + 18, x + 108, y + 76, RED)
    cv.rect(x + 8, y + h - 16, w - 16, 10, NAVY)
    cv.text(x + 12, y + h - 14, 'ANTALYA - FIRST NO-DEAL COP SINCE 2000', 1, WHITE)


def draw_dymer(cv, x, y, w, h):
    cv.rect(x, y, w, h, (40, 44, 56))
    # drone
    dx, dy = x + w - 56, y + 18
    cv.rect(dx - 16, dy - 2, 32, 4, (200, 200, 200))
    cv.circle(dx - 18, dy - 2, 5, (200, 200, 200), True)
    cv.circle(dx + 18, dy - 2, 5, (200, 200, 200), True)
    cv.rect(dx - 6, dy, 12, 8, (160, 160, 160))
    # apartment block, collapsed middle stairwell
    bx, by, bw, bh = x + 14, y + 22, 150, h - 36
    cv.rect(bx, by, bw, bh, (150, 138, 118))
    for r in range(5):
        for c in range(5):
            wx = bx + 8 + c * 28
            wy = by + 5 + r * 9
            if c == 2:
                continue
            cv.rect(wx, wy, 18, 7, (250, 214, 120) if r % 2 else (60, 60, 66))
    cv.poly([(bx + 56, by), (bx + 84, by), (bx + 78, by + bh),
             (bx + 62, by + bh)], (30, 30, 34))
    cv.rect(bx + 52, by + bh - 10, 46, 10, (90, 84, 70))
    cv.tri(bx + 52, by + bh - 10, bx + 75, by + bh - 18, bx + 98,
           by + bh - 10, (90, 84, 70))
    # fire glow
    cv.circle(bx + 75, by + 14, 8, ORANGE, True)
    cv.circle(bx + 75, by + 14, 4, RED, True)
    cv.rect(x + 8, y + h - 16, w - 16, 10, NAVY)
    cv.text(x + 12, y + h - 14, 'DYMER, NORTH OF KYIV - 14 MISSING', 1, WHITE)


def draw_gulf(cv, x, y, w, h):
    cv.rect(x, y, w, h, (250, 196, 120))
    cv.rect(x, y + h - 44, w, 44, SEA)
    cv.rect(x, y + h - 44, w, 3, (220, 230, 235))
    # sun
    cv.circle(x + w - 44, y + 26, 18, (255, 240, 160), True)
    # tanker 1
    tx, ty = x + 16, y + h - 62
    cv.rect(tx, ty, 110, 18, (120, 40, 30))
    cv.rect(tx + 84, ty - 14, 20, 14, WHITE)
    cv.rect(tx + 10, ty - 8, 30, 8, (90, 30, 24))
    cv.rect(tx + 46, ty - 8, 8, 8, (90, 30, 24))
    # tanker 2 (far)
    tx2 = x + w - 130
    cv.rect(tx2, ty + 6, 80, 12, (70, 70, 80))
    cv.rect(tx2 + 58, ty - 2, 14, 8, WHITE)
    # missile streaks
    cv.line(x + 30, y + 12, x + 90, y + 44, RED)
    cv.line(x + 34, y + 8, x + 94, y + 40, RED)
    cv.circle(x + 92, y + 42, 4, RED, True)
    cv.line(x + 150, y + 6, x + 190, y + 30, RED)
    cv.circle(x + 192, y + 32, 4, RED, True)
    cv.rect(x + 8, y + h - 16, w - 16, 10, NAVY)
    cv.text(x + 12, y + h - 14, 'STRAIT OF HORMUZ - GULF STANDOFF', 1, WHITE)


def icon_ship(cv, x, y, c):
    cv.rect(x, y + 12, 26, 8, c)
    cv.rect(x + 18, y + 2, 6, 10, c)
    cv.line(x, y + 12, x + 5, y + 20, c)
    cv.line(x + 26, y + 12, x + 21, y + 20, c)
    cv.line(x + 5, y + 20, x + 21, y + 20, c)


def icon_flame(cv, x, y, c):
    cv.tri(x + 13, y, x + 24, y + 18, x + 13, y + 26, c)
    cv.tri(x + 13, y, x + 2, y + 18, x + 13, y + 26, c)
    cv.circle(x + 13, y + 18, 6, c, True)


def icon_missile(cv, x, y, c):
    cv.line(x + 4, y + 22, x + 22, y + 4, c)
    cv.tri(x + 22, y + 4, x + 26, y + 8, x + 18, y + 10, c)
    cv.tri(x + 4, y + 22, x + 8, y + 18, x + 2, y + 18, c)


def icon_fire(cv, x, y, c):
    cv.rect(x + 2, y + 14, 22, 10, c)
    cv.tri(x + 2, y + 14, x + 13, y + 2, x + 24, y + 14, c)
    cv.rect(x + 6, y + 8, 14, 6, (255, 200, 60))


def icon_drone(cv, x, y, c):
    cv.rect(x + 4, y + 10, 18, 4, c)
    cv.circle(x + 3, y + 10, 4, c, True)
    cv.circle(x + 23, y + 10, 4, c, True)
    cv.rect(x + 11, y + 14, 4, 6, c)


def icon_cap(cv, x, y, c):
    cv.tri(x + 2, y + 12, x + 13, y + 2, x + 24, y + 12, c)
    cv.rect(x + 2, y + 12, 22, 3, c)
    cv.rect(x + 22, y + 15, 4, 3, c)


def icon_card(cv, x, y, c):
    cv.rect(x + 2, y + 6, 22, 14, c)
    cv.rect(x + 2, y + 6, 22, 4, WHITE)
    cv.rect(x + 5, y + 13, 12, 2, WHITE)


def icon_mic(cv, x, y, c):
    cv.rect(x + 10, y + 2, 6, 12, c)
    cv.rect(x + 6, y + 14, 14, 3, c)
    cv.rect(x + 12, y + 17, 2, 6, c)


def icon_ball(cv, x, y, c):
    cv.circle(x + 13, y + 13, 11, c, True)
    cv.circle(x + 13, y + 13, 4, WHITE, True)
    cv.line(x + 13, y + 2, x + 13, y + 9, WHITE)
    cv.line(x + 13, y + 17, x + 13, y + 24, WHITE)
    cv.line(x + 2, y + 13, x + 9, y + 13, WHITE)
    cv.line(x + 17, y + 13, x + 24, y + 13, WHITE)


def icon_bat(cv, x, y, c):
    cv.rect(x + 6, y + 2, 6, 16, c)
    cv.rect(x + 8, y + 18, 3, 6, c)
    cv.circle(x + 20, y + 20, 4, RED, True)


def icon_flag(cv, x, y, c):
    cv.rect(x + 5, y + 2, 2, 22, c)
    cv.tri(x + 7, y + 2, x + 24, y + 6, x + 7, y + 11, c)


def icon_parl(cv, x, y, c):
    cv.tri(x + 2, y + 10, x + 13, y + 2, x + 24, y + 10, c)
    cv.rect(x + 4, y + 12, 3, 10, c)
    cv.rect(x + 12, y + 12, 3, 10, c)
    cv.rect(x + 20, y + 12, 3, 10, c)
    cv.rect(x + 2, y + 22, 22, 2, c)


ICONS = [icon_ship, icon_flame, icon_missile, icon_fire, icon_drone, icon_cap,
         icon_card, icon_mic, icon_ball, icon_bat, icon_flag, icon_parl]


# ---------------------------------------------------------------- world map
# coarse continent polygons in (lon, lat)
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-55, 52), (-60, 47), (-70, 44),
     (-75, 38), (-80, 32), (-84, 30), (-90, 21), (-97, 26), (-105, 22),
     (-110, 24), (-117, 33), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58), (-168, 66)],
    [(-80, 10), (-75, 12), (-62, 10), (-52, 5), (-50, 0), (-45, -5),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -45),
     (-70, -52), (-73, -40), (-72, -25), (-78, -10), (-80, 10)],
    [(-18, 35), (-10, 37), (-9, 43), (-2, 44), (0, 46), (-4, 48),
     (2, 51), (8, 54), (10, 57), (18, 56), (21, 55), (28, 59),
     (30, 60), (24, 65), (30, 70), (40, 68), (45, 66), (50, 60),
     (40, 55), (35, 50), (30, 46), (28, 44), (23, 40), (20, 40),
     (15, 38), (10, 37), (0, 38), (-6, 36), (-10, 35), (-18, 35)],
    [(-18, 32), (-10, 30), (-5, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (51, 12), (44, 0), (40, -10),
     (36, -20), (32, -29), (26, -34), (19, -35), (15, -27), (12, -18),
     (13, -12), (9, -2), (9, 4), (0, 6), (-8, 5), (-13, 8), (-17, 15),
     (-17, 21), (-16, 28), (-18, 32)],
    [(45, 70), (60, 69), (70, 72), (90, 75), (110, 74), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 45), (142, 40), (135, 35), (130, 33), (127, 38), (122, 40),
     (120, 32), (115, 23), (109, 18), (105, 10), (100, 8), (98, 14),
     (95, 16), (92, 21), (89, 22), (86, 20), (80, 15), (77, 8),
     (73, 16), (66, 25), (61, 25), (57, 26), (52, 26), (50, 29),
     (48, 30), (44, 29), (40, 32), (36, 36), (30, 36), (27, 40),
     (23, 40), (26, 45), (28, 45), (30, 50), (32, 55), (35, 60),
     (40, 65), (45, 70)],
    [(114, -22), (124, -15), (132, -12), (142, -11), (146, -19),
     (150, -23), (153, -28), (150, -37), (145, -38), (140, -38),
     (135, -35), (130, -32), (124, -33), (116, -35), (114, -22)],
]


def draw_map(cv, x, y, w, h, pins):
    cv.rect(x, y, w, h, (214, 230, 236))
    for cont in CONTINENTS:
        pts = []
        for lon, lat in cont:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((90 - lat) / 180.0 * h)
            pts.append((px, py))
        cv.poly(pts, LAND)
    # graticule
    for lon in range(-150, 181, 30):
        gx = x + int((lon + 180) / 360.0 * w)
        for yy in range(y, y + h, 4):
            cv.px(gx, yy, (190, 205, 215))
    for lat in (-60, -30, 0, 30, 60):
        gy = y + int((90 - lat) / 180.0 * h)
        for xx in range(x, x + w, 4):
            cv.px(xx, gy, (190, 205, 215))
    for num, lon, lat, col in pins:
        px = x + int((lon + 180) / 360.0 * w)
        py = y + int((90 - lat) / 180.0 * h)
        cv.circle(px, py, 7, col, True)
        cv.circle(px, py, 7, WHITE, False)
        cv.text(px - 3 if len(num) == 1 else px - 6, py - 3, num, 1, WHITE)


# ---------------------------------------------------------------- content
LEADS = [
    ("COP31 COLLAPSES:",
     "NO CLIMATE DEAL",
     "Antalya ends in no deal after 2 weeks + 2 days overtime. EU, UK, "
     "island states rejected a draft silent on fossil fuels.",
     draw_cop),
    ("DRONE FLATTENS",
     "FLAT, 14 MISSING",
     "Russian drone hits 5-storey block in Dymer, north of Kyiv; stairwell "
     "collapses. 14 missing, 9 evacuated, 2 bodies found.",
     draw_dymer),
    ("GULF STANDOFF:",
     "BAHRAIN HIT",
     "Iranian projectiles hit a civilian site in Bahrain; 2 hurt, 1 "
     "critical. Two Hong Kong tankers hit near Hormuz; 14+ wait at Kharg.",
     draw_gulf),
]

MEDIUM = [
    ("2ND RUSSIAN SHIP HIT IN 24H",
     "Dawn blast hits the corvette Merkury at Benghazi naval base in Libya. "
     "Drone attack suspected; injuries, no deaths reported. Axios: "
     "Ukraine's SBU blamed."),
    ("SPARTA II STILL BURNING",
     "Russian cargo ship hit by drones on Saturday still burns in the Gulf "
     "of Finland despite overnight firefighting. All 16 crew evacuated. "
     "Finland: Ukraine likely behind it."),
    ("3 RUSSIAN KH-101 OVER POLAND",
     "Prosecutors say all three objects that flew in on Friday were Kh-101 "
     "missiles, made in Q4 2026 - not drones as first thought. NATO meets "
     "Monday."),
    ("SETTLERS TORCHED CARS IN WEST BANK",
     "Israeli settlers set fire to 12 vehicles and sprayed racist graffiti "
     "in four villages near Ramallah and in the South Hebron Hills. No "
     "injuries; police investigating."),
    ("DRONES STRIKE KHARTOUM",
     "Early-morning drone strikes kill four in and around Sudan's capital "
     "and damage a UN building while staff were inside. RSF blamed in "
     "local reports."),
    ("SEOUL EDUCATION MINISTER RESIGNS",
     "Choi Kyo-jin quits after last-minute measures to stop AI-assisted "
     "cheating in the national college entrance exam caused chaos."),
    ("TRUMP BACKS 10% CARD CAP",
     "Trump says he will work with the incoming Democratic Congress to cap "
     "credit-card interest at 10%, far below today's median of about 22.2%. "
     "No law yet."),
    ("PUTIN 'NOT A FRIEND'",
     "DNI Jay Clayton says Putin is 'not America's friend' on Ukraine, days "
     "after Trump praised him. Trump: hard to work with Schumer as Senate "
     "leader."),
    ("LIVERPOOL THRASH UTD 4-0",
     "Liverpool thrash 10-man Man Utd 4-0 at Anfield: Szoboszlai 10', Wirtz "
     "13', Ngumoha 66', Munoz 82'. Yoro sent off 8'. Pochettino's first "
     "game. Hull beat Brighton 2-0."),
    ("INDIA DECLARES 720/9 IN WELLINGTON",
     "India declare at 720/9 on Day 4 - the highest Test innings ever on New "
     "Zealand soil. Rahul 136, Pant 128. At stumps NZ 119/2, still 233 "
     "behind."),
    ("NEPAL PM LANDS IN INDIA",
     "PM Balendra (Balen) Shah reaches New Delhi for a two-day state visit - "
     "his first trip to India since taking office in March and his first "
     "bilateral visit abroad."),
    ("MAY: 'BREXIT IS DONE'",
     "Theresa May says she is 'aghast' at PM Andy Burnham's EU plans as the "
     "government defends its new UK-EU package. Farage attacks the deal in "
     "Brussels."),
]

ALSO = [
    "Israel: Eisenkot invites Likud to coalition talks.",
    "Kharg: 14+ Iranian tankers staged, none sailed.",
    "Spoof: 'Khat Shekan' tanker track was faked.",
    "Iran claims it hit a US F-16; CENTCOM denies.",
    "Iowa: Army to detonate 68 barrels of lead azide.",
    "Seattle: governor condemns ICE arrests at Sea-Tac.",
    "RAF: next fighter jet may be the last crewed one.",
    "Centrica boss 'hugely concerned' over energy bills.",
    "BBC apologises for Strictly noise disruption.",
    "Rahul 136: first Indian opener with 100s in SENA.",
    "Pant 128: first Indian keeper with 100s in SENA.",
    "Modi: happy people are buying less gold.",
    "Amit Shah: better Centre-State peace coordination.",
    "Films from BRICS opens at IFFI in Goa.",
    "India-Bangladesh talks as Ganga treaty nears end.",
    "Delhi court frames charges in NEET paper leak.",
    "First Ladakh local polls since 2026; 187,000 vote.",
    "HPV drive: 1 crore+ free doses to girls aged 14+.",
    "ICE: record 483,200 deportations in 2026.",
    "Somali American driver assaulted after Trump remark.",
    "Senate rejects war powers limit on Iran strikes.",
    "St. Johns River breaks 73-year record in Florida.",
    "Cost-of-living protests enter 6th weekend in France.",
    "Belgium air traffic strikes planned, not yet held.",
    "Libya loses $30.8m as pipeline blocked 20+ days.",
    "Saudi Arabia triples oil stored in Japan.",
    "Iran begins rationing electricity.",
    "Israeli strike hits World Central Kitchen truck.",
    "DRC Ebola outbreak hampers aid delivery.",
    "Qatari-Iranian diplomatic talks reported.",
    "One-time CRISPR therapy cuts bad cholesterol 52%.",
    "Earth gains a new mini-moon: asteroid 2026 QQ8.",
    "Bolsonaro in intensive care with bowel obstruction.",
    "Kansas City Current win first NWSL Championship.",
    "Cavalry FC win Canadian Premier League title.",
    "Canadian women sweep 500m speed skating podium.",
    "Culture: 200 mascots in Saitama; anime tapestries.",
    "Science: Essex moth; Jersey squirrels; Milky Way.",
    "NFL early finals: BUF 26-9 MIA, CHI 21-13 NO, DAL 51-30 TEN, DET "
    "31-21 TB, KC 34-7 ARI, PHI 19-16 PIT.",
]

NUMBERS = [
    ("14", "missing after drone hits flat in Dymer"),
    ("720/9", "India declare in Wellington, lead 352"),
    ("483,200", "ICE deportations in 2026, a record"),
    ("52%", "cholesterol cut by one-time CRISPR therapy"),
    ("$92.57", "Brent crude, Fri 20 Nov close"),
    ("4-0", "Liverpool rout Man Utd at Anfield"),
]

PINS = [
    ("1", 15, 28, NAVY), ("2", 28, 62, NAVY), ("3", 19, 52, NAVY),
    ("4", 38, 30, NAVY), ("5", 28, 13, NAVY), ("6", 127, 37, NAVY),
    ("7", -77, 39, NAVY), ("9", -0.3, 53.7, NAVY),
    ("10", 174.8, -41.3, NAVY), ("11", 77.2, 28.6, NAVY),
    ("12", -8, 55, NAVY),
    ("A", 24, 38, RED), ("B", 34, 52, RED), ("C", 56.5, 26.5, RED),
]
LEGEND = ("1 Benghazi 2 Gulf of Finland 3 Poland 4 West Bank 5 Khartoum "
          "6 Seoul 7-8 Washington 9 Hull 10 Wellington 11 New Delhi "
          "12 London A Antalya B Dymer C Hormuz")


# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 56, NAVY)
    cv.rect(0, 56, W, 3, GOLD)
    cv.text(16, 8, "THE WORLD TODAY", 4, WHITE)
    cv.text(16, 40, "54 STORIES FROM ONE DAY", 2, GOLD)
    date = "SUNDAY 22 NOVEMBER 2026"
    cv.text(W - 16 - cv.text_w(date, 2), 10, date, 2, WHITE)
    cv.text(W - 16 - cv.text_w("ANTALYA - DYMER - HORMUZ", 1), 40,
            "ANTALYA - DYMER - HORMUZ", 1, (200, 205, 220))

    # ---- leads ----
    ly, lh = 64, 240
    lw = (W - 32 - 16) // 3
    for i, (h1, h2, body, draw) in enumerate(LEADS):
        x = 16 + i * (lw + 8)
        cv.rect(x, ly, lw, lh, WHITE)
        cv.frame(x, ly, lw, lh, NAVY)
        cv.rect(x, ly, lw, 20, NAVY)
        cv.text_c(x + lw // 2, ly + 4, "LEAD %d" % (i + 1), 2, WHITE)
        draw(cv, x + 8, ly + 20, lw - 16, 84)
        hy = ly + 106
        cv.text(x + 8, hy, h1, 3, RED if i else NAVY)
        cv.text(x + 8, hy + 24, h2, 3, RED if i else NAVY)
        lines = cv.wrap(body, 26)
        for k, ln in enumerate(lines[:6]):
            cv.text(x + 8, hy + 46 + k * 17, ln, 2, INK)

    # ---- medium grid ----
    my, mh = 310, 100
    mw = (W - 32 - 24) // 4
    for i, (head, body) in enumerate(MEDIUM):
        r, c = divmod(i, 4)
        x = 16 + c * (mw + 8)
        y = my + r * (mh + 6)
        cv.rect(x, y, mw, mh, WHITE)
        cv.frame(x, y, mw, mh, NAVY)
        cv.rect(x, y, 30, 16, RED)
        cv.text(x + 9 if i + 1 < 10 else x + 6, y + 4, "M%d" % (i + 1), 1,
                WHITE)
        ICONS[i](cv, x + mw - 32, y + 2, NAVY2)
        hl = cv.wrap(head, 19)
        for k, ln in enumerate(hl[:2]):
            cv.text(x + 8, y + 20 + k * 17, ln, 2, NAVY)
        lines = cv.wrap(body, 39)
        for k, ln in enumerate(lines[:5]):
            cv.text(x + 8, y + 54 + k * 9, ln, 1, INK)

    # ---- map ----
    y = 628
    cv.text(16, y, "WHERE IT HAPPENED - 12 STORIES ON THE MAP", 1, NAVY)
    cv.text(W - 16 - cv.text_w("RED LETTERS = LEAD STORIES", 1), y,
            "RED LETTERS = LEAD STORIES", 1, RED)
    draw_map(cv, 16, y + 14, W - 32, 76, PINS)
    cv.text(16, y + 96, LEGEND, 1, INK)

    # ---- by the numbers ----
    y = 738
    cv.rect(16, y, W - 32, 56, NAVY)
    bw = (W - 32) // 6
    for i, (num, lab) in enumerate(NUMBERS):
        x = 16 + i * bw
        if i:
            cv.rect(x, y + 8, 1, 40, (90, 100, 130))
        cv.text_c(x + bw // 2, y + 6, num, 3, GOLD)
        lines = cv.wrap(lab, 24)
        for k, ln in enumerate(lines[:2]):
            cv.text_c(x + bw // 2, y + 30 + k * 10, ln, 1, WHITE)

    # ---- also today ----
    y = 802
    cv.text(16, y, "ALSO TODAY - 39 MORE STORIES", 2, NAVY)
    cv.rect(16, y + 18, W - 32, 1, NAVY)
    colw = (W - 32 - 16) // 3
    yy = y + 24
    for col in range(3):
        x = 16 + col * (colw + 8)
        cy = yy
        for j in range(13):
            idx = col * 13 + j
            item = "%d. %s" % (idx + 1, ALSO[idx])
            for ln in cv.wrap(item, 54):
                cv.text(x, cy, ln, 1, INK)
                cy += 9

    # ---- markets ticker ----
    y = 960
    cv.rect(0, y, W, 52, NAVY)
    cv.text(16, y + 2, "MARKETS - FRI 20 NOV CLOSE (MARKETS CLOSED SUNDAY)",
            2, GOLD)
    cv.text(16, y + 17,
            "S&P 500 6,910.39 -3.70% | NASDAQ 22,617.73 -5.28% | "
            "DOW 48,147.33 -1.93%", 2, WHITE)
    cv.text(16, y + 32,
            "FTSE -1.02% | NIKKEI -5.06% | BRENT $92.57 | GOLD $3,515.40 | "
            "10Y ~4.91%", 2, WHITE)

    # ---- footer ----
    cv.text(16, 1014,
            "Sources: Reuters, AP, BBC, CNN, Al Jazeera, AFP, Sky Sports, "
            "The Times, FT - 22 Nov 2026. NFL finals: Sportradar. Markets: "
            "Fri 20 Nov close.", 1, GREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = build()
    n = write_png(path, cv)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()

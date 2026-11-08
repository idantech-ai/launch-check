#!/usr/bin/env python3
"""WCAG 2.1 contrast checker with an on-brand fix suggestion.

Usage:
  python3 contrast.py FG BG [--large] [--adjust-bg]
  python3 contrast.py "#FF6B2C" "#FFFFFF"              # orange text on white
  python3 contrast.py "#FFFFFF" "#FF6B2C" --adjust-bg  # white text on an orange button

--adjust-bg: the brand color is the BACKGROUND (e.g. a button), so suggest a
new background shade and keep the text color. Default adjusts the text color.

Prints the contrast ratio, whether it passes AA (4.5:1 normal text,
3:1 large text / UI components), and — if it fails — the closest shade
of the same hue that passes, darker or lighter depending on the background.
Standard library only.
"""
import colorsys
import sys


def parse_hex(value):
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"not a hex color: {value}")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def suggest(color, fixed, target):
    """Walk the color's lightness (HLS) away from the fixed color until the target is met."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in color))
    go_darker = luminance(fixed) > 0.18
    step = -0.005 if go_darker else 0.005
    while 0 <= l <= 1:
        candidate = tuple(c * 255 for c in colorsys.hls_to_rgb(h, l, s))
        if ratio(candidate, fixed) >= target:
            return to_hex(candidate), ratio(candidate, fixed)
        l += step
    return None, None


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    large = "--large" in argv
    if len(args) != 2:
        print(__doc__)
        return 2
    fg, bg = parse_hex(args[0]), parse_hex(args[1])
    target = 3.0 if large else 4.5
    r = ratio(fg, bg)
    status = "PASS" if r >= target else "FAIL"
    print(f"{to_hex(fg)} on {to_hex(bg)}: {r:.2f}:1 — {status} (AA needs {target}:1"
          f"{' for large text / UI' if large else ' for normal text'})")
    if r < target:
        adjust_bg = "--adjust-bg" in argv
        color, fixed = (bg, fg) if adjust_bg else (fg, bg)
        hex_, new_r = suggest(color, fixed, target)
        which = "background" if adjust_bg else "text"
        if hex_:
            print(f"Closest passing {which} shade of the same hue: {hex_} ({new_r:.2f}:1)")
        else:
            other = "text" if adjust_bg else "background"
            print(f"No passing {which} shade of this hue found — change the {other} color instead.")
    return 0 if r >= target else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

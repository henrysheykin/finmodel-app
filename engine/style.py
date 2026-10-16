"""Shared workbook style kit (Arial; blue input, black formula, green link)."""

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT = "Arial"
NAVY = "1F3864"
SECTION = "2F5597"
BLUE = "0000FF"
GREEN = "008000"
GREY = "6B7280"
ORANGE = "C55A11"
YELLOW_FILL = PatternFill("solid", fgColor="FFFF00")
_thin = Side(style="thin", color="D9D9D9")
BOTTOM = Border(bottom=_thin)
TOTAL_TOP = Border(top=Side(style="thin", color="000000"))


def font(color: str = "000000", bold: bool = False, size: int = 10, italic: bool = False) -> Font:
    return Font(name=FONT, color=color, bold=bold, size=size, italic=italic)


def title(ws, text: str, sub: str | None = None, width_cols: int = 8) -> None:
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, size=14, bold=True, color="FFFFFF")
    for c in range(1, width_cols + 1):
        ws.cell(row=1, column=c).fill = PatternFill("solid", fgColor=NAVY)
    ws.row_dimensions[1].height = 24
    if sub:
        ws["A2"] = sub
        ws["A2"].font = font(GREY, italic=True, size=9)


def section(ws, row: int, text: str, ncols: int) -> None:
    ws.cell(row=row, column=1, value=text).font = font("FFFFFF", bold=True)
    for c in range(1, ncols + 1):
        ws.cell(row=row, column=c).fill = PatternFill("solid", fgColor=SECTION)


def header(cell, right: bool = False) -> None:
    cell.font = font(bold=True)
    cell.border = BOTTOM
    cell.alignment = Alignment(horizontal="right" if right else "left")

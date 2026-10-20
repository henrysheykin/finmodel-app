"""Chart kit — native Excel charts for every presentation sheet (docs/WORKBOOK_STANDARD.md §3).

Charts reference cells, so they stay live when the scenario switch changes. The kit fixes the look: Arial,
title 10 pt bold ink, axes and legend 8 pt grey, legend at the bottom, no chart border, light gridlines,
category labels at the bottom even when values go negative, data labels with every flag but the value off
(LibreOffice shows series and category names otherwise), series colours in the standard order.

Kinds: ``bar`` (columns, clustered or stacked), ``hbar`` (horizontal bars), ``line``, ``combo`` (bars plus a
line on a secondary axis), ``doughnut``. Every function takes cell *range strings* (``'Dashboard'!$B$12:$F$12``)
and returns the chart; ``place`` anchors it. A chart survives the LibreOffice recalculation step (engine/recalc.py
re-saves the file); ``tests/test_dashboard.py`` opens the recalculated file and finds the charts again.
"""

from __future__ import annotations

from dataclasses import dataclass

from openpyxl.chart import BarChart, DoughnutChart, LineChart
from openpyxl.chart import Series as _Series
from openpyxl.chart.data_source import AxDataSource, NumRef, StrRef
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint, SeriesLabel
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText, Text
from openpyxl.chart.title import Title
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, RegularTextRun
from openpyxl.drawing.text import Font as DFont

from engine import style as st

#: standard size (cm): 8 grid cells x 16 rows of the Dashboard grid
WIDTH_CM, HEIGHT_CM = 14.2, 8.3
#: the one large chart (Break-even)
LARGE_CM = (20.0, 10.5)
#: series colours in the standard order (red only for losses / lost items)
PALETTE = (st.PINE, st.SAGE, st.AMBER, st.INK, st.CHART_GREY)
LOSS = st.RED
TITLE_PT, TEXT_PT = 1000, 800
GRID = "E3E6E1"
AXIS = "9AA3A0"
#: axis / label formats
MILLIONS = '$#,##0.0,,"M"'
THOUSANDS = "$#,##0,"
PERCENT = "0%"


@dataclass(frozen=True)
class Ser:
    """One series: a value range, its name (literal text or a single-cell reference) and an optional colour."""

    values: str
    name: str
    color: str | None = None


# --------------------------------------------------------------------------- text and shapes
def _cp(sz: int, bold: bool = False, color: str = st.GREY) -> CharacterProperties:
    return CharacterProperties(sz=sz, b=bold, solidFill=color, latin=DFont(typeface=st.FONT))


def _rich(sz: int = TEXT_PT, color: str = st.GREY) -> RichText:
    return RichText(
        p=[Paragraph(pPr=ParagraphProperties(defRPr=_cp(sz, color=color)), endParaRPr=_cp(sz, color=color))]
    )


def _title(text: str) -> Title:
    cp = _cp(TITLE_PT, True, st.INK)
    para = Paragraph(pPr=ParagraphProperties(defRPr=cp), r=[RegularTextRun(rPr=cp, t=text)])
    return Title(tx=Text(rich=RichText(p=[para])), overlay=False)


def _is_ref(text: str) -> bool:
    return "!" in text and "$" in text


def _name(text: str) -> SeriesLabel:
    return SeriesLabel(strRef=StrRef(f=text)) if _is_ref(text) else SeriesLabel(v=text)


def _series(ser: Ser, cats: str | None, line: bool = False, color: str | None = None) -> _Series:
    s = _Series(ser.values)
    s.tx = _name(ser.name)
    if cats:
        s.cat = AxDataSource(numRef=NumRef(f=cats))
    col = ser.color or color
    if col:
        if line:
            s.graphicalProperties.line.solidFill = col
            s.graphicalProperties.line.width = 28000
            s.marker.symbol = "circle"
            s.marker.size = 6
            s.marker.graphicalProperties = GraphicalProperties(solidFill=col, ln=LineProperties(solidFill=col))
            s.smooth = False
        else:
            s.graphicalProperties = GraphicalProperties(solidFill=col, ln=LineProperties(noFill=True))
    if not line:
        s.invertIfNegative = False  # Excel would otherwise paint negative bars white
    return s


def _value_labels(fmt: str | None = None, position: str | None = None) -> DataLabelList:
    d = DataLabelList()
    d.showVal = True
    d.showSerName = d.showCatName = d.showLegendKey = d.showPercent = d.showBubbleSize = d.showLeaderLines = False
    if fmt:
        d.numFmt = fmt
    if position:
        d.position = position
    d.txPr = _rich(TEXT_PT, st.INK)
    return d


def style_chart(ch, title: str, size: tuple[float, float] = (WIDTH_CM, HEIGHT_CM), legend: bool = True) -> None:
    """Title, size, legend at the bottom, no border, light gridlines, category labels at the bottom."""
    ch.title = _title(title)
    ch.width, ch.height = size
    ch.style = 2
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    if legend:
        ch.legend.position = "b"
        ch.legend.txPr = _rich()
    else:
        ch.legend = None
    if not hasattr(ch, "x_axis"):
        return
    for ax in (ch.x_axis, ch.y_axis):
        ax.delete = False
        ax.txPr = _rich()
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill=GRID))
    ch.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.x_axis.spPr = GraphicalProperties(ln=LineProperties(solidFill=AXIS))
    ch.x_axis.tickLblPos = "low"  # labels stay below the plot when values go negative


# --------------------------------------------------------------------------- kinds
def bar(
    title: str,
    cats: str,
    series: list[Ser],
    *,
    fmt: str = MILLIONS,
    cat_fmt: str | None = None,
    stacked: bool = False,
    horizontal: bool = False,
    labels: bool = False,
    label_fmt: str | None = None,
    legend: bool | None = None,
    size: tuple[float, float] = (WIDTH_CM, HEIGHT_CM),
    gap: int = 60,
) -> BarChart:
    """Column chart (``horizontal`` = bars). One series gets no legend unless asked."""
    ch = BarChart()
    ch.type = "bar" if horizontal else "col"
    ch.gapWidth = gap
    if stacked:
        ch.grouping, ch.overlap = "stacked", 100
    for i, ser in enumerate(series):
        ch.series.append(_series(ser, cats, color=PALETTE[i % len(PALETTE)]))
    style_chart(ch, title, size, legend=len(series) > 1 if legend is None else legend)
    ch.y_axis.number_format = fmt
    if cat_fmt:
        ch.x_axis.number_format = cat_fmt
    if horizontal:
        ch.x_axis.scaling.orientation = "maxMin"  # first category on top
        ch.y_axis.crosses = "max"
    if labels:
        ch.dataLabels = _value_labels(label_fmt, None if stacked else "outEnd")
    return ch


def line(
    title: str,
    cats: str,
    series: list[Ser],
    *,
    fmt: str = MILLIONS,
    cat_fmt: str | None = None,
    labels: bool = False,
    legend: bool | None = None,
    size: tuple[float, float] = (WIDTH_CM, HEIGHT_CM),
) -> LineChart:
    ch = LineChart()
    for i, ser in enumerate(series):
        ch.series.append(_series(ser, cats, line=True, color=PALETTE[i % len(PALETTE)]))
    style_chart(ch, title, size, legend=len(series) > 1 if legend is None else legend)
    ch.y_axis.number_format = fmt
    if cat_fmt:
        ch.x_axis.number_format = cat_fmt
    if labels:
        ch.dataLabels = _value_labels(fmt, "t")
    return ch


def combo(
    title: str,
    cats: str,
    bars: list[Ser],
    lines: list[Ser],
    *,
    fmt: str = MILLIONS,
    line_fmt: str = PERCENT,
    cat_fmt: str | None = None,
    stacked: bool = False,
    size: tuple[float, float] = (WIDTH_CM, HEIGHT_CM),
) -> BarChart:
    """Bars on the left axis plus line(s) on a secondary right axis (colours continue the standard order)."""
    base = bar(title, cats, bars, fmt=fmt, cat_fmt=cat_fmt, stacked=stacked, legend=True, size=size)
    top = LineChart()
    for i, ser in enumerate(lines):
        top.series.append(_series(ser, cats, line=True, color=PALETTE[2 + i % (len(PALETTE) - 2)]))
    top.y_axis.axId = 200
    top.y_axis.crosses = "max"
    top.y_axis.delete = False
    top.y_axis.number_format = line_fmt
    top.y_axis.majorGridlines = None
    top.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    top.y_axis.txPr = _rich()
    base += top
    return base


def doughnut(
    title: str,
    cats: str,
    values: Ser,
    colors: tuple[str, ...] = PALETTE,
    *,
    points: int,
    size: tuple[float, float] = (WIDTH_CM, HEIGHT_CM),
) -> DoughnutChart:
    """Doughnut of one series of ``points`` slices, percentage labels, legend at the bottom."""
    ch = DoughnutChart()
    ch.holeSize = 55
    s = _series(values, cats)
    for i in range(points):
        s.dPt.append(DataPoint(idx=i, spPr=GraphicalProperties(solidFill=colors[i % len(colors)])))
    ch.series.append(s)
    style_chart(ch, title, size, legend=True)
    d = DataLabelList()
    d.showPercent = True
    d.showVal = d.showSerName = d.showCatName = d.showLegendKey = d.showBubbleSize = d.showLeaderLines = False
    d.txPr = _rich(TEXT_PT, st.WHITE)
    ch.dataLabels = d
    return ch


def place(ws, chart, anchor: str) -> None:
    ws.add_chart(chart, anchor)


# --------------------------------------------------------------------------- grid placement
def slot_anchor(slot: int, first_row: int, rows: int = 17, cols: tuple[str, str] = ("H", "P")) -> str:
    """Anchor of the n-th standard chart (0-based), two columns wide: left, right, then the next row."""
    return f"{cols[slot % 2]}{first_row + (slot // 2) * rows}"

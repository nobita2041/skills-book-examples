"""月次売上レポートPDF生成スクリプト"""

import csv
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie

# 日本語フォント登録
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
FONT_NAME = "HeiseiKakuGo-W5"

# カラーパレット
COLOR_PRIMARY = colors.HexColor("#1a365d")
COLOR_ACCENT = colors.HexColor("#2b6cb0")
COLOR_LIGHT_BG = colors.HexColor("#ebf8ff")
COLOR_GREEN = colors.HexColor("#276749")
COLOR_RED = colors.HexColor("#c53030")
COLOR_CHART = [
    colors.HexColor("#2b6cb0"),
    colors.HexColor("#38a169"),
    colors.HexColor("#d69e2e"),
    colors.HexColor("#e53e3e"),
]


def load_csv(filepath):
    """CSVファイルを読み込んでリストで返す"""
    rows = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["販売数量"] = int(row["販売数量"])
            row["単価"] = int(row["単価"])
            row["売上金額"] = int(row["売上金額"])
            rows.append(row)
    return rows


def aggregate_by_dept(rows):
    """部門別に売上を集計"""
    dept = defaultdict(lambda: {"売上金額": 0, "販売数量": 0, "取引件数": 0})
    for r in rows:
        d = dept[r["部門"]]
        d["売上金額"] += r["売上金額"]
        d["販売数量"] += r["販売数量"]
        d["取引件数"] += 1
    return dict(dept)


def fmt_yen(n):
    """金額フォーマット"""
    return f"¥{n:,.0f}"


def fmt_pct(v):
    """パーセントフォーマット（符号付き）"""
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"


def make_styles():
    """スタイル定義"""
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "Title", fontName=FONT_NAME, fontSize=22, leading=30,
            textColor=COLOR_PRIMARY, spaceAfter=4 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", fontName=FONT_NAME, fontSize=10, leading=14,
            textColor=colors.gray, spaceAfter=8 * mm,
        ),
        "h1": ParagraphStyle(
            "H1", fontName=FONT_NAME, fontSize=16, leading=22,
            textColor=COLOR_PRIMARY, spaceBefore=6 * mm, spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "H2", fontName=FONT_NAME, fontSize=12, leading=16,
            textColor=COLOR_ACCENT, spaceBefore=4 * mm, spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "Body", fontName=FONT_NAME, fontSize=10, leading=16,
            spaceAfter=3 * mm,
        ),
        "small": ParagraphStyle(
            "Small", fontName=FONT_NAME, fontSize=8, leading=12,
            textColor=colors.gray,
        ),
    }
    return styles


def build_kpi_table(total_jan, total_dec, qty_jan, qty_dec, txn_jan, txn_dec):
    """KPIカード風テーブル"""
    def diff_color(cur, prev):
        pct = (cur - prev) / prev * 100 if prev else 0
        c = COLOR_GREEN if pct >= 0 else COLOR_RED
        return fmt_pct(pct), c

    sales_diff, sc = diff_color(total_jan, total_dec)
    qty_diff, qc = diff_color(qty_jan, qty_dec)
    txn_diff, tc = diff_color(txn_jan, txn_dec)

    data = [
        ["", "売上金額", "販売数量", "取引件数"],
        ["2025年1月", fmt_yen(total_jan), f"{qty_jan:,}", f"{txn_jan:,}"],
        ["前月比", sales_diff, qty_diff, txn_diff],
    ]

    t = Table(data, colWidths=[30 * mm, 50 * mm, 40 * mm, 35 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, 1), 11),
        ("FONTSIZE", (0, 2), (-1, 2), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), COLOR_LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    return t


def build_dept_table(dept_jan, dept_dec):
    """部門別売上テーブル"""
    header = ["部門", "売上金額", "販売数量", "取引件数", "前月比"]
    rows = [header]
    dept_order = sorted(dept_jan.keys())

    for name in dept_order:
        j = dept_jan[name]
        d = dept_dec.get(name, {"売上金額": 0})
        prev = d["売上金額"]
        pct = (j["売上金額"] - prev) / prev * 100 if prev else 0
        rows.append([
            name.replace("事業部", "\n事業部"),
            fmt_yen(j["売上金額"]),
            f'{j["販売数量"]:,}',
            f'{j["取引件数"]:,}',
            fmt_pct(pct),
        ])

    t = Table(rows, colWidths=[40 * mm, 45 * mm, 30 * mm, 28 * mm, 25 * mm])
    style_cmds = [
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_LIGHT_BG]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def build_bar_chart(dept_jan, dept_dec):
    """部門別売上 棒グラフ（当月 vs 前月）"""
    drawing = Drawing(450, 200)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 30
    chart.width = 360
    chart.height = 150

    dept_order = sorted(dept_jan.keys())
    jan_vals = [dept_jan[d]["売上金額"] / 10000 for d in dept_order]
    dec_vals = [dept_dec.get(d, {"売上金額": 0})["売上金額"] / 10000 for d in dept_order]

    chart.data = [jan_vals, dec_vals]
    chart.categoryAxis.categoryNames = [
        d.replace("事業部", "") for d in dept_order
    ]
    chart.categoryAxis.labels.fontName = FONT_NAME
    chart.categoryAxis.labels.fontSize = 8
    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontName = FONT_NAME
    chart.valueAxis.labels.fontSize = 8
    chart.valueAxis.labelTextFormat = "%d万"
    chart.bars[0].fillColor = COLOR_CHART[0]
    chart.bars[1].fillColor = COLOR_CHART[2]
    chart.barWidth = 12
    chart.groupSpacing = 15

    # 凡例テキスト
    drawing.add(chart)
    drawing.add(String(80, 188, "■ 2025年1月", fontName=FONT_NAME, fontSize=8,
                        fillColor=COLOR_CHART[0]))
    drawing.add(String(200, 188, "■ 2024年12月", fontName=FONT_NAME, fontSize=8,
                        fillColor=COLOR_CHART[2]))
    return drawing


def build_pie_chart(dept_jan):
    """部門別構成比 円グラフ"""
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.x = 100
    pie.y = 20
    pie.width = 160
    pie.height = 160

    dept_order = sorted(dept_jan.keys())
    pie.data = [dept_jan[d]["売上金額"] for d in dept_order]
    pie.labels = [d.replace("事業部", "") for d in dept_order]

    for i, c in enumerate(COLOR_CHART[:len(dept_order)]):
        pie.slices[i].fillColor = c
        pie.slices[i].fontName = FONT_NAME
        pie.slices[i].fontSize = 8
        pie.slices[i].labelRadius = 1.3

    drawing.add(pie)
    return drawing


def build_comparison_table(dept_jan, dept_dec):
    """前月比較 詳細テーブル"""
    header = ["部門", "2024年12月", "2025年1月", "増減額", "増減率"]
    rows = [header]
    dept_order = sorted(dept_jan.keys())
    total_jan = total_dec = 0

    for name in dept_order:
        j = dept_jan[name]["売上金額"]
        d = dept_dec.get(name, {"売上金額": 0})["売上金額"]
        diff = j - d
        pct = (diff / d * 100) if d else 0
        total_jan += j
        total_dec += d
        rows.append([
            name.replace("事業部", "\n事業部"),
            fmt_yen(d),
            fmt_yen(j),
            fmt_yen(diff),
            fmt_pct(pct),
        ])

    # 合計行
    diff_total = total_jan - total_dec
    pct_total = (diff_total / total_dec * 100) if total_dec else 0
    rows.append([
        "合計",
        fmt_yen(total_dec),
        fmt_yen(total_jan),
        fmt_yen(diff_total),
        fmt_pct(pct_total),
    ])

    t = Table(rows, colWidths=[40 * mm, 38 * mm, 38 * mm, 32 * mm, 22 * mm])
    n_rows = len(rows)
    style_cmds = [
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, n_rows - 1), (-1, n_rows - 1), COLOR_LIGHT_BG),
        ("LINEABOVE", (0, n_rows - 1), (-1, n_rows - 1), 1.5, COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def main():
    jan_data = load_csv("sales_202501.csv")
    dec_data = load_csv("sales_202412.csv")

    dept_jan = aggregate_by_dept(jan_data)
    dept_dec = aggregate_by_dept(dec_data)

    total_jan = sum(r["売上金額"] for r in jan_data)
    total_dec = sum(r["売上金額"] for r in dec_data)
    qty_jan = sum(r["販売数量"] for r in jan_data)
    qty_dec = sum(r["販売数量"] for r in dec_data)
    txn_jan = len(jan_data)
    txn_dec = len(dec_data)

    styles = make_styles()
    outfile = "sales_report_202501.pdf"

    doc = SimpleDocTemplate(
        outfile, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    story = []

    # --- タイトル ---
    story.append(Paragraph("2025年1月 売上レポート", styles["title"]))
    story.append(Paragraph("作成日: 2025年2月  |  対象期間: 2025年1月1日 〜 1月31日", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=6 * mm))

    # --- 1. 概要 ---
    story.append(Paragraph("1. 概要", styles["h1"]))
    story.append(Paragraph(
        f"2025年1月の売上合計は <b>{fmt_yen(total_jan)}</b> でした。"
        f"前月（2024年12月）の <b>{fmt_yen(total_dec)}</b> と比較して"
        f" <b>{fmt_pct((total_jan - total_dec) / total_dec * 100)}</b> の変動です。",
        styles["body"],
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(build_kpi_table(total_jan, total_dec, qty_jan, qty_dec, txn_jan, txn_dec))
    story.append(Spacer(1, 6 * mm))

    # --- 2. 部門別売上 ---
    story.append(Paragraph("2. 部門別売上", styles["h1"]))
    story.append(Paragraph(
        "各事業部の売上実績と前月比を以下に示します。",
        styles["body"],
    ))
    story.append(build_dept_table(dept_jan, dept_dec))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("部門別売上比較（万円）", styles["h2"]))
    story.append(build_bar_chart(dept_jan, dept_dec))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("部門別構成比", styles["h2"]))
    story.append(build_pie_chart(dept_jan))

    story.append(PageBreak())

    # --- 3. 前月比較 ---
    story.append(Paragraph("3. 前月比較", styles["h1"]))
    story.append(Paragraph(
        "2024年12月と2025年1月の部門別売上を比較します。",
        styles["body"],
    ))
    story.append(build_comparison_table(dept_jan, dept_dec))
    story.append(Spacer(1, 6 * mm))

    # 部門ごとのコメント
    story.append(Paragraph("主なポイント", styles["h2"]))
    dept_order = sorted(dept_jan.keys())
    for name in dept_order:
        j = dept_jan[name]["売上金額"]
        d = dept_dec.get(name, {"売上金額": 0})["売上金額"]
        diff = j - d
        pct = (diff / d * 100) if d else 0
        arrow = "増加" if pct >= 0 else "減少"
        story.append(Paragraph(
            f"<b>{name}</b>: {fmt_yen(j)}（前月比 {fmt_pct(pct)}, {fmt_yen(abs(diff))} {arrow}）",
            styles["body"],
        ))

    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceAfter=3 * mm))
    story.append(Paragraph("※ 本レポートは sales_202501.csv および sales_202412.csv から自動生成されています。", styles["small"]))

    doc.build(story)
    print(f"PDF generated: {outfile}")


if __name__ == "__main__":
    main()

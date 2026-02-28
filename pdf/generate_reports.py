"""月次売上レポートPDF生成スクリプト (report_01.pdf, report_02.pdf)"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

# 日本語フォント登録
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
FONT = "HeiseiKakuGo-W5"

# カラーパレット
DARK_BLUE = colors.HexColor("#1a365d")
MEDIUM_BLUE = colors.HexColor("#2b6cb0")
LIGHT_BLUE = colors.HexColor("#bee3f8")
LIGHT_GRAY = colors.HexColor("#f7fafc")
BORDER_GRAY = colors.HexColor("#e2e8f0")


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "JTitle",
            fontName=FONT,
            fontSize=22,
            leading=30,
            textColor=DARK_BLUE,
            spaceAfter=6 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "JSubtitle",
            fontName=FONT,
            fontSize=12,
            leading=16,
            textColor=MEDIUM_BLUE,
            spaceAfter=12 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "JHeading",
            fontName=FONT,
            fontSize=14,
            leading=20,
            textColor=DARK_BLUE,
            spaceBefore=8 * mm,
            spaceAfter=4 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "JBody",
            fontName=FONT,
            fontSize=10,
            leading=16,
            spaceAfter=3 * mm,
        )
    )
    return styles


def header_footer(canvas, doc, title):
    canvas.saveState()
    # ヘッダー線
    canvas.setStrokeColor(MEDIUM_BLUE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, A4[1] - 15 * mm, A4[0] - 20 * mm, A4[1] - 15 * mm)
    # ヘッダーテキスト
    canvas.setFont(FONT, 8)
    canvas.setFillColor(MEDIUM_BLUE)
    canvas.drawString(20 * mm, A4[1] - 13 * mm, title)
    # フッター
    canvas.setStrokeColor(BORDER_GRAY)
    canvas.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    canvas.setFillColor(colors.gray)
    canvas.setFont(FONT, 8)
    canvas.drawCentredString(A4[0] / 2, 10 * mm, f"- {doc.page} -")
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, "TechVision株式会社")
    canvas.restoreState()


def make_table(headers, rows):
    data = [headers] + rows
    col_count = len(headers)
    col_width = (A4[0] - 40 * mm) / col_count

    t = Table(data, colWidths=[col_width] * col_count)
    style_commands = [
        # ヘッダー
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
    ]
    # 偶数行の背景色
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY))
    t.setStyle(TableStyle(style_commands))
    return t


def build_report(filename, month_label, year_month, data):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )
    styles = get_styles()
    story = []

    title_text = f"{year_month} 売上レポート"

    # --- タイトルページ ---
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph(title_text, styles["JTitle"]))
    story.append(Paragraph("TechVision株式会社", styles["JSubtitle"]))
    story.append(Spacer(1, 20 * mm))

    # 概要ボックス的にテキストで表現
    story.append(Paragraph("レポート概要", styles["JHeading"]))
    story.append(
        Paragraph(f"対象期間: {year_month}", styles["JBody"])
    )
    story.append(
        Paragraph(f"全社売上合計: {data['total']:,}円", styles["JBody"])
    )
    if data.get("prev_diff"):
        story.append(
            Paragraph(
                f"前月比: {data['prev_diff']}",
                styles["JBody"],
            )
        )
    story.append(
        Paragraph(f"部門数: {len(data['departments'])}部門", styles["JBody"])
    )

    story.append(PageBreak())

    # --- 部門別売上 ---
    story.append(Paragraph("部門別売上", styles["JHeading"]))
    story.append(
        Paragraph(
            f"　{month_label}の部門別売上実績をまとめます。",
            styles["JBody"],
        )
    )

    headers = ["部門", "売上金額", "構成比"]
    rows = []
    for dept in data["departments"]:
        ratio = dept["amount"] / data["total"] * 100
        rows.append(
            [dept["name"], f"{dept['amount']:,}円", f"{ratio:.1f}%"]
        )
    rows.append(["合計", f"{data['total']:,}円", "100.0%"])

    story.append(make_table(headers, rows))
    story.append(Spacer(1, 6 * mm))

    # --- 商品別売上 TOP5 ---
    story.append(Paragraph("商品別売上 TOP5", styles["JHeading"]))
    story.append(
        Paragraph(
            f"　{month_label}に最も売上が高かった商品のランキングです。",
            styles["JBody"],
        )
    )

    top_headers = ["順位", "商品名", "部門", "売上金額"]
    top_rows = []
    for i, item in enumerate(data["top_products"], 1):
        top_rows.append(
            [str(i), item["name"], item["dept"], f"{item['amount']:,}円"]
        )
    story.append(make_table(top_headers, top_rows))

    # ビルド
    doc.build(
        story,
        onFirstPage=lambda c, d: header_footer(c, d, title_text),
        onLaterPages=lambda c, d: header_footer(c, d, title_text),
    )
    print(f"Generated: {filename}")


def main():
    # --- 1月データ ---
    jan_data = {
        "total": 287_450_000,
        "prev_diff": "+8.3%（12月比）",
        "departments": [
            {"name": "コンシューマー事業部", "amount": 98_200_000},
            {"name": "エンタープライズ事業部", "amount": 82_500_000},
            {"name": "クラウドサービス事業部", "amount": 67_350_000},
            {"name": "デバイス事業部", "amount": 39_400_000},
        ],
        "top_products": [
            {"name": "クラウドERP Standard", "dept": "エンタープライズ事業部", "amount": 32_800_000},
            {"name": "スマートウォッチ Pro", "dept": "コンシューマー事業部", "amount": 27_150_000},
            {"name": "AI分析プラットフォーム", "dept": "クラウドサービス事業部", "amount": 24_600_000},
            {"name": "ワイヤレスイヤホン Elite", "dept": "コンシューマー事業部", "amount": 21_900_000},
            {"name": "セキュリティGateway X1", "dept": "エンタープライズ事業部", "amount": 18_750_000},
        ],
    }

    # --- 2月データ ---
    feb_data = {
        "total": 312_800_000,
        "prev_diff": "+8.8%（1月比）",
        "departments": [
            {"name": "コンシューマー事業部", "amount": 105_600_000},
            {"name": "エンタープライズ事業部", "amount": 91_200_000},
            {"name": "クラウドサービス事業部", "amount": 72_400_000},
            {"name": "デバイス事業部", "amount": 43_600_000},
        ],
        "top_products": [
            {"name": "クラウドERP Standard", "dept": "エンタープライズ事業部", "amount": 36_400_000},
            {"name": "AI分析プラットフォーム", "dept": "クラウドサービス事業部", "amount": 28_900_000},
            {"name": "スマートウォッチ Pro", "dept": "コンシューマー事業部", "amount": 28_200_000},
            {"name": "ワイヤレスイヤホン Elite", "dept": "コンシューマー事業部", "amount": 24_300_000},
            {"name": "統合監視ダッシュボード", "dept": "クラウドサービス事業部", "amount": 19_800_000},
        ],
    }

    build_report("report_01.pdf", "1月", "2025年1月", jan_data)
    build_report("report_02.pdf", "2月", "2025年2月", feb_data)


if __name__ == "__main__":
    main()

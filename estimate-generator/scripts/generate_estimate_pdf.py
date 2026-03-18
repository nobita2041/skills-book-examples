#!/usr/bin/env python3
"""見積書PDF生成スクリプト

Usage:
    uv run --with weasyprint python generate_estimate_pdf.py input.json [output.pdf]
"""

import json
import sys
from pathlib import Path


def format_currency(amount: int) -> str:
    """金額をカンマ区切りでフォーマット"""
    return f"¥{amount:,}"


def generate_html(data: dict) -> str:
    """見積書のHTMLを生成"""
    # 品目の計算
    items = data.get("items", [])
    subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
    tax_rate = data.get("tax_rate", 0.10)
    tax = int(subtotal * tax_rate)
    total = subtotal + tax

    # 日付
    estimate_date = data.get("date", "")
    valid_until = data.get("valid_until", "")

    # 品目行のHTML
    items_html = ""
    for i, item in enumerate(items, 1):
        amount = item["quantity"] * item["unit_price"]
        items_html += f"""
            <tr>
                <td class="center">{i}</td>
                <td>{item["name"]}</td>
                <td class="right">{item["quantity"]}</td>
                <td class="center">{item.get("unit", "式")}</td>
                <td class="right">{format_currency(item["unit_price"])}</td>
                <td class="right">{format_currency(amount)}</td>
            </tr>"""

    # 品目が少ない場合のみ空行を追加（A4に収まる範囲で）
    if len(items) < 6:
        empty_rows_needed = 6 - len(items)
        for _ in range(empty_rows_needed):
            items_html += """
            <tr class="empty-row">
                <td>&nbsp;</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>"""

    # 会社情報
    company = data.get("company", {})
    company_name = company.get("name", "株式会社技術評論デザイン")
    company_address = company.get("address", "東京都新宿区市谷左内町xx-xx")
    company_tel = company.get("tel", "03-XXXX-XXXX")
    company_email = company.get("email", "info@gijutsu-design.example.com")

    # クライアント情報
    client_name = data.get("client_name", "")
    client_address = data.get("client_address", "")
    client_person = data.get("client_person", "")

    # プロジェクト情報
    project_name = data.get("project_name", "")
    estimate_number = data.get("estimate_number", "")

    # 振込先
    bank = data.get("bank", {})
    bank_html = ""
    if bank:
        bank_html = f"""
        <div class="section">
            <div class="section-title">お振込先</div>
            <div class="section-body">
                <p>{bank.get("bank_name", "○○銀行")} {bank.get("branch_name", "○○支店")} {bank.get("account_type", "普通")} {bank.get("account_number", "XXXXXXX")}</p>
                <p>口座名義: {bank.get("account_holder", company_name)}</p>
            </div>
        </div>"""

    # 備考
    notes = data.get("notes", "")
    notes_html = ""
    if notes:
        notes_html = f"""
        <div class="section">
            <div class="section-title">備考</div>
            <div class="section-body"><p>{notes}</p></div>
        </div>"""

    # クライアント住所・担当者
    client_address_html = f'<p class="client-address">{client_address}</p>' if client_address else ""
    client_person_html = f'<p class="client-person">{client_person} 様</p>' if client_person else ""

    # 件名
    project_html = f'<div class="project-name">件名: {project_name}</div>' if project_name else ""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
    @page {{
        size: A4;
        margin: 18mm 15mm 15mm 15mm;
    }}
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    body {{
        font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic", "Meiryo", sans-serif;
        font-size: 9.5pt;
        color: #222;
        line-height: 1.5;
    }}

    /* ヘッダー */
    .header {{
        text-align: center;
        margin-bottom: 24px;
    }}
    .header h1 {{
        font-size: 22pt;
        font-weight: 700;
        letter-spacing: 0.6em;
        padding-bottom: 6px;
        border-bottom: 3px double #333;
        display: inline-block;
    }}

    /* メタ情報セクション */
    .meta {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
    }}
    .client-info {{
        flex: 1;
        padding-right: 30px;
    }}
    .client-name {{
        font-size: 14pt;
        font-weight: 700;
        border-bottom: 1px solid #333;
        padding-bottom: 4px;
        margin-bottom: 6px;
    }}
    .client-name .honorific {{
        font-size: 11pt;
        font-weight: normal;
        margin-left: 8px;
    }}
    .client-address {{
        font-size: 9pt;
        color: #555;
        margin-bottom: 2px;
    }}
    .client-person {{
        font-size: 9.5pt;
        margin-top: 4px;
    }}

    .estimate-meta {{
        text-align: right;
        font-size: 9pt;
        white-space: nowrap;
    }}
    .estimate-meta table {{
        margin-left: auto;
        border-collapse: collapse;
    }}
    .estimate-meta td {{
        padding: 2px 0 2px 12px;
    }}
    .estimate-meta td:first-child {{
        font-weight: 600;
        text-align: right;
        padding-right: 8px;
        padding-left: 0;
    }}

    /* 合計金額ボックス */
    .total-box {{
        border: 2px solid #333;
        padding: 10px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: baseline;
        justify-content: center;
        gap: 12px;
        background: #fafafa;
    }}
    .total-box .label {{
        font-size: 11pt;
        font-weight: 600;
    }}
    .total-box .amount {{
        font-size: 20pt;
        font-weight: 700;
    }}
    .total-box .tax-note {{
        font-size: 9pt;
        color: #666;
    }}

    /* 件名 */
    .project-name {{
        margin-bottom: 12px;
        font-size: 10pt;
        font-weight: 600;
    }}

    /* 品目テーブル */
    table.items {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 8px;
    }}
    table.items th {{
        background: #3a3a3a;
        color: #fff;
        padding: 7px 8px;
        font-size: 8.5pt;
        font-weight: 500;
        text-align: center;
    }}
    table.items td {{
        padding: 6px 8px;
        border-bottom: 1px solid #e0e0e0;
        font-size: 9pt;
    }}
    table.items tbody tr:nth-child(even) {{
        background: #f8f8f8;
    }}
    .right {{
        text-align: right;
    }}
    .center {{
        text-align: center;
    }}

    /* 小計・税・合計 */
    .summary-wrap {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }}
    .summary {{
        width: 260px;
    }}
    .summary table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .summary td {{
        padding: 5px 8px;
        font-size: 9.5pt;
        border-bottom: 1px solid #ddd;
    }}
    .summary tr.total-row td {{
        border-top: 2px solid #333;
        border-bottom: 2px solid #333;
        font-weight: 700;
        font-size: 11pt;
        padding: 7px 8px;
    }}

    /* 振込先・備考 */
    .section {{
        margin-bottom: 12px;
    }}
    .section-title {{
        font-size: 9pt;
        font-weight: 600;
        background: #f0f0f0;
        padding: 4px 8px;
        border-left: 3px solid #3a3a3a;
        margin-bottom: 6px;
    }}
    .section-body {{
        padding-left: 11px;
        font-size: 9pt;
    }}
    .section-body p {{
        margin: 2px 0;
    }}

    /* 発行元情報 */
    .company-section {{
        margin-top: 20px;
        border-top: 1px solid #ccc;
        padding-top: 10px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 20px;
    }}
    .company-detail {{
        text-align: right;
    }}
    .company-name-footer {{
        font-size: 12pt;
        font-weight: 700;
        margin-bottom: 3px;
    }}
    .company-detail p {{
        font-size: 8.5pt;
        color: #555;
        margin: 1px 0;
    }}
    .stamp {{
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 1px dashed #bbb;
        border-radius: 50%;
        line-height: 50px;
        text-align: center;
        font-size: 8pt;
        color: #bbb;
        flex-shrink: 0;
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>見 積 書</h1>
    </div>

    <div class="meta">
        <div class="client-info">
            <div class="client-name">
                {client_name}<span class="honorific">御中</span>
            </div>
            {client_address_html}
            {client_person_html}
        </div>
        <div class="estimate-meta">
            <table>
                <tr><td>見積番号</td><td>{estimate_number}</td></tr>
                <tr><td>見積日</td><td>{estimate_date}</td></tr>
                <tr><td>有効期限</td><td>{valid_until}</td></tr>
            </table>
        </div>
    </div>

    <div class="total-box">
        <span class="label">合計金額</span>
        <span class="amount">{format_currency(total)}</span>
        <span class="tax-note">（税込）</span>
    </div>

    {project_html}

    <table class="items">
        <thead>
            <tr>
                <th style="width:5%">No.</th>
                <th style="width:38%">品目</th>
                <th style="width:9%">数量</th>
                <th style="width:9%">単位</th>
                <th style="width:17%">単価</th>
                <th style="width:22%">金額</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>

    <div class="summary-wrap">
        <div class="summary">
            <table>
                <tr>
                    <td class="right">小計</td>
                    <td class="right">{format_currency(subtotal)}</td>
                </tr>
                <tr>
                    <td class="right">消費税（{int(tax_rate * 100)}%）</td>
                    <td class="right">{format_currency(tax)}</td>
                </tr>
                <tr class="total-row">
                    <td class="right">合計</td>
                    <td class="right">{format_currency(total)}</td>
                </tr>
            </table>
        </div>
    </div>

    {bank_html}
    {notes_html}

    <div class="company-section">
        <div class="company-detail">
            <div class="company-name-footer">{company_name}</div>
            <p>{company_address}</p>
            <p>TEL: {company_tel}</p>
            <p>Email: {company_email}</p>
        </div>
        <div class="stamp">印</div>
    </div>
</body>
</html>"""
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_estimate_pdf.py input.json [output.pdf]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".pdf")

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    html = generate_html(data)

    # HTMLファイルも保存（フォールバック用）
    html_path = output_file.with_suffix(".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(str(output_file))
        print(f"PDF生成完了: {output_file}")
    except ImportError:
        print(f"weasyprint が見つかりません。HTMLファイルを保存しました: {html_path}")
        print("PDF生成するには: uv run --with weasyprint python generate_estimate_pdf.py input.json")
        sys.exit(1)
    except Exception as e:
        print(f"PDF生成でエラーが発生しました: {e}")
        print(f"HTMLファイルは保存済みです: {html_path}")
        print("ブラウザでHTMLを開き「PDFとして印刷」で代用できます。")
        sys.exit(1)


if __name__ == "__main__":
    main()

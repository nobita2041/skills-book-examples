# skills-book-examples

「Agent Skills入門」書籍のサンプルスキル集です。

## スキル一覧

| スキル | 概要 | 登場章 |
|--------|------|--------|
| [weekly-report](./weekly-report/) | 製造業向け週報（グラフ付きHTMLレポート） | 第3章 |

## インストール方法

```bash
git clone https://github.com/nobita2041/skills-book-examples.git
cp -r skills-book-examples/weekly-report ~/.claude/skills/
```

インストール後、Claude Codeを再起動してください。

```bash
/exit
claude
```

`/skills` コマンドで `weekly-report` が表示されればインストール完了です。

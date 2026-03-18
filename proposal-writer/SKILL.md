---
name: proposal-writer
description: Create structured project proposals and planning documents in Japanese. Use this skill whenever the user wants to write a proposal (企画書), project plan (プロジェクト計画書), business case, or planning document — even if they just say something like "新機能のアイデアをまとめたい" or "このプロジェクトを提案したい". Also trigger when the user mentions 企画, 提案書, 稟議, or asks to organize project ideas into a formal document.
---

# Proposal Writer（企画書作成）

プロジェクト企画書を構造化されたMarkdownドキュメントとして作成するスキルです。

## いつ使うか

- ユーザーが企画書、提案書、プロジェクト計画書の作成を求めたとき
- 「アイデアをまとめたい」「プロジェクトを提案したい」と言われたとき
- 稟議書や事業計画の下書きが必要なとき

## 企画書の作成手順

### Step 1: ヒアリング

企画書を書く前に、以下の情報を確認する。ユーザーがすでに会話の中で述べている内容は再度聞かない。不足している項目だけを質問する。

1. **プロジェクト名**: 仮タイトルでもよい
2. **背景・課題**: なぜこの企画が必要か
3. **ターゲット**: 誰に向けたものか
4. **ゴール**: 何を達成したいか
5. **想定スケジュール**: 大まかな期間
6. **予算規模**: 概算でよい（不明なら「未定」）
7. **読み手**: 企画書の提出先（経営層、チームリーダー等）

すべてが揃わなくても構わない。最低限「背景・課題」と「ゴール」があれば着手できる。

### Step 2: 企画書の作成

`references/template.md` を読み、テンプレートに沿って企画書を作成する。

**重要なポイント:**

- 読み手に合わせた粒度で書く。経営層向けなら要点を簡潔に、実務者向けなら詳細に
- 数値や根拠を可能な限り含める。「多くの」ではなく「約30%の」のように具体的に
- 各セクションは独立して読めるようにする。前のセクションを読まないと理解できない書き方は避ける
- 箇条書きと文章を適切に使い分ける。概要は文章で、詳細項目は箇条書きで

### Step 3: 出力

- ファイル名は `proposal-{プロジェクト名の英語略称}.md` とする
- 作成後、企画書の概要を1-2文で伝え、レビューポイントがあれば添える

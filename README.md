# AI News JP Slack Bot - 日本のAIニュース配信ボット

日本のAI関連ニュースを収集、要約し、Slackチャンネルで共有する包括的なSlackボットです。

A comprehensive Slack bot that collects, summarizes, and shares Japanese AI-related news from various Japanese web sources and social media platforms.

## 特徴 (Features)

🇯🇵 **日本語専用**: 日本のAIニュースのみを収集  
📰 **複数のソース**: 日本の主要なニュースサイト、RSS フィード、ソーシャルメディアから情報を集約  
📝 **AI要約**: OpenAI GPTを使用して記事を日本語で自動要約  
🏷️ **スマートタグ付け**: 関連するキーワードで記事を自動的にタグ付け  
🔍 **検索機能**: タグやキーワードで収集した記事を検索  
📅 **スケジュール収集**: 指定された間隔で自動実行  
💬 **Slack統合**: 要約をSlackチャンネルに直接投稿  
🗄️ **データベース保存**: 記事、要約、タグを将来の参照用に保存  

## アーキテクチャ (Architecture)

```
ai-news-jp-slack-bot/
├── src/
│   ├── collectors/          # ニュース収集モジュール
│   ├── processors/          # テキスト処理と要約
│   ├── database/           # データベースモデルと操作
│   ├── slack/              # Slackボット統合
│   └── utils/              # ユーティリティ関数
├── config/                 # 設定ファイル
├── data/                   # ローカルデータストレージ
├── tests/                  # ユニットテスト
└── requirements.txt        # Python依存関係
```

## クイックスタート (Quick Start)

### 前提条件 (Prerequisites)

✅ Python 3.8+  
✅ Slackワークスペースとボット権限  
✅ OpenAI APIキー（要約用）  
✅ SQLite（Pythonに含まれています）  

### インストール (Installation)

1. プロジェクトに移動:
```bash
cd ai-news-jp-slack-bot
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

3. 設定をセットアップ:
```bash
cp config/config.example.yaml config/config.yaml
# config/config.yamlをAPIキーと設定で編集
```

4. データベースを初期化:
```bash
python src/database/init_db.py
```

5. ボットを実行:
```bash
python main.py
```

## 設定 (Configuration)

`config/config.yaml`を編集してカスタマイズ:

📱 **Slack設定**: ボットトークン、チャンネル（#times-mayo）、投稿頻度  
📰 **ニュースソース**: 日本のRSSフィード、ウェブサイト、ソーシャルメディアアカウント  
🤖 **AI設定**: OpenAI APIキー、要約設定  
🏷️ **タグ付けルール**: カスタムタグパターンとキーワード  
📅 **スケジュール**: 収集頻度とタイミング  

## 使用方法 (Usage)

### Slackコマンド (Slack Commands)

📝 `/ai-news search <キーワード>` - キーワードで記事を検索  
🏷️ `/ai-news tags` - 利用可能なタグを一覧表示  
📰 `/ai-news latest` - 最新の収集記事を表示  
📡 `/ai-news sources` - 設定されたニュースソースを一覧表示  
📊 `/ai-news stats` - 収集統計を表示  

### 手動収集 (Manual Collection)

```bash
# すぐにニュースを収集
python main.py --collect-now

# 特定のソースから収集
python main.py --source "ITmedia AI+"

# 日本語のみ収集（デフォルト）
python main.py --language japanese
```

## サポートされているソース (Supported Sources)

### 日本のニュースサイト (Japanese News Sites)
✅ ITmedia AI+  
✅ ASCII.jp AI  
✅ 日経xTECH AI  
✅ Impress Watch AI  
✅ マイナビニュース AI  
✅ CNET Japan AI  
✅ ZDNet Japan AI  
✅ 週刊アスキー AI  

### 日本のAI企業・研究機関 (Japanese AI Companies & Research)
✅ Preferred Networks  
✅ RIKEN AIP（理化学研究所）  
✅ リンナ株式会社  
✅ 東京大学 AI研究  

### ソーシャルメディア (Social Media)
✅ 日本のAI企業Twitterアカウント  
✅ 日本の研究機関アカウント  
✅ 日本のAI研究者アカウント  

## カスタマイズ (Customization)

### 新しいソースの追加 (Adding New Sources)

1. `src/collectors/`に新しいコレクターを作成
2. `BaseCollector`インターフェースを実装
3. `config/config.yaml`にソース設定を追加
4. `main.py`にコレクターを登録

### カスタムタグ付けルール (Custom Tagging Rules)

`config/config.yaml`でカスタムタグパターンを追加:

```yaml
tagging:
  categories:
    technology:
      keywords: ["機械学習", "深層学習", "ニューラルネットワーク", "生成AI"]
      weight: 1.0
    
    companies:
      keywords: ["プリファード", "リンナ", "ソフトバンク", "NTT"]
      weight: 0.8
```

## データベーススキーマ (Database Schema)

ボットは以下の主要テーブルでSQLiteを使用:

📄 `articles`: メタデータ付きの元記事を保存  
📝 `summaries`: AI生成の要約  
🏷️ `tags`: 記事のタグとカテゴリ  
📡 `sources`: ニュースソース設定  
📊 `collection_logs`: 収集履歴と統計  

## API統合 (API Integration)

### OpenAI統合 (OpenAI Integration)
🤖 記事要約にGPT-4を使用  
🇯🇵 日本語テキストをサポート  
⚙️ 設定可能なプロンプトテンプレート  

### Slack API
🔑 ボットユーザーOAuthトークンが必要  
🔐 必要な権限: `chat:write`, `commands`, `channels:read`  
💬 インタラクティブコンポーネントとスラッシュコマンドをサポート  

## モニタリングとログ (Monitoring and Logging)

📁 `logs/`ディレクトリへの包括的なログ  
📊 収集統計と成功率  
🚨 エラー追跡と通知  
⚡ パフォーマンスメトリクス  

## ドキュメント (Documentation)

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - ステップバイステップの設定手順
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 一般的な問題の包括的なトラブルシューティングガイド
- **[MACOS_SERVICE_GUIDE.md](MACOS_SERVICE_GUIDE.md)** - macOSサービスのセットアップと管理
- **[IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)** - 技術実装の詳細とパフォーマンス最適化
- **[DOCS.md](DOCS.md)** - ドキュメントインデックスとクイックリファレンス

## サポート (Support)

問題や質問については:
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** で一般的な問題と解決策を確認
- `logs/`ディレクトリのログを確認
- デバッグモードで実行: `python main.py --debug`
- 接続をテスト: `python main.py --test`

## クイックトラブルシューティング (Quick Troubleshooting)

### 最も一般的な問題 (Most Common Issues)

1. **スラッシュコマンドが応答しない**: 通常は`chat:write`スコープが不足 - [TROUBLESHOOTING.md](TROUBLESHOOTING.md#slack-token-and-scope-issues)を参照
2. **記事が収集されない**: インターネット接続とRSSフィードのアクセス可能性を確認
3. **サービスが開始しない**: 設定ファイルが存在し、APIキーが有効であることを確認

### デバッグコマンド (Debug Commands)

```bash
# すべての接続をテスト
python main.py --test

# デバッグログで実行
python main.py --collect-now --debug

# 重複をチェック
python check_duplicates.py

# データベースの内容を表示
python view_database.py
```

## ライセンス (License)

MIT License - 詳細はLICENSEファイルを参照

## 貢献 (Contributing)

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 新機能のテストを追加
4. プルリクエストを送信

---

**日本のAIエコシステムの最新情報をお楽しみください！** 🇯🇵🤖

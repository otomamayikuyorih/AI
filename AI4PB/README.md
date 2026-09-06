# 🎓 Stanford AI4PB Research Agent (Google Cloud Agentic AI Hackathon)

Stanford University の **AI for Public Benefit Lab (AI4PB)** をテーマに、自律的な研究調査、論文検索、情報ギャップ評価、再現実験ガイドの提示を行う **Agentic AI リサーチエージェント** です。

---

## 🌟 主な特徴

1. **自律的な Agentic Loop (7段階自律処理)**:
   - **調査計画 (Planning)**: ユーザーの自然言語クエリを分解し、スコープを自律立案。
   - **動的検索 (Search)**: AI4PB Lab のナレッジベースおよび **arXiv API** を動的検索。
   - **ギャップ評価 (Gap Analysis)**: アブストラクト情報から充足度を自己判定し、本文深掘りの要否を判断。
   - **論文本文取得 (Full-Text Retrieval)**: ar5iv / arXiv HTML から論文の Introduction, Methods, Results 本文を自動スクレイピング・精読。
   - **プロトコル特定 (Protocol Search)**: 実験設計、プロンプト構成、再現性手順を抽出。
   - **レポート統合 (Synthesis)**: 本文エビデンスを反映した学術的・実践的レポートを執筆。
   - **セッション記録 (BigQuery Logging)**: 全調査イベントとレポートを **Google Cloud BigQuery** に自動ストリーミング保存。

2. **Google Cloud ネイティブ アーキテクチャ**:
   - **Vertex AI (Gemini 2.5 Flash)**: 高速・高精度な自律推論による計画・ギャップ分析・レポート執筆。
   - **Google Cloud BigQuery**: 調査履歴、ツール呼び出しログ、生成レポートを分析用テーブル（`research_sessions`）に永続化。
   - **Google Cloud Run**: コンテナ化された Streamlit Web UI をフルマネージド・自動スケーリング環境で本番公開中。

3. **思考プロセスの可視化**:
   - Agent が裏でどのような Tool を使い、何を観察（Observation）し、どう判断したかを UI 上でリアルタイムに追跡可能。

---

## 🌐 本番公開 URL (Live Demo)

- **Cloud Run Service**: [https://ai4pb-research-agent-121643671058.us-central1.run.app](https://ai4pb-research-agent-121643671058.us-central1.run.app)
- **GCP Project**: `stable-century-479407-m7`
- **Region**: `us-central1`

---

## 📁 ディレクトリ構成

```text
AI4PB/
├── app.py                 # Streamlit Web UI (思考プロセスリアルタイム可視化)
├── agent.py               # 7段階 Agentic リサーチループ実装
├── tools.py               # arXiv API検索・ar5iv本文抽出・再現性プロトコル取得 Tools
├── bq_logger.py           # Google Cloud BigQuery REST API ロギング
├── ai4pb_data.py          # Stanford AI4PB Lab 論文・実験プロトコルデータ
├── config.py              # GCP Project, Vertex AI モデル (gemini-2.5-flash) 設定
├── requirements.txt       # 依存パッケージ (streamlit, google-genai, etc.)
├── Dockerfile             # Cloud Run デプロイ用コンテナ設定
├── .dockerignore          # コンテナ除外設定
├── .gitignore             # Git 除外設定
├── .env.example           # 環境変数テンプレート
└── README.md              # 本ドキュメント
```

---

## 🚀 ローカルでの動作確認手順

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
```bash
# Windows PowerShell
$env:GOOGLE_CLOUD_PROJECT="stable-century-479407-m7"
$env:GEMINI_MODEL="gemini-2.5-flash"
```

### 3. Streamlit アプリの起動
```bash
streamlit run app.py
```
ブラウザで `http://localhost:8501` が開き、Web UI が利用可能になります。

---

## ☁️ Google Cloud Run へのデプロイ手順

ソースコードのあるディレクトリから直接ビルド・デプロイします:

```bash
gcloud run deploy ai4pb-research-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=stable-century-479407-m7,GEMINI_MODEL=gemini-2.5-flash
```

---

## 💡 ハッカソンでのデモ・想定質問例

UI 上のクイックボタンや自由入力から以下の調査を試すことができます:

1. **Synthetic Respondents の研究**:
   - *「Synthetic Respondents について AI4PB ではどんな研究が行われている？」*
   - → Robb Willer 教授らによる『Generative Agent Simulations of 1,000 People (arXiv:2411.10109)』の本文を精読し、85%の人間再現精度や3層プロンプト設計を抽出。
2. **最新テーマの整理**:
   - *「AI4PB の最近の研究テーマと成果を整理して」*
   - → 6大コアテーマ（人間シミュレーション、社会科学実験予測、有権者ガイド、AI説得ラベル、感情的幸福度、手法基準）を体系的に整理。
3. **再現実験のしやすさ**:
   - *「自分で再現実験するなら、どの研究が取り組みやすい？」*
   - → 難易度ランキング（Very Easy〜Medium）、所要時間、推奨技術スタックを提示。
4. **高度な学術比較**:
   - *「AI4PBの2025年以降の主要研究テーマを1つ選んで、代表論文、研究目的、実験デザイン、主要結果、限界を比較してください。」*
   - → Vertex AI (Gemini 2.5 Flash) が自律的に論文を選定し、指定された全観点を網羅した学術レポートを執筆。

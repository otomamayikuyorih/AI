# aidash

`bidash` の AI 拡張パッケージです。財務ダッシュボードに **Hugging Face Inference API** による生成 AI コメントを付加します。

## インストール

```r
# devtools が必要です
devtools::install_local("path/to/aidash")
```

## 使い方

```r
library(aidash)

# 1. Hugging Face API トークンを設定
#    https://huggingface.co/settings/tokens で発行（無料）
set_hf_token("hf_xxxxxxxxxxxxxxxxxxxx")

# 2. CSV を用意して実行（bidash と同じ入力形式）
create_ai_dashboard(
  pl_file      = "input_pl.csv",
  bs_file      = "input_bs.csv",
  summary_file = "input_summary.csv",
  company_name = "株式会社サンプル (1234)"
)
```

ブラウザで `ai_dashboard.html` が開き、各ページ末尾に AI コメントが表示されます。

## モデルの変更

`model_id` に任意の Hugging Face モデル ID を指定できます。

```r
create_ai_dashboard(
  company_name = "株式会社サンプル",
  model_id     = "Qwen/Qwen2.5-7B-Instruct"   # 日本語が得意なモデル
)
```

### 推奨モデル

| モデル ID | 特徴 |
|---|---|
| `mistralai/Mistral-7B-Instruct-v0.2` | デフォルト。多言語対応、無料枠あり |
| `Qwen/Qwen2.5-7B-Instruct` | 日本語の精度が高い |
| `google/gemma-2-2b-it` | 軽量・高速 |
| `meta-llama/Llama-3.2-3B-Instruct` | 要利用規約同意 |

> 無料枠のモデルは混雑時にタイムアウトすることがあります。  
> その場合はしばらく待つか、[Hugging Face Pro](https://huggingface.co/pro) へのアップグレードを検討してください。

## AI なしで生成する

`hf_token` を省略または空文字にすると、AI コメントなしでダッシュボードが生成されます。

```r
create_ai_dashboard(company_name = "株式会社サンプル", hf_token = "")
```

## 個別にコメントだけ取得する

```r
pl       <- read.csv("input_pl.csv", fileEncoding = "UTF-8-BOM", check.names = FALSE)
summary5 <- read.csv("input_summary.csv", fileEncoding = "UTF-8-BOM", check.names = FALSE)

comment <- generate_summary_comment(
  pl, summary5,
  period_prev = "2024年6月期",
  period_curr = "2025年6月期",
  model_id    = "mistralai/Mistral-7B-Instruct-v0.2",
  token       = Sys.getenv("HF_API_TOKEN")
)
cat(comment)
```

## 依存パッケージ

`httr`, `jsonlite`, `htmltools`, `rmarkdown`, `flexdashboard`, `plotly`, `dplyr`, `DT`, `pandoc`

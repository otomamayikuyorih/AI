#' AI コメント付き財務ダッシュボードを生成する
#'
#' 損益計算書・貸借対照表・複数期サマリーのCSVを読み込み、
#' Hugging Face Inference API で業績コメントを生成してから
#' インタラクティブなHTMLダッシュボードを出力します。
#'
#' @param pl_file      損益計算書CSVのパス（デフォルト: "input_pl.csv"）
#' @param bs_file      貸借対照表CSVのパス（デフォルト: "input_bs.csv"）
#' @param summary_file 複数期サマリーCSVのパス（デフォルト: "input_summary.csv"）
#' @param company_name ダッシュボードに表示する会社名
#' @param output_file  出力HTMLファイルのパス（デフォルト: "ai_dashboard.html"）
#' @param hf_token     Hugging Face API トークン。省略時は環境変数 HF_API_TOKEN
#' @param model_id     使用するHFモデルID（デフォルト: mistralai/Mistral-7B-Instruct-v0.2）
#' @param open         生成後にブラウザで開くか（デフォルト: TRUE）
#'
#' @return 出力ファイルパス（不可視）
#' @export
#'
#' @examples
#' \dontrun{
#' # トークンを設定してダッシュボード生成
#' set_hf_token("hf_xxxxxxxxxxxxxxxxxxxx")
#' create_ai_dashboard(company_name = "株式会社サンプル (1234)")
#'
#' # モデルを変更する場合
#' create_ai_dashboard(
#'   company_name = "株式会社サンプル",
#'   model_id     = "Qwen/Qwen2.5-7B-Instruct"
#' )
#' }
create_ai_dashboard <- function(
    pl_file      = "input_pl.csv",
    bs_file      = "input_bs.csv",
    summary_file = "input_summary.csv",
    company_name = "財務分析",
    output_file  = "ai_dashboard.html",
    hf_token     = Sys.getenv("HF_API_TOKEN"),
    model_id     = "mistralai/Mistral-7B-Instruct-v0.2",
    open         = TRUE
) {
  pandoc::pandoc_activate()

  pl_path      <- normalizePath(pl_file,      mustWork = TRUE)
  bs_path      <- normalizePath(bs_file,      mustWork = TRUE)
  summary_path <- normalizePath(summary_file, mustWork = TRUE)
  out_path     <- normalizePath(output_file,  mustWork = FALSE)

  pl       <- read.csv(pl_path,      fileEncoding = "UTF-8-BOM", check.names = FALSE)
  bs       <- read.csv(bs_path,      fileEncoding = "UTF-8-BOM", check.names = FALSE)
  summary5 <- read.csv(summary_path, fileEncoding = "UTF-8-BOM", check.names = FALSE)

  pl_periods  <- tail(colnames(pl)[colnames(pl) != "項目"], 2)
  period_prev <- pl_periods[1]
  period_curr <- pl_periods[2]

  fallback <- paste0(
    "（AIコメントを生成できませんでした。",
    "set_hf_token() でトークンを設定し、model_id が正しいか確認してください）"
  )

  if (nzchar(hf_token)) {
    message(sprintf("AIコメントを生成中... (model: %s)", model_id))

    ai_summary <- tryCatch(
      generate_summary_comment(pl, summary5, period_prev, period_curr, model_id, hf_token),
      error = function(e) { warning(conditionMessage(e)); NA_character_ }
    )
    ai_pl <- tryCatch(
      generate_pl_comment(pl, period_prev, period_curr, model_id, hf_token),
      error = function(e) { warning(conditionMessage(e)); NA_character_ }
    )
    ai_bs <- tryCatch(
      generate_bs_comment(bs, period_prev, period_curr, model_id, hf_token),
      error = function(e) { warning(conditionMessage(e)); NA_character_ }
    )
  } else {
    message("HF_API_TOKEN が未設定のため、AIコメントなしで生成します。")
    ai_summary <- ai_pl <- ai_bs <- NA_character_
  }

  if (is.na(ai_summary)) ai_summary <- fallback
  if (is.na(ai_pl))      ai_pl      <- fallback
  if (is.na(ai_bs))      ai_bs      <- fallback

  template <- system.file("templates", "ai_dashboard.Rmd", package = "aidash")
  if (!nzchar(template)) {
    stop("テンプレートが見つかりません。パッケージを再インストールしてください。")
  }

  message("ダッシュボードを生成中...")
  rmarkdown::render(
    input       = template,
    output_file = out_path,
    params      = list(
      pl_file      = pl_path,
      bs_file      = bs_path,
      summary_file = summary_path,
      company_name = company_name,
      model_id     = model_id,
      ai_summary   = ai_summary,
      ai_pl        = ai_pl,
      ai_bs        = ai_bs
    ),
    quiet = TRUE
  )

  message("生成完了: ", out_path)
  if (open) utils::browseURL(out_path)

  invisible(out_path)
}

#' 財務ダッシュボードを生成する
#'
#' 損益計算書・貸借対照表・複数期サマリーのCSVを読み込み、
#' インタラクティブなHTMLダッシュボードを生成します。
#'
#' @param pl_file      損益計算書CSVのパス（デフォルト: "input_pl.csv"）
#' @param bs_file      貸借対照表CSVのパス（デフォルト: "input_bs.csv"）
#' @param summary_file 複数期サマリーCSVのパス（デフォルト: "input_summary.csv"）
#' @param company_name ダッシュボードに表示する会社名
#' @param output_file  出力HTMLファイルのパス（デフォルト: "dashboard.html"）
#' @param open         生成後にブラウザで開くか（デフォルト: TRUE）
#'
#' @return 出力ファイルパス（不可視）
#' @export
#'
#' @examples
#' \dontrun{
#' # テンプレートCSVをカレントディレクトリにコピーしてから編集
#' use_templates()
#'
#' # ダッシュボード生成
#' create_dashboard(company_name = "株式会社サンプル (1234)")
#' }
create_dashboard <- function(
    pl_file      = "input_pl.csv",
    bs_file      = "input_bs.csv",
    summary_file = "input_summary.csv",
    company_name = "財務分析",
    output_file  = "dashboard.html",
    open         = TRUE
) {
  # pandoc を有効化
  pandoc::pandoc_activate()

  # テンプレート Rmd の場所
  template <- system.file("templates", "dashboard.Rmd", package = "bidash")
  if (template == "") stop("テンプレートが見つかりません。パッケージを再インストールしてください。")

  # CSVの絶対パス化
  pl_path      <- normalizePath(pl_file,      mustWork = TRUE)
  bs_path      <- normalizePath(bs_file,      mustWork = TRUE)
  summary_path <- normalizePath(summary_file, mustWork = TRUE)
  out_path     <- normalizePath(output_file,  mustWork = FALSE)

  message("ダッシュボードを生成中...")

  rmarkdown::render(
    input       = template,
    output_file = out_path,
    params      = list(
      pl_file      = pl_path,
      bs_file      = bs_path,
      summary_file = summary_path,
      company_name = company_name
    ),
    quiet = TRUE
  )

  message("生成完了: ", out_path)

  if (open) utils::browseURL(out_path)

  invisible(out_path)
}

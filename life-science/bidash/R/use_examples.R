#' サンプルデータをカレントディレクトリにコピーする
#'
#' 架空の会社「株式会社サンプルテック（9999）」の5期分ダミーデータを
#' コピーします。動作確認やフォーマット確認に使用してください。
#'
#' @param dir コピー先ディレクトリ（デフォルト: カレントディレクトリ）
#' @param overwrite 既存ファイルを上書きするか（デフォルト: FALSE）
#'
#' @return コピー先ディレクトリパス（不可視）
#' @export
#'
#' @examples
#' \dontrun{
#' # サンプルデータをコピーしてダッシュボードを生成
#' use_examples()
#' create_dashboard(company_name = "株式会社サンプルテック (9999)")
#' }
use_examples <- function(dir = ".", overwrite = FALSE) {
  files <- c("input_pl.csv", "input_bs.csv", "input_summary.csv")

  for (f in files) {
    src <- system.file("examples", f, package = "bidash")
    if (src == "") {
      warning("サンプルファイルが見つかりません: ", f)
      next
    }
    dst <- file.path(dir, f)
    if (file.exists(dst) && !overwrite) {
      message("スキップ（既存）: ", dst)
    } else {
      file.copy(src, dst, overwrite = overwrite)
      message("コピー完了: ", dst)
    }
  }

  message("\n次のコマンドでダッシュボードを生成できます:")
  message('  create_dashboard(company_name = "株式会社サンプルテック (9999)")')

  invisible(normalizePath(dir))
}

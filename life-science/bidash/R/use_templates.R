#' テンプレートCSVをカレントディレクトリにコピーする
#'
#' input_pl.csv・input_bs.csv・input_summary.csv の3ファイルを
#' 指定ディレクトリにコピーします。既存ファイルは上書きしません。
#'
#' @param dir コピー先ディレクトリ（デフォルト: カレントディレクトリ）
#' @param overwrite 既存ファイルを上書きするか（デフォルト: FALSE）
#'
#' @return コピー先ディレクトリパス（不可視）
#' @export
#'
#' @examples
#' \dontrun{
#' use_templates()         # カレントディレクトリにコピー
#' use_templates("./data") # ./data にコピー
#' }
use_templates <- function(dir = ".", overwrite = FALSE) {
  files <- c("input_pl.csv", "input_bs.csv", "input_summary.csv")

  for (f in files) {
    src <- system.file("templates", f, package = "bidash")
    if (src == "") {
      warning("テンプレートが見つかりません: ", f)
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

  invisible(normalizePath(dir))
}

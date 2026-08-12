# ── 内部ヘルパー ────────────────────────────────────────────────────────────

.get_val <- function(df, item_col, item, val_col) {
  rows <- df[[item_col]] == item
  if (!any(rows, na.rm = TRUE)) return(NA_real_)
  as.numeric(df[rows, val_col][1])
}

.fmt <- function(x) {
  if (is.na(x)) return("N/A")
  format(round(x), big.mark = ",", scientific = FALSE)
}

.pct <- function(x, digits = 1) {
  if (is.na(x)) return("N/A")
  paste0(round(x, digits), "%")
}

# ── 業績サマリーコメント ──────────────────────────────────────────────────

#' 業績サマリーの AI コメントを生成する
#'
#' @param pl        損益計算書データフレーム
#' @param summary5  複数期サマリーデータフレーム
#' @param period_prev 前期カラム名
#' @param period_curr 当期カラム名
#' @param model_id  HF モデルID
#' @param token     HF API トークン
#' @return 生成されたコメント文字列（エラー時は NA）
#' @export
generate_summary_comment <- function(pl, summary5, period_prev, period_curr,
                                     model_id, token) {
  rev_curr <- .get_val(pl, "項目", "売上高",     period_curr)
  rev_prev <- .get_val(pl, "項目", "売上高",     period_prev)
  op_curr  <- .get_val(pl, "項目", "営業利益",   period_curr)
  ni_curr  <- .get_val(pl, "項目", "当期純利益", period_curr)
  roe      <- if ("ROE" %in% colnames(summary5)) tail(summary5$ROE, 1) else NA_real_

  rev_yoy <- if (!is.na(rev_prev) && rev_prev != 0)
    round((rev_curr - rev_prev) / abs(rev_prev) * 100, 1) else NA_real_
  op_mgn  <- if (!is.na(rev_curr) && rev_curr != 0)
    round(op_curr / rev_curr * 100, 1) else NA_real_

  prompt <- paste0(
    "あなたは証券アナリストです。以下の日本企業の業績データをもとに、",
    "投資家向けの総合コメントを日本語で5行以内で書いてください。\n\n",
    sprintf("【%s → %s 実績】\n", period_prev, period_curr),
    sprintf("・売上高: %s千円（前期比 %s）\n",    .fmt(rev_curr), .pct(rev_yoy)),
    sprintf("・営業利益: %s千円（営業利益率 %s）\n", .fmt(op_curr), .pct(op_mgn)),
    sprintf("・当期純利益: %s千円\n",              .fmt(ni_curr)),
    sprintf("・ROE: %s\n\n",                       .pct(roe)),
    "増収増益/増収減益/減収増益/減収減益の評価、",
    "収益性と成長性の強み・課題を中心に簡潔に述べてください。"
  )

  hf_inference(prompt, model_id = model_id, token = token)
}

# ── 損益計算書コメント ────────────────────────────────────────────────────

#' 損益計算書の AI コメントを生成する
#'
#' @param pl        損益計算書データフレーム
#' @param period_prev 前期カラム名
#' @param period_curr 当期カラム名
#' @param model_id  HF モデルID
#' @param token     HF API トークン
#' @return 生成されたコメント文字列（エラー時は NA）
#' @export
generate_pl_comment <- function(pl, period_prev, period_curr, model_id, token) {
  items <- c("売上高", "売上総利益", "販売費及び一般管理費",
             "営業利益", "経常利益", "当期純利益")

  rows <- vapply(items, function(i) {
    curr <- .get_val(pl, "項目", i, period_curr)
    prev <- .get_val(pl, "項目", i, period_prev)
    yoy  <- if (!is.na(prev) && prev != 0)
      round((curr - prev) / abs(prev) * 100, 1) else NA_real_
    sprintf("・%s: %s千円（前期比 %s）", i, .fmt(curr), .pct(yoy))
  }, character(1))

  prompt <- paste0(
    "以下は日本企業の損益計算書データです。",
    "損益構造の変化と収益性について、アナリスト視点で日本語5行以内のコメントを書いてください。\n\n",
    paste(rows, collapse = "\n"), "\n\n",
    "粗利率・営業利益率の変化、費用効率、改善点・懸念点を中心に述べてください。"
  )

  hf_inference(prompt, model_id = model_id, token = token)
}

# ── 貸借対照表コメント ────────────────────────────────────────────────────

#' 貸借対照表の AI コメントを生成する
#'
#' @param bs        貸借対照表データフレーム
#' @param period_prev 前期カラム名
#' @param period_curr 当期カラム名
#' @param model_id  HF モデルID
#' @param token     HF API トークン
#' @return 生成されたコメント文字列（エラー時は NA）
#' @export
generate_bs_comment <- function(bs, period_prev, period_curr, model_id, token) {
  items <- c("資産合計", "流動資産合計", "流動負債合計", "純資産合計", "負債合計")

  rows <- vapply(items, function(i) {
    curr <- .get_val(bs, "項目", i, period_curr)
    prev <- .get_val(bs, "項目", i, period_prev)
    yoy  <- if (!is.na(prev) && prev != 0)
      round((curr - prev) / abs(prev) * 100, 1) else NA_real_
    sprintf("・%s: %s千円（前期比 %s）", i, .fmt(curr), .pct(yoy))
  }, character(1))

  ca    <- .get_val(bs, "項目", "流動資産合計", period_curr)
  cl    <- .get_val(bs, "項目", "流動負債合計", period_curr)
  eq    <- .get_val(bs, "項目", "純資産合計",   period_curr)
  asset <- .get_val(bs, "項目", "資産合計",     period_curr)

  cur_r <- if (!is.na(cl) && cl != 0) round(ca / cl * 100, 1) else NA_real_
  eq_r  <- if (!is.na(asset) && asset != 0) round(eq / asset * 100, 1) else NA_real_

  prompt <- paste0(
    "以下は日本企業の貸借対照表データです。",
    "財務健全性・資本効率について、アナリスト視点で日本語5行以内のコメントを書いてください。\n\n",
    paste(rows, collapse = "\n"), "\n",
    sprintf("・流動比率: %s\n",   .pct(cur_r)),
    sprintf("・自己資本比率: %s\n\n", .pct(eq_r)),
    "財務安定性、資産効率、自己資本の変化について述べてください。"
  )

  hf_inference(prompt, model_id = model_id, token = token)
}

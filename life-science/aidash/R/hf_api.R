#' Hugging Face API トークンを環境変数に設定する
#'
#' @param token Hugging Face API トークン（hf_ から始まる文字列）
#' @export
#'
#' @examples
#' \dontrun{
#' set_hf_token("hf_xxxxxxxxxxxxxxxxxxxx")
#' }
set_hf_token <- function(token) {
  Sys.setenv(HF_API_TOKEN = token)
  message("HF_API_TOKEN を設定しました。")
  invisible(token)
}

#' Hugging Face Inference API でテキストを生成する
#'
#' @param prompt 入力プロンプト文字列
#' @param model_id 使用するモデルID（デフォルト: mistralai/Mistral-7B-Instruct-v0.2）
#' @param max_new_tokens 生成する最大トークン数（デフォルト: 512）
#' @param temperature 生成の多様性 0〜1（デフォルト: 0.7）
#' @param token API トークン。省略時は環境変数 HF_API_TOKEN を使用
#' @return 生成されたテキスト文字列。エラー時は NA_character_
#' @export
#'
#' @examples
#' \dontrun{
#' set_hf_token("hf_xxxxxxxxxxxxxxxxxxxx")
#' hf_inference("日本の経済について教えてください。")
#' }
hf_inference <- function(
    prompt,
    model_id       = "mistralai/Mistral-7B-Instruct-v0.2",
    max_new_tokens = 512,
    temperature    = 0.7,
    token          = Sys.getenv("HF_API_TOKEN")) {

  if (!nzchar(token)) {
    warning("HF_API_TOKEN が未設定です。set_hf_token() で設定してください。")
    return(NA_character_)
  }

  url <- paste0("https://api-inference.huggingface.co/models/", model_id)
  body <- jsonlite::toJSON(
    list(
      inputs     = prompt,
      parameters = list(
        max_new_tokens   = max_new_tokens,
        temperature      = temperature,
        return_full_text = FALSE
      )
    ),
    auto_unbox = TRUE
  )

  resp <- tryCatch(
    httr::POST(
      url    = url,
      httr::add_headers(
        Authorization  = paste("Bearer", token),
        `Content-Type` = "application/json"
      ),
      body   = body,
      encode = "raw",
      httr::timeout(60)
    ),
    error = function(e) {
      warning("HF API 接続エラー: ", conditionMessage(e))
      NULL
    }
  )

  if (is.null(resp)) return(NA_character_)

  status <- httr::status_code(resp)
  if (status != 200) {
    warning(sprintf(
      "HF API エラー (HTTP %d): %s",
      status,
      httr::content(resp, "text", encoding = "UTF-8")
    ))
    return(NA_character_)
  }

  result <- httr::content(resp, "parsed", encoding = "UTF-8")

  if (is.list(result) && length(result) > 0 &&
      !is.null(result[[1]]$generated_text)) {
    return(trimws(result[[1]]$generated_text))
  }

  NA_character_
}

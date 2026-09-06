"""
Streamlit Web UI for Stanford AI4PB Research Agent.
Google Cloud Agentic AI Hackathon MVP with Full-Text Paper Analysis & BigQuery Persistence.
"""

import streamlit as st
import json
import time
from agent import AI4PBResearchAgent
from config import PROJECT_ID, LOCATION, GEMINI_MODEL, LAB_NAME, LAB_URL, LAB_DIRECTOR

# Page Configuration
st.set_page_config(
    page_title="Stanford AI4PB Research Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #8C1515; /* Stanford Cardinal Red */
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .bq-card {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background-color: #8C1515; color: white; border-radius: 8px; padding: 6px 12px; font-weight: 700; font-size: 15px; display: inline-block; margin-bottom: 8px; letter-spacing: 0.5px;">
        🏛️ STANFORD AI4PB
    </div>
    """, unsafe_allow_html=True)
    st.title("AI4PB Agent")
    st.markdown(f"**対象研究機関**: [{LAB_NAME}]({LAB_URL})")
    st.markdown(f"**ディレクター**: {LAB_DIRECTOR}")
    
    st.divider()
    st.subheader("☁️ Google Cloud 連携情報")
    st.text_input("GCP Project ID", value=PROJECT_ID, disabled=True)
    st.text_input("Region", value=LOCATION, disabled=True)
    st.text_input("LLM Model", value=GEMINI_MODEL, disabled=True)
    st.text_input("BigQuery Dataset", value="ai4pb_research_logs", disabled=True)
    
    st.divider()
    st.subheader("⚡ 推論エンジン状態")
    user_api_key = st.text_input(
        "Google AI Studio API Key (任意)",
        type="password",
        help="個人の Google AI Studio API Key を指定できます。未入力の場合は Google Cloud Vertex AI (Gemini 2.5 Flash) が自動適用されます。"
    )
    if user_api_key:
        st.caption("🟢 API Key モード: Gemini 2.5 Flash 動的推論")
    else:
        st.caption("🟢 Google Cloud Vertex AI (Gemini 2.5 Flash) 連携稼働中")
    
    st.divider()
    st.markdown("### 🤖 Agentic 動作フロー")
    st.markdown("""
    1. **Plan**: 調査スコープを自律立案
    2. **Search**: ラボ情報・**arXiv API 動的検索**
    3. **Assess**: 情報の充足度を自己判定
    4. **Fetch Full-Text**: **論文本文を自動抽出・精読**
    5. **Protocol**: 再現性プロトコルの特定
    6. **Report**: 本文エビデンス付きレポート生成
    7. **Log**: **BigQuery に全履歴を保存**
    """)
    st.caption("Google Cloud Agentic AI Hackathon")

# Main Header
st.markdown('<div class="main-title">🎓 Stanford AI4PB Research Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Stanford大学 <b>AI for Public Benefit Lab (AI4PB)</b> の公開研究成果・論文・再現実験を自律調査する独立した学術 AI Agent です。</div>',
    unsafe_allow_html=True
)

# Session state initialization
DEFAULT_QUERY = "Synthetic Respondents について AI4PB ではどんな研究が行われている？"
if "query_text" not in st.session_state:
    st.session_state["query_text"] = DEFAULT_QUERY

run_triggered = False

# Example Queries
st.markdown("**💡 サンプル質問をクリックして即時実行:**")
col1, col2, col3 = st.columns(3)

if col1.button("🤖 1. Synthetic Respondents の研究", use_container_width=True):
    st.session_state["query_text"] = "Synthetic Respondents について AI4PB ではどんな研究が行われている？"
    run_triggered = True

if col2.button("📑 2. 最新研究テーマの整理", use_container_width=True):
    st.session_state["query_text"] = "AI4PB の最近の研究テーマと成果を整理して"
    run_triggered = True

if col3.button("🛠️ 3. 再現実験のしやすさ比較", use_container_width=True):
    st.session_state["query_text"] = "自分で再現実験するなら、どの研究が取り組みやすい？"
    run_triggered = True

# Input Area
user_input = st.text_area(
    "調査したい内容を入力してください（自由入力も可能）:",
    value=st.session_state["query_text"],
    height=80,
    placeholder="例: Silicon Sampling の最新論文と実験手法を教えて"
)

if st.button("🚀 自律リサーチを開始する", type="primary", use_container_width=True):
    st.session_state["query_text"] = user_input
    run_triggered = True

st.caption("🔒 ※ ご入力内容およびエージェントの自律実行ログは、デモ改善および分析のため Google Cloud BigQuery に記録されます。")

# Execution
if run_triggered:
    active_query = st.session_state["query_text"].strip()
    if not active_query:
        active_query = DEFAULT_QUERY

    st.markdown("---")
    st.subheader(f"🔍 調査テーマ: 『{active_query}』")
    
    agent = AI4PBResearchAgent(api_key=user_api_key if user_api_key else None)
    events_log = []
    final_report_text = ""
    bq_status_info = None

    # Real-time Agent Status Container
    with st.status("🤖 Agent が自律リサーチ（arXiv 動的検索 & 本文精読）を実行中...", expanded=True) as status:
        for event in agent.research(active_query):
            events_log.append(event)
            st.markdown(f"**[{event.step}]** {event.title}")
            
            if event.event_type == "plan":
                if isinstance(event.details, dict):
                    st.json(event.details)
                else:
                    st.info(event.details)
            elif event.event_type == "tool_call":
                st.code(f"Tool: {event.details.get('tool')}\nArgs: {json.dumps(event.details.get('arguments', {}), ensure_ascii=False)}", language="yaml")
            elif event.event_type == "observation":
                st.json(event.details)
            elif event.event_type == "gap":
                st.warning(event.details)
            elif event.event_type == "fulltext":
                st.success(f"📄 本文抽出完了: 『{event.details.get('paper_title')}』 (約 {event.details.get('extracted_length')} 文字)")
                with st.expander("🔍 取得した論文本文（抜粋）を見る"):
                    st.text(event.details.get("content_preview"))
            elif event.event_type == "report":
                final_report_text = event.details
            elif event.event_type == "bq":
                bq_status_info = event.details
                if bq_status_info.get("status") == "success":
                    st.info(f"📊 BigQuery に保存完了: `{bq_status_info.get('table_full_path')}`")
            
            time.sleep(0.15)
        
        status.update(label="✅ 自律調査 & BigQuery ログ保存が完了しました！", state="complete", expanded=False)

    # Render BigQuery Badge if successful
    if bq_status_info and bq_status_info.get("status") == "success":
        st.markdown(f"""
        <div class="bq-card">
            📊 <b>Google Cloud BigQuery に調査セッションを保存しました</b><br>
            <span style="font-size: 13px;">テーブル: <code>{bq_status_info.get('table_full_path')}</code> | セッションID: <code>{bq_status_info.get('session_id')}</code></span>
        </div>
        """, unsafe_allow_html=True)

    # Render Final Report
    st.markdown("---")
    st.header("📑 最終リサーチレポート (本文エビデンス統合版)")
    
    tab_report, tab_bq, tab_raw_log, tab_tools = st.tabs(["📄 統合レポート", "📊 BigQuery ログ連携", "📜 Agent 実行履歴 (JSON)", "🛠️ 使用ツール一覧"])
    
    with tab_report:
        st.markdown(final_report_text)
        st.download_button(
            label="💾 レポートをMarkdownとしてダウンロード",
            data=final_report_text,
            file_name="AI4PB_Research_Report.md",
            mime="text/markdown"
        )
    
    with tab_bq:
        st.markdown(f"""
        ### 📊 BigQuery 保存データについて
        本リサーチエージェントの会話履歴および自律調査ステップは、**Google Cloud BigQuery** に自動的にストリーミング保存されています。

        * **プロジェクト**: `{PROJECT_ID}`
        * **データセット**: `ai4pb_research_logs`
        * **テーブル**: `research_sessions`

        #### 保存された主なカラム:
        - `session_id`: セッション固有 ID
        - `timestamp`: 実行タイムスタンプ (UTC)
        - `user_query`: ユーザーの質問
        - `full_text_used`: 論文本文（Full-Text）を読み込んだかのフラグ
        - `agent_events_log`: Agent が実行した全 Action / Tool の中間 JSON ログ
        - `final_report`: 生成された Markdown レポート

        #### ログ確認用 SQL クエリ（BigQuery コンソールで実行可能）:
        ```sql
        SELECT
            timestamp,
            user_query,
            full_text_used,
            events_count,
            SUBSTR(final_report, 1, 200) AS report_preview
        FROM
            `{PROJECT_ID}.ai4pb_research_logs.research_sessions`
        ORDER BY
            timestamp DESC
        LIMIT 10;
        ```
        """)

    with tab_raw_log:
        st.write("Agentic 実行ログ (Hackathon 審査・デバッグ用):")
        st.json([e.to_dict() for e in events_log])
        
    with tab_tools:
        st.markdown("""
        ### 今回の調査で使用された Tools
        1. **`search_ai4pb_topics(query)`**: AI4PB Lab の研究ビジョン、ディレクター情報、コアテーマを抽出
        2. **`search_academic_papers(keywords)`**: **arXiv API とリアルタイム通信**し、最新の関連プレプリント・論文を動的検索
        3. **`fetch_paper_fulltext(paper_id)`**: **ar5iv / arXiv HTML から論文本文（数千〜数万文字）を抽出・精読**
        4. **`fetch_paper_details(paper_id)`**: 実験プロトコル、再現難易度、プロンプト設計ガイドを取得
        5. **`BigQueryLogger.log_session(...)`**: 調査セッションを Google Cloud BigQuery に自動保存
        """)

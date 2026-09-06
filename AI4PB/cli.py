"""
Command Line Interface (CLI) for Stanford AI4PB Research Agent.
Lightweight test runner without external UI dependencies.
"""

import sys
from agent import AI4PBResearchAgent

SAMPLE_QUERIES = [
    "Synthetic Respondents について AI4PB ではどんな研究が行われている？",
    "AI4PB の最近の研究テーマと成果を整理して",
    "自分で再現実験するなら、どの研究が取り組みやすい？"
]


def run_cli():
    print("=" * 70)
    print("🎓 Stanford AI4PB Research Agent (CLI Mode)")
    print("=" * 70)
    print("以下のサンプル質問番号を選択するか、質問を自由入力してください:")
    print(" [1] Synthetic Respondents について AI4PB ではどんな研究が行われている？")
    print(" [2] AI4PB の最近の研究テーマと成果を整理して")
    print(" [3] 自分で再現実験するなら、どの研究が取り組みやすい？")
    print(" [Enter] 1番をデフォルト実行")
    print("-" * 70)

    try:
        user_choice = input("選択 (1/2/3 または自由入力) > ").strip()
    except (EOFError, KeyboardInterrupt):
        user_choice = "1"

    if user_choice == "1" or not user_choice:
        query = SAMPLE_QUERIES[0]
    elif user_choice == "2":
        query = SAMPLE_QUERIES[1]
    elif user_choice == "3":
        query = SAMPLE_QUERIES[2]
    else:
        query = user_choice

    print(f"\n🚀 調査開始: '{query}'\n")

    agent = AI4PBResearchAgent()
    final_report = ""

    for event in agent.research(query):
        print(f"\n>>> [{event.step}] {event.title}")
        if event.event_type == "plan":
            if isinstance(event.details, dict):
                for k, v in event.details.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"{event.details}")
        elif event.event_type == "tool_call":
            print(f"    🛠️ Tool: {event.details.get('tool')}")
            print(f"    Arguments: {event.details.get('arguments')}")
        elif event.event_type == "observation":
            print(f"    📥 結果: {event.details}")
        elif event.event_type == "gap":
            print(f"    🔍 ギャップ評価:\n{event.details}")
        elif event.event_type == "report":
            final_report = event.details

    print("\n" + "=" * 70)
    print("📑 最終リサーチレポート")
    print("=" * 70)
    print(final_report)


if __name__ == "__main__":
    run_cli()

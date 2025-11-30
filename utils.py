from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import random
import os
from openai import OpenAI
import constants as ct
import streamlit as st

# OpenAI APIキーの取得（Streamlit Secrets優先、なければ環境変数）
def get_openai_api_key():
    # Streamlit Secretsから取得を試みる
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except:
        pass
    
    # 環境変数から取得
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        return api_key
    
    # どちらも取得できない場合はNone
    return None

api_key = get_openai_api_key()
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None  # ヒント機能使用時にエラーメッセージを表示


############################################################
# CSV読込
############################################################

def load_questions_csv():
    """
    問題データのCSVファイルを読み込む
    
    Returns:
        pd.DataFrame: 問題データ
        
    Raises:
        FileNotFoundError: CSVファイルが存在しない場合
    """
    if not os.path.exists(ct.QUESTIONS_CSV):
        st.error(f"エラー: {ct.QUESTIONS_CSV} が見つかりません", icon=":material/error:")
        st.info("data/questions.csv ファイルを配置してください", icon=":material/info:")
        st.stop()
    
    try:
        df = pd.read_csv(ct.QUESTIONS_CSV, encoding="utf-8-sig")
        
        # 必須列の存在チェック
        required_columns = ["question", "option1", "option2", "option3", "option4", 
                        "correct_option", "genre", "difficulty", "option_explanations"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"エラー: CSVファイルに必要な列が不足しています: {', '.join(missing_columns)}", 
                    icon=":material/error:")
            st.stop()
        
        # データが空でないかチェック
        if len(df) == 0:
            st.error("エラー: CSVファイルに問題データが存在しません", icon=":material/error:")
            st.stop()
        
        return df
        
    except pd.errors.EmptyDataError:
        st.error(f"エラー: {ct.QUESTIONS_CSV} が空のファイルです", icon=":material/error:")
        st.stop()
    except Exception as e:
        st.error(f"エラー: CSVファイルの読み込みに失敗しました - {str(e)}", icon=":material/error:")
        st.stop()

############################################################
# 次の問題を選択
############################################################

def load_next_question(df, genre, difficulty):
    st = __import__("streamlit").session_state

    # フィルター条件のキーを作成
    filter_key = f"{genre}_{difficulty}"
    
    # このフィルター条件の出題履歴を初期化（存在しない場合）
    if filter_key not in st.asked_questions:
        st.asked_questions[filter_key] = []

    filtered = df.copy()
    if genre != "ランダム":
        filtered = filtered[filtered["genre"] == genre]
    if difficulty != "ランダム":
        filtered = filtered[filtered["difficulty"] == difficulty]

    # フィルター結果が0件の場合（問題が存在しない組み合わせ）
    if len(filtered) == 0:
        st.no_questions_available = True
        st.all_questions_done = False
        return
    
    # 問題が存在するのでフラグをリセット
    st.no_questions_available = False

    # 元のインデックスを保持したまま、出題済み問題を除外
    asked_indices = st.asked_questions[filter_key]
    available_questions = filtered[~filtered.index.isin(asked_indices)]
    
    # 全問題出題済みの場合
    if len(available_questions) == 0:
        st.all_questions_done = True
        return
    
    # 全問出題完了フラグをリセット
    st.all_questions_done = False
    
    # ランダムに1問選択（1回のsampleで問題とインデックスの両方を取得）
    sampled = available_questions.sample(1)
    q = sampled.iloc[0]
    question_index = sampled.index[0]
    
    # 出題済みリストに追加（元のインデックスを記録）
    st.asked_questions[filter_key].append(question_index)

    # 選択肢シャッフル（元のインデックスも保持）
    options_with_indices = [
        (q["option1"], 0),
        (q["option2"], 1),
        (q["option3"], 2),
        (q["option4"], 3)
    ]
    random.shuffle(options_with_indices)
    
    # シャッフル後の選択肢と元のインデックスを分離
    options = [opt for opt, _ in options_with_indices]
    shuffled_indices = [idx for _, idx in options_with_indices]

    # 正解インデックス
    correct_index = options.index(q[f"option{int(q['correct_option'])}"])

    st.current_question = q
    st.shuffled_options = options
    st.shuffled_indices = shuffled_indices  # 元のインデックスを保存
    st.correct_index = correct_index

    # ▼ 正誤データを必ずリセット
    st.user_answer = None
    st.show_result = False
    st.hint_step = 1

############################################################
# AIヒント生成
############################################################

def generate_hint(explanation, difficulty, step):
    # OpenAI APIキーが設定されていない場合のエラー処理
    if client is None:
        raise ValueError("OpenAI APIキーが設定されていません。Streamlit Secretsまたは.envファイルにOPENAI_API_KEYを設定してください。")
    
    prompt = f"""
あなたはクイズのヒントだけを短く生成するAIです。
以下の制約でヒントを生成してください。

【解説】
{explanation}

【難易度】
{difficulty}

【ヒント段階】
STEP {step}

【条件】
- 答えを直接示さない
- 1〜2文で短く
- 難易度に応じてヒントの強弱を調整
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7,
        )
        return res.choices[0].message.content
    except Exception as e:
        raise Exception(f"ヒント生成中にエラーが発生しました: {str(e)}")


############################################################
# ヒント管理（段階制）
############################################################

def get_hint(explanation, difficulty):
    st = __import__("streamlit").session_state

    if "hint_step" not in st:
        st.hint_step = 1

    hint = generate_hint(explanation, difficulty, st.hint_step)

    if st.hint_step < 2:
        st.hint_step += 1

    return hint


############################################################
# スコア計算（マルチプレイヤー用）
############################################################

def calculate_points(is_correct, hint_used):
    """
    正解時の得点を計算
    
    Args:
        is_correct (bool): 正解かどうか
        hint_used (bool): ヒントを使用したかどうか
        
    Returns:
        float: 獲得点数（正解かつヒント使用: 0.5点、正解かつヒント未使用: 1点、不正解: 0点）
    """
    if not is_correct:
        return 0.0
    return 0.5 if hint_used else 1.0


def update_player_score(player_index, is_correct, hint_used):
    """
    プレイヤーのスコアを更新
    
    Args:
        player_index (int): プレイヤーのインデックス（0=A, 1=B, 2=C, 3=D）
        is_correct (bool): 正解かどうか
        hint_used (bool): ヒントを使用したかどうか
    """
    st = __import__("streamlit").session_state
    
    if player_index not in st.player_scores:
        st.player_scores[player_index] = {"correct": 0, "total": 0, "points": 0.0}
    
    points = calculate_points(is_correct, hint_used)
    st.player_scores[player_index]["total"] += 1
    st.player_scores[player_index]["points"] += points
    
    if is_correct:
        st.player_scores[player_index]["correct"] += 1


def get_next_player(current_player, player_count):
    """
    次のプレイヤーのインデックスを取得
    
    Args:
        current_player (int): 現在のプレイヤーインデックス
        player_count (int): プレイヤー総数
        
    Returns:
        int: 次のプレイヤーのインデックス
    """
    return (current_player + 1) % player_count
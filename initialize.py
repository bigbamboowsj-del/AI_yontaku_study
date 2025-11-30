"""
アプリ起動時に一度だけ実行する初期化処理
"""

import streamlit as st
from dotenv import load_dotenv
import constants as ct
from utils import load_questions_csv


############################################################
# .env 読み込み（OpenAI APIキーのため必須）
############################################################

load_dotenv()


############################################################
# 初期化関数
############################################################

def init_app():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

        st.session_state.full_df = load_questions_csv()

        # 初期化データ
        st.session_state.current_question = None
        st.session_state.shuffled_options = []
        st.session_state.shuffled_indices = []  # シャッフル後の元インデックス
        st.session_state.correct_index = None
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.question_number = 1
        st.session_state.hint_step = 1
        st.session_state.asked_questions = {}  # フィルター条件ごとに出題済み問題を記録
        st.session_state.all_questions_done = False  # 全問出題完了フラグ
        st.session_state.no_questions_available = False  # 問題が存在しないフラグ
        st.session_state.game_started = False  # ゲーム開始フラグ

        # 追加推奨の初期化
        st.session_state.genre = "ランダム"
        st.session_state.difficulty = "ランダム"

        # マルチプレイヤー設定
        st.session_state.player_count = 1  # デフォルトは1人
        st.session_state.current_player = 0  # 現在の解答者インデックス（0=A, 1=B, 2=C, 3=D）
        st.session_state.player_scores = {}  # {player_index: {"correct": 0, "total": 0, "points": 0.0}}
        st.session_state.hint_used = False  # 現在の問題でヒントを使用したかどうか
        st.session_state.question_limit = None  # 問題数制限（Noneは無制限）
        st.session_state.time_limit = None  # 時間制限（秒、Noneは無制限）
        st.session_state.question_start_time = None  # 問題開始時刻
        st.session_state.game_finished = False  # ゲーム終了フラグ
        st.session_state.player_answers = {}  # {player_index: answer_index} 各プレイヤーの解答記録
        st.session_state.all_players_answered = False  # 全員解答完了フラグ
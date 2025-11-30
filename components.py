import streamlit as st
import constants as ct
from utils import get_hint, load_next_question, update_player_score, get_next_player
import time


############################################################
# タイトル
############################################################

def show_title():
    st.markdown(
        f"<h1 style='color:{ct.THEME_COLOR}; text-align:center; margin-bottom:0.5rem;'>{ct.APP_TITLE}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h4 style='text-align:center; color: gray; margin-top:0; font-weight:normal;'>{ct.SUBTITLE}</h4>",
        unsafe_allow_html=True,
    )
    st.write("")

def show_start_guide():
    """ゲーム開始前の案内を表示"""
    # constants.pyのアイコンを使用
    guide_icon = ct.ICON_GUIDE.replace(':material/', '').replace(':', '')
    
    st.markdown(f"""
    <div style='text-align:center; padding:2.5rem 1.5rem; background-color:#f8f9fa; border-radius:10px; margin:2rem 0;'>
        <p style='font-size:1.4rem; color:#666; margin-bottom:1rem;'><strong>使い方</strong></p>
        <p style='font-size:1.2rem; color:#666; line-height:1.8;'>
            ① サイドバーから<strong>ジャンル</strong>と<strong>難易度</strong>を選択<br>
            ② <strong style='color:{ct.THEME_COLOR};'>New Game</strong>ボタンを押してスタート！
        </p>
    </div>
    """, unsafe_allow_html=True)


############################################################
# フィルター
############################################################

def show_sidebar_filters(df):
    # サイドバー全体の翻訳を防止とフォントサイズ調整
    st.sidebar.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebar"] * {
            translate: no !important;
        }
        .stSelectbox, .stButton {
            translate: no !important;
        }
        /* サイドバーのフォントサイズを小さく調整 */
        [data-testid="stSidebar"] h3 {
            font-size: 1.1rem !important;
        }
        [data-testid="stSidebar"] h4 {
            font-size: 0.95rem !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.3rem !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            font-size: 0.9rem !important;
        }
        [data-testid="stSidebar"] button {
            font-size: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"### {ct.TITLE_CUSTOMIZE}")

    genres = ["ランダム"] + sorted(df["genre"].unique())
    diffs = ["ランダム", "easy", "normal", "hard"]

    genre = st.sidebar.selectbox("ジャンル", genres)
    difficulty = st.sidebar.selectbox("難易度", diffs)
    
    # プレイヤー数選択
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"#### {ct.ICON_PLAYER} プレイヤー数")
    player_count = st.sidebar.selectbox(
        "人数を選択",
        ct.PLAYER_COUNT_OPTIONS,
        key="player_count_select",
        label_visibility="collapsed"
    )
    
    # 問題数制限
    st.sidebar.markdown(f"#### {ct.ICON_SCOREBOARD} 問題数")
    question_limit_label = st.sidebar.selectbox(
        "問題数を選択",
        list(ct.QUESTION_LIMIT_OPTIONS.keys()),
        key="question_limit_select",
        label_visibility="collapsed"
    )
    question_limit = ct.QUESTION_LIMIT_OPTIONS[question_limit_label]
    
    # 時間制限
    st.sidebar.markdown(f"#### {ct.ICON_TIMER} 制限時間")
    time_limit_label = st.sidebar.selectbox(
        "制限時間を選択",
        list(ct.TIME_LIMIT_OPTIONS.keys()),
        key="time_limit_select",
        label_visibility="collapsed"
    )
    time_limit = ct.TIME_LIMIT_OPTIONS[time_limit_label]
    
    # NEW GAME ボタン（制限時間の下に配置）
    st.sidebar.markdown("---")
    if st.sidebar.button(ct.BTN_NEW_GAME, use_container_width=True):
        reset_game()

    # セッションに保存
    st.session_state.genre = genre
    st.session_state.difficulty = difficulty
    st.session_state.player_count = player_count
    st.session_state.question_limit = question_limit
    st.session_state.time_limit = time_limit

    return genre, difficulty


############################################################
# ゲームリセット
############################################################
def reset_game():
    st.session_state.current_question = None
    st.session_state.user_answer = None
    st.session_state.show_result = False
    st.session_state.question_number = 1
    st.session_state.asked_questions = {}  # 出題履歴もリセット
    st.session_state.all_questions_done = False  # 全問完了フラグもリセット
    st.session_state.no_questions_available = False  # 問題なしフラグもリセット
    st.session_state.game_started = True  # ゲーム開始
    
    # マルチプレイヤー関連のリセット
    st.session_state.current_player = 0
    st.session_state.player_scores = {}
    st.session_state.hint_used = False
    st.session_state.question_start_time = None
    st.session_state.game_finished = False
    st.session_state.player_answers = {}
    st.session_state.all_players_answered = False
    st.session_state.result_processed = False  # スコア更新フラグもリセット


############################################################
# スコアボード表示（問題上部に横並び）
############################################################
def show_scoreboard():
    """全プレイヤーのスコアを横並びで表示"""
    player_count = st.session_state.player_count
    
    if player_count == 1:
        return  # 1人プレイ時は表示しない
    
    st.markdown(f"### {ct.ICON_SCOREBOARD} スコアボード")
    
    # プレイヤー数に応じてカラムを作成
    cols = st.columns(player_count)
    
    for i in range(player_count):
        player_name = ct.PLAYER_NAMES[i]
        score_data = st.session_state.player_scores.get(i, {"correct": 0, "total": 0, "points": 0.0})
        
        # 正解率計算
        if score_data["total"] > 0:
            percentage = (score_data["correct"] / score_data["total"]) * 100
            score_text = f"{score_data['correct']}/{score_data['total']} ({percentage:.0f}%)"
        else:
            score_text = "0/0 (0%)"
        
        # ポイント表示
        points = score_data['points']
        
        # 現在の解答者かどうかで表示を変更
        is_current = (i == st.session_state.current_player)
        
        with cols[i]:
            if is_current:
                st.markdown(f"""
                <div style='padding: 1.2rem; background-color: {ct.THEME_SUB_COLOR}; border: 3px solid {ct.THEME_COLOR}; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {ct.THEME_COLOR};'>{player_name}</div>
                    <div style='font-size: 1.1rem; color: #666; margin: 0.5rem 0;'>{score_text}</div>
                    <div style='font-size: 1.5rem; font-weight: bold; color: {ct.THEME_COLOR};'>{points:.1f}点</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='padding: 1.2rem; background-color: white; border: 1px solid #ddd; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 1.6rem; font-weight: bold; color: {ct.THEME_COLOR};'>{player_name}</div>
                    <div style='font-size: 1.1rem; color: #666; margin: 0.5rem 0;'>{score_text}</div>
                    <div style='font-size: 1.3rem; font-weight: bold; color: {ct.THEME_COLOR};'>{points:.1f}点</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.write("")


############################################################
# 現在の解答者表示
############################################################
def show_current_player():
    """現在の解答者を大きく表示"""
    player_count = st.session_state.player_count
    
    if player_count == 1:
        return  # 1人プレイ時は表示しない
    
    current_player_name = ct.PLAYER_NAMES[st.session_state.current_player]
    
    # HTML背景 + Streamlitアイコンを分離
    st.markdown(f"""
    <div style='text-align: center; margin: 1rem 0; padding: 1rem; background: linear-gradient(135deg, {ct.THEME_COLOR} 0%, #1a5fbf 100%); border-radius: 10px;'>
    </div>
    """, unsafe_allow_html=True)
    
    # アイコン付きテキストを上に重ねる
    st.markdown(f"<div style='text-align: center; margin-top: -3.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
    st.markdown(f"## {ct.ICON_TARGET} 現在の解答者: **{current_player_name}**")
    st.markdown("</div>", unsafe_allow_html=True)


############################################################
# 問題文
############################################################

def show_question():
    q = st.session_state.current_question
    num = st.session_state.question_number

    html = (
        f"<h3 style='line-height:1.6; word-wrap:break-word;'>"
        f"<span style='color:{ct.THEME_COLOR}; font-size:inherit; font-weight:bold;'>Q{num}</span>　{q['question']}"
        f"</h3>"
    )
    st.markdown(html, unsafe_allow_html=True)
    st.write("")


############################################################
# 選択肢 ＆ Tips
############################################################

def show_answer_area():
    q = st.session_state.current_question
    options = st.session_state.shuffled_options
    correct_index = st.session_state.correct_index
    player_count = st.session_state.player_count
    current_player = st.session_state.current_player

    # 全員解答済みの場合は結果表示
    if st.session_state.all_players_answered:
        show_all_players_result(q, correct_index)
        return

    st.markdown(f"### {ct.TITLE_SELECT_OPTIONS}")

    # 現在のプレイヤーの選択状態を表示
    if current_player in st.session_state.player_answers:
        selected_index = st.session_state.player_answers[current_player]
        selected_label = ct.CHOICE_LABELS[selected_index]
        st.info(f"現在の選択: {selected_label} - {options[selected_index]}")

    # 選択肢（レスポンシブ対応）
    for i, opt in enumerate(options):
        label = ct.CHOICE_LABELS[i]
        # 現在の選択をハイライト
        button_type = "primary" if current_player in st.session_state.player_answers and st.session_state.player_answers[current_player] == i else "secondary"
        if st.button(f"{label}: {opt}", key=f"opt_{i}", use_container_width=True, type=button_type):
            st.session_state.player_answers[current_player] = i
            st.rerun()

    st.write("---")

    # ヒント機能（解答前に表示）
    st.markdown(f"#### {ct.ICON_HINT_TITLE} ヒント")
    if st.button(ct.BTN_HINT, key="hint_before_answer", use_container_width=True):
        try:
            # 正解の解説を取得してヒント生成
            explanations = str(q.get("option_explanations", "")).split("|")
            correct_explanation = explanations[int(q["correct_option"]) - 1] if len(explanations) >= int(q["correct_option"]) else "解説がありません"
            hint = get_hint(correct_explanation, q["difficulty"])
            st.info(hint, icon=ct.ICON_HINT)
            st.warning("ヒントを見ても得点は変わりません", icon=ct.ICON_INFO)
        except ValueError as e:
            st.error(str(e), icon=":material/error:")
        except Exception as e:
            st.error(f"ヒント生成に失敗しました: {str(e)}", icon=":material/error:")
    
    st.write("---")
    
    # プレイヤー交代ボタン（選択済みの場合のみ表示）
    if current_player in st.session_state.player_answers:
        # 最後のプレイヤーかどうか
        is_last_player = (current_player == player_count - 1)
        
        if is_last_player:
            # 最後のプレイヤーは「解答を表示」ボタン
            if st.button(f"{ct.ICON_CHART} 解答を表示", use_container_width=True, type="primary"):
                st.session_state.all_players_answered = True
                st.session_state.show_result = True
                st.rerun()
        else:
            # 次のプレイヤー名を取得
            next_player_idx = current_player + 1
            next_player_name = ct.PLAYER_NAMES[next_player_idx]
            
            if st.button(f"{ct.ICON_ARROW_NEXT} 次のプレイヤーへ（{next_player_name}）", use_container_width=True, type="primary"):
                st.session_state.current_player = next_player_idx
                # タイマーリセット
                st.session_state.question_start_time = time.time()
                st.rerun()
    else:
        st.warning(f"{ct.ICON_WARNING} {ct.PLAYER_NAMES[current_player]}さん、選択肢を選んでください")


############################################################
# 全選択肢の解説表示
############################################################

def show_all_options_explanation(q, options, correct_index):
    """全選択肢の解説をカード形式で表示"""
    st.markdown(f"### {ct.ICON_BOOK} 全選択肢の解説")
    
    # option_explanationsを|で分割
    if "option_explanations" in q and q["option_explanations"]:
        explanations = str(q["option_explanations"]).split("|")
        
        # 解説が4つない場合のエラー処理
        if len(explanations) < 4:
            st.warning("解説データが不完全です", icon=":material/warning:")
            return
        
        # シャッフルされた選択肢の元のインデックスを取得（存在しない場合はデフォルト値）
        shuffled_indices = st.session_state.get('shuffled_indices', [0, 1, 2, 3])
        
        for i in range(4):
            label = ct.CHOICE_LABELS[i]
            option_text = options[i]
            is_correct = (i == correct_index)
            
            # シャッフル前の元のインデックスを使って正しい解説を取得
            original_index = shuffled_indices[i]
            explanation_text = explanations[original_index]
            
            # 正解/不正解マークと色
            if is_correct:
                mark_icon = ct.ICON_CORRECT
                border_color = ct.THEME_COLOR
                bg_color = ct.THEME_SUB_COLOR
                status_text = "正解"
            else:
                mark_icon = ct.ICON_WRONG
                border_color = "#999"
                bg_color = "#f8f9fa"
                status_text = "不正解"
            
            # カード表示
            st.markdown(f"""
            <div style='margin: 1rem 0; padding: 1.2rem; border-left: 5px solid {border_color}; background-color: {bg_color}; border-radius: 8px;'>
                <div style='font-size: 1.3rem; font-weight: bold; color: {border_color}; margin-bottom: 0.5rem;'>
                    {label}: {option_text} {status_text}
                </div>
                <div style='color: #333; line-height: 1.8; font-size: 1.1rem;'>
                    {explanation_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # 解説データがない場合は表示しない
        pass


############################################################
# 全員の解答結果表示
############################################################

def show_all_players_result(q, correct_index):
    """全プレイヤーの解答と結果を一覧表示"""
    player_count = st.session_state.player_count
    options = st.session_state.shuffled_options
    correct_option = options[correct_index]
    
    st.markdown(f"### {ct.ICON_CHART} 解答結果")
    st.write("")
    
    # スコア更新を先に一括処理（初回のみ）
    if "result_processed" not in st.session_state or not st.session_state.result_processed:
        # 実際に解答したプレイヤーのみスコア更新
        for player_idx in st.session_state.player_answers.keys():
            answer_idx = st.session_state.player_answers[player_idx]
            is_correct = (answer_idx == correct_index) if answer_idx != -1 else False
            update_player_score(player_idx, is_correct, False)  # ヒント使用なし
        st.session_state.result_processed = True
    
    # 各プレイヤーの結果を表示
    for i in range(player_count):
        player_name = ct.PLAYER_NAMES[i]
        answer_index = st.session_state.player_answers.get(i, -1)
        
        # 時間切れまたは未解答
        if answer_index == -1:
            is_correct = False
            answer_text = "時間切れ / 未解答"
        else:
            is_correct = (answer_index == correct_index)
            answer_label = ct.CHOICE_LABELS[answer_index]
            answer_text = f"{answer_label}: {options[answer_index]}"
        
        # 結果表示
        if is_correct:
            st.success(f"**{player_name}**: {answer_text} → **正解！ (+1点)**", icon=ct.ICON_CORRECT)
        else:
            st.error(f"**{player_name}**: {answer_text} → **不正解**", icon=ct.ICON_WRONG)
    
    st.write("---")
    
    # 正解表示
    st.markdown(f"### {ct.ICON_BULLSEYE} 正解")
    correct_label = ct.CHOICE_LABELS[correct_index]
    st.info(f"**{correct_label}: {correct_option}**", icon=ct.ICON_CORRECT)
    
    # 全選択肢の解説
    show_all_options_explanation(q, options, correct_index)
    
    st.write("---")
    
    # ボタン
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("ゲーム終了", use_container_width=True, type="secondary"):
            st.session_state.game_finished = True
            st.rerun()
    
    with col2:
        if st.button(ct.BTN_NEXT, use_container_width=True, type="primary"):
            st.session_state.question_number += 1
            load_next_question(
                st.session_state.full_df,
                st.session_state.genre,
                st.session_state.difficulty,
            )
            
            # 全問出題完了時
            if st.session_state.all_questions_done:
                st.session_state.game_finished = True
                st.rerun()
            
            # 問題数制限チェック
            if st.session_state.question_limit is not None:
                total_questions = sum(st.session_state.player_scores.get(i, {}).get("total", 0) 
                                    for i in range(st.session_state.player_count))
                if total_questions >= st.session_state.question_limit:
                    st.session_state.game_finished = True
                    st.rerun()
            
            # 次の問題の準備
            st.session_state.current_player = 0  # 最初のプレイヤーに戻す
            st.session_state.player_answers = {}  # 解答記録をクリア
            st.session_state.all_players_answered = False
            st.session_state.show_result = False
            st.session_state.question_start_time = time.time()
            st.session_state.result_processed = False
            
            st.rerun()


############################################################
# 最終結果画面
############################################################

def show_final_results():
    """ゲーム終了時の最終結果を表示"""
    st.markdown(f"## {ct.ICON_TROPHY} ゲーム終了！")
    
    # ランキング生成
    rankings = []
    for i in range(st.session_state.player_count):
        score_data = st.session_state.player_scores.get(i, {"correct": 0, "total": 0, "points": 0.0})
        rankings.append({
            "player": ct.PLAYER_NAMES[i],
            "points": score_data["points"],
            "correct": score_data["correct"],
            "total": score_data["total"],
            "percentage": (score_data["correct"] / score_data["total"] * 100) if score_data["total"] > 0 else 0
        })
    
    # ポイント順にソート
    rankings.sort(key=lambda x: x["points"], reverse=True)
    
    # ランキング表示
    st.markdown(f"### {ct.ICON_TROPHY} ランキング")
    
    for rank, data in enumerate(rankings, 1):
        # メダル表示
        if rank == 1:
            medal = "1位"
            color = "#FFD700"
        elif rank == 2:
            medal = "2位"
            color = "#C0C0C0"
        elif rank == 3:
            medal = "3位"
            color = "#CD7F32"
        else:
            medal = f"{rank}位"
            color = "#666"
        
        # ランキングカード
        st.markdown(f"""
        <div style='margin: 1rem 0; padding: 2rem; border-radius: 10px; background-color: #f8f9fa; border-left: 5px solid {color};'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div style='font-size: 1.8rem; font-weight: bold; color: {color};'>{medal} {data['player']}</div>
                <div style='text-align: right;'>
                    <div style='font-size: 2.2rem; font-weight: bold; color: {ct.THEME_COLOR};'>{data['points']:.1f}点</div>
                    <div style='font-size: 1.2rem; color: #666;'>{data['correct']}/{data['total']} ({data['percentage']:.0f}%)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.write("---")
    
    # 操作ボタン
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(ct.BTN_NEW_GAME, use_container_width=True, type="primary"):
            reset_game()
            st.rerun()
    
    with col2:
        if st.button("カスタマイズに戻る", use_container_width=True):
            st.session_state.game_started = False
            st.session_state.game_finished = False
            st.rerun()
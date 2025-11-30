import streamlit as st
from initialize import init_app
import components as cp
import utils as ut
import constants as ct


############################################################
# ページ設定
############################################################

st.set_page_config(
    page_title=ct.APP_TITLE,
    page_icon=ct.PAGE_ICON,
    layout="centered",
)

# ページ全体の翻訳を防止（JavaScriptによる強制）
st.markdown("""
<script>
    // 言語属性を日本語に設定（ブラウザに「既に日本語」と認識させる）
    document.documentElement.setAttribute('lang', 'ja');
    document.documentElement.setAttribute('translate', 'no');
    document.documentElement.setAttribute('class', 'notranslate');
    document.body.setAttribute('translate', 'no');
    document.body.setAttribute('class', 'notranslate');
    
    // すべての要素に翻訳防止属性を追加
    function disableTranslation() {
        // HTML要素のlang属性を確実に設定
        document.documentElement.lang = 'ja';
        
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            el.setAttribute('translate', 'no');
            el.classList.add('notranslate');
        });
        
        // サイドバー、ボタン、セレクトボックスを特に強制
        const criticalElements = document.querySelectorAll(
            '[data-testid="stSidebar"], [data-testid="stSidebar"] *, button, select, option, .stButton, .stSelectbox'
        );
        criticalElements.forEach(el => {
            el.setAttribute('translate', 'no');
            el.classList.add('notranslate');
            el.setAttribute('lang', 'ja');
        });
    }
    
    // 即座に実行
    document.documentElement.lang = 'ja';
    disableTranslation();
    
    // ページ読み込み完了後も実行
    window.addEventListener('load', disableTranslation);
    
    // 定期的に実行
    setInterval(disableTranslation, 100);
    
    // MutationObserverで動的に追加される要素も監視
    const observer = new MutationObserver(disableTranslation);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# 自動翻訳防止 & レスポンシブ対応
st.markdown("""
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    /* 自動翻訳を完全に防止 */
    html {
        translate: no !important;
    }
    
    body {
        translate: no !important;
    }
    
    * {
        translate: no !important;
    }
    
    .main, .stApp, [data-testid="stAppViewContainer"] {
        translate: no !important;
    }
    
    /* サイドバー、ボタン、セレクトボックスの翻訳を防止 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    .stButton,
    .stButton button,
    .stSelectbox,
    .stSelectbox *,
    button,
    select,
    option {
        translate: no !important;
    }
    
    /* コンテナの最大幅設定 */
    .main .block-container {
        max-width: 900px;
        padding: 2rem 1rem;
    }
    
    /* PC用（768px以上） */
    @media (min-width: 768px) {
        .main .block-container {
            padding: 3rem 2rem;
        }
        
        /* PCのフォントサイズを大きく */
        h1 {
            font-size: 2.8rem !important;
        }
        
        h2 {
            font-size: 2.2rem !important;
        }
        
        h3 {
            font-size: 1.8rem !important;
        }
        
        h4 {
            font-size: 1.4rem !important;
        }
        
        p, div, span {
            font-size: 1.1rem !important;
        }
        
        /* ボタンのフォントサイズ */
        .stButton button {
            font-size: 1.2rem !important;
            padding: 0.8rem 1.5rem !important;
        }
    }
    
    /* スマホ用（767px以下） */
    @media (max-width: 767px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        /* タイトルのフォントサイズ調整 */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h3 {
            font-size: 1.3rem !important;
        }
        
        h4 {
            font-size: 1rem !important;
        }
        
        /* ボタンのタッチ領域を大きく */
        .stButton button {
            min-height: 3rem !important;
            font-size: 1rem !important;
            padding: 0.75rem 1rem !important;
        }
    }
    
    /* タブレット用（768px～1024px） */
    @media (min-width: 768px) and (max-width: 1024px) {
        .main .block-container {
            max-width: 750px;
        }
    }
    
    /* ボタンのスタイル調整 */
    .stButton button {
        width: 100%;
        text-align: left;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)


############################################################
# 初期化
############################################################

init_app()

# 全問題
df = st.session_state.full_df


############################################################
# UI構成
############################################################

cp.show_title()

genre, difficulty = cp.show_sidebar_filters(df)

# ゲーム未開始時は案内を表示
if not st.session_state.game_started:
    # マルチプレイヤー時の説明を追加
    if st.session_state.player_count > 1:
        st.markdown(f"""
        <div style='text-align:center; padding:2rem 1rem; background-color:#f8f9fa; border-radius:10px; margin:2rem 0;'>
            <p style='font-size:1.1rem; color:#666; margin-bottom:1rem;'><strong>マルチプレイヤーモード</strong></p>
            <p style='font-size:1rem; color:#666; line-height:1.8;'>
                ① プレイヤー数: <strong style='color:{ct.THEME_COLOR};'>{st.session_state.player_count}人</strong><br>
                ② 解答順: <strong style='color:{ct.THEME_COLOR};'>A → B → C → D</strong> の順番で交代<br>
                ③ 得点: 通常正解 <strong style='color:{ct.THEME_COLOR};'>1点</strong>、ヒント使用正解 <strong style='color:{ct.THEME_COLOR};'>0.5点</strong><br>
                ④ <strong style='color:{ct.THEME_COLOR};'>New Game</strong>ボタンを押してスタート！
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cp.show_start_guide()
    st.stop()

# ゲーム終了時は結果画面を表示
if st.session_state.game_finished:
    cp.show_final_results()
    st.stop()

# スコアボード表示（マルチプレイ時のみ、問題の上部）
cp.show_scoreboard()

# 現在の解答者表示（マルチプレイ時のみ）
cp.show_current_player()

# 初回ロード
if st.session_state.current_question is None:
    ut.load_next_question(df, genre, difficulty)
    st.session_state.question_start_time = __import__("time").time()

# 問題が存在しない場合のメッセージ表示
if st.session_state.no_questions_available:
    st.warning("この組み合わせの問題は存在しません", icon=ct.ICON_WARNING)
    st.info("サイドバーから別のジャンルや難易度を選択してください", icon=ct.ICON_INFO)
    st.stop()

# 時間制限チェック（全員解答前のみ）
if st.session_state.time_limit is not None and not st.session_state.all_players_answered:
    if st.session_state.question_start_time is not None:
        elapsed_time = __import__("time").time() - st.session_state.question_start_time
        remaining_time = st.session_state.time_limit - elapsed_time
        
        if remaining_time > 0:
            # 残り時間を表示
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <span style='font-size: 1.2rem; color: {ct.THEME_COLOR}; font-weight: bold;'>
                    {ct.ICON_TIMER.replace(':', '').replace('material/', '')} 残り時間: {int(remaining_time)}秒
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # 自動リロードで時間を更新
            if remaining_time <= 10:  # 残り10秒以下は警告色
                st.markdown(f"""
                <div style='text-align: center; margin-bottom: 1rem; padding: 0.5rem; background-color: #fff3cd; border-radius: 5px;'>
                    <span style='font-size: 1rem; color: #856404;'>
                        {ct.ICON_WARNING.replace(':', '').replace('material/', '')} 制限時間が迫っています！
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            # 時間切れ（現在のプレイヤーの解答を-1にして次へ）
            st.error(f"{ct.ICON_TIMER} {ct.PLAYER_NAMES[st.session_state.current_player]}さんの時間切れです！", icon=ct.ICON_WARNING)
            st.session_state.player_answers[st.session_state.current_player] = -1
            
            # 最後のプレイヤーなら結果表示、それ以外は次のプレイヤーへ
            if st.session_state.current_player == st.session_state.player_count - 1:
                st.session_state.all_players_answered = True
                st.session_state.show_result = True
            else:
                st.session_state.current_player += 1
                st.session_state.question_start_time = __import__("time").time()
            
            __import__("time").sleep(2)  # 2秒待機してメッセージを表示
            st.rerun()

cp.show_question()
cp.show_answer_area()
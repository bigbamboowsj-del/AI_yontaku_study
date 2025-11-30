"""
AIよんたくスタディで使用する定数をまとめたファイル
UIテキスト・アイコン・テーマカラーなどを一元管理する
"""

############################################################
# アプリ基本情報
############################################################

APP_TITLE = "AIよんたくスタディ"
SUBTITLE = "4択クイズ × 生成AI × 学習アプリ"

# CSVファイルのパス
QUESTIONS_CSV = "data/questions.csv"


############################################################
# カラー設定
############################################################

THEME_COLOR = "#2C7FFF"
THEME_SUB_COLOR = "#F0F4FF"


############################################################
# Material Icons（すべて icon= 形式で利用）
############################################################

ICON_CORRECT = ":material/check_circle:"
ICON_WRONG = ":material/cancel:"
ICON_HINT = ":material/lightbulb:"
ICON_HINT_TITLE = ":material/tips_and_updates:"
ICON_BOOK = ":material/menu_book:"
ICON_NEXT = ":material/arrow_forward:"
ICON_SELECT = ":material/arrow_drop_down_circle:"
ICON_CUSTOMIZE = ":material/tune:"
ICON_WARNING = ":material/warning:"
ICON_INFO = ":material/info:"
ICON_SUCCESS = ":material/celebration:"
ICON_GUIDE = ":material/description:"
PAGE_ICON = ":material/emoji_events:"   # トロフィー（クイズっぽい）

############################################################
# タイトル系テキスト
############################################################

TITLE_SELECT_OPTIONS = f"{ICON_SELECT} 選択肢"
TITLE_ANSWER = f"{ICON_BOOK} 解説"
TITLE_CUSTOMIZE = f"{ICON_CUSTOMIZE} カスタマイズ"


############################################################
# ボタン系
############################################################

BTN_NEW_GAME = ":material/sports_esports: New Game"
BTN_NEXT = f"{ICON_NEXT} 次の問題へ"
BTN_HINT = f"{ICON_HINT} Tips"


############################################################
# 選択肢ラベル（A/B/C/D）
############################################################

CHOICE_LABELS = ["A", "B", "C", "D"]


############################################################
# マルチプレイヤー設定
############################################################

# プレイヤー数オプション
PLAYER_COUNT_OPTIONS = [1, 2, 3, 4]
PLAYER_NAMES = ["A", "B", "C", "D"]

# 問題数制限オプション
QUESTION_LIMIT_OPTIONS = {
    "10問": 10,
    "20問": 20,
    "30問": 30,
    "全問": None
}

# 時間制限オプション（秒）
TIME_LIMIT_OPTIONS = {
    "無制限": None,
    "30秒": 30
}

# マルチプレイヤー用アイコン
ICON_PLAYER = ":material/person:"
ICON_TROPHY = ":material/emoji_events:"
ICON_TIMER = ":material/timer:"
ICON_SCOREBOARD = ":material/leaderboard:"
ICON_TARGET = ":material/gps_fixed:"
ICON_CHART = ":material/bar_chart:"  # 解答結果表示用
ICON_ARROW_NEXT = ":material/arrow_forward:"  # 次のプレイヤーへ
ICON_MEDAL_1 = ":material/looks_one:"  # 1位
ICON_MEDAL_2 = ":material/looks_two:"  # 2位
ICON_MEDAL_3 = ":material/looks_3:"  # 3位
ICON_BULLSEYE = ":material/adjust:"  # 正解マーク用
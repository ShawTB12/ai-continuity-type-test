import streamlit as st
import os
import json
import random
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import base64
import openai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# ページ設定
st.set_page_config(
    page_title="AI継続力タイプ診断",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSSスタイル
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1742&q=80");
            background-size: cover;
        }}
        .css-1d391kg, .css-1lcbmhc {{
            background-color: rgba(251, 251, 251, 0.85);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .main-title {{
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            color: #1E1E1E;
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        .sub-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.5rem;
            color: #3A3A3A;
            text-align: center;
            margin-bottom: 2rem;
        }}
        .chat-container {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .user-bubble {{
            background-color: #E8F4F8;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            text-align: right;
            position: relative;
        }}
        .assistant-bubble {{
            background-color: #F8F8F8;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            text-align: left;
            position: relative;
            color: #000000;
            font-weight: 500;
        }}
        .result-card {{
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .personality-title {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            color: #1E1E1E;
            margin-bottom: 1rem;
            text-align: center;
        }}
        .stButton>button {{
            background-color: #4A4A4A;
            color: white;
            border-radius: 30px;
            padding: 10px 25px;
            font-weight: bold;
            border: none;
            transition: all 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #2E2E2E;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        .stat-container {{
            padding: 20px;
            background-color: #F9F9F9;
            border-radius: 10px;
            margin: 10px 0;
        }}
        .rating-container {{
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }}
        .rating-button {{
            padding: 10px 15px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            margin: 0 5px;
            transition: all 0.2s;
        }}
        .rating-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .strength-item, .role-item, .growth-item {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

add_bg_from_url()

# セッション状態の初期化
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0

if 'answers' not in st.session_state:
    st.session_state.answers = {}

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

if 'type_result' not in st.session_state:
    st.session_state.type_result = None

# 継続力タイプに関する質問リスト
questions = [
    {"質問": "私はチームをリードし、目標達成のために人々を動かすことが得意だ", "タイプ": "指揮官型"},
    {"質問": "決断を下すとき、論理的な分析と詳細なデータを重視する", "タイプ": "分析者型"},
    {"質問": "アイデアよりも行動を重視し、すぐに実行に移すことが多い", "タイプ": "実行者型"},
    {"質問": "新しいアイデアを生み出したり、既存のやり方に革新をもたらすことが好きだ", "タイプ": "創造者型"},
    {"質問": "チーム内の調和を保ち、全員が協力して働けるよう橋渡しをするのが得意だ", "タイプ": "調整者型"},
    {"質問": "変化よりも安定を好み、一貫したパフォーマンスを発揮することを重視する", "タイプ": "安定者型"},
    {"質問": "細部まで注意を払い、プロジェクトを完璧に仕上げることを重視する", "タイプ": "完遂者型"},
    {"質問": "人々を励まし、モチベーションを高めることで、変化を促進するのが得意だ", "タイプ": "触媒型"},
    {"質問": "明確な目標を設定し、その達成のために戦略を立てることが好きだ", "タイプ": "指揮官型"},
    {"質問": "問題解決には時間をかけて情報を収集し、慎重に分析する", "タイプ": "分析者型"}
]

# 継続力タイプの定義
personality_types = {
    "指揮官型": {
        "英語名": "Commander",
        "説明": "目標を設定し、リーダーシップを発揮して他者を導く能力に優れています。",
        "強み": ["・明確な方向性を示す能力", "・迅速な意思決定力", "・他者を鼓舞するリーダーシップ"],
        "推奨役割": ["・プロジェクトリーダー", "・組織のマネージャー", "・戦略立案担当"],
        "育成ポイント": ["・他者の意見に耳を傾ける忍耐力を養う", "・詳細への注意を高める", "・感情的知性を向上させる"],
        "四柱推命": "あなたは天干の「甲」と地支の「寅」の性質を持ち合わせています。これは木の気が強く、成長と拡大を象徴します。指揮官型のあなたは物事を前進させる力強さと決断力を持っており、これは甲寅の持つ「開拓者精神」と「先駆的なエネルギー」に通じます。あなたのリーダーシップは春の目覚めのように周囲に活力を与え、組織を成長へと導きます。ただし、強すぎる木のエネルギーは時に柔軟性を欠くことがあります。水（知恵）と土（安定）のエネルギーを取り入れることで、よりバランスの取れたリーダーシップを発揮できるでしょう。",
        "陰陽五行": "陽の木の気質を持つあなたは、上昇と拡張のエネルギーに満ちています。継続的な成長と発展を象徴する木の性質は、あなたの先見性とビジョンの強さに表れています。五行の中で、あなたは木の「仁」の徳を体現し、周囲に慈愛と公正さをもたらします。木は金（規律）に制約されますが、火（情熱）を生み出します。従って、厳格な規則や枠組みに挑戦しながらも、周囲に熱意と活力を与える役割を担っています。バランスを取るためには、金（規律）の要素を尊重し、水（柔軟性）の知恵を取り入れることが重要です。"
    },
    "分析者型": {
        "英語名": "Analyzer",
        "説明": "情報を論理的に分析し、詳細を注意深く検討する能力に優れています。",
        "強み": ["・論理的思考力", "・複雑な問題の解決能力", "・データに基づいた判断力"],
        "推奨役割": ["・データアナリスト", "・研究開発部門", "・戦略的計画立案者"],
        "育成ポイント": ["・決断のスピードを向上させる", "・理論から実践へ移行する力を養う", "・直感的判断も取り入れる"],
        "四柱推命": "あなたは天干の「壬」と地支の「子」の特質を持っています。水の気が強く、深い知恵と洞察力を象徴します。分析者型のあなたは「壬子」が持つ「深遠な知性」と「冷静な判断力」を備えています。北方に位置する水のエネルギーは内向的で深く、表面的でなく本質を見抜く力をもたらします。あなたの思考は冬の静けさのように静かに深まり、根本的な理解へと至ります。ただし、水のエネルギーが過剰になると停滞することも。火（行動力）と土（実用性）のエネルギーを意識的に取り入れることで、分析から実行へとスムーズに移行できるでしょう。",
        "陰陽五行": "陽の水の特質を持つあなたは、深い知恵と洞察力というエネルギーを有しています。下降と内省を象徴する水の性質は、あなたの分析的思考と深い考察力として現れています。五行の中で、あなたは水の「智」の徳を体現し、知性と賢明さをもって周囲に影響を与えます。水は火（衝動）を抑制し、木（創造性）を育みます。したがって、性急な判断を冷静に分析し、新しいアイデアや方向性を育てる役割を担っています。バランスを保つためには、土（実用性）の要素を取り入れ、火（情熱）のエネルギーも活用することが大切です。"
    },
    "実行者型": {
        "英語名": "Implementer",
        "説明": "計画を具体的な行動に移し、効率的に実行する能力に優れています。",
        "強み": ["・実用的な問題解決能力", "・効率性の高い作業スタイル", "・行動力と実行力"],
        "推奨役割": ["・運営マネージャー", "・プロセス改善リーダー", "・プロジェクト実行担当"],
        "育成ポイント": ["・長期的な視点を養う", "・創造的思考を取り入れる", "・戦略的計画能力を高める"],
        "四柱推命": "あなたは天干の「丙」と地支の「午」の特質を持ち合わせています。これは火の気が強く、行動力と情熱を象徴します。実行者型のあなたは「丙午」の持つ「強い意志」と「実行力」を備えています。南方に位置する火のエネルギーは上昇し拡散する性質があり、これがあなたの迅速な行動力と決断力に表れています。あなたのエネルギーは真夏の太陽のように明るく活発で、プロジェクトに生命力を吹き込みます。ただし、火のエネルギーが過剰になると消耗することも。水（熟考）と金（規律）のエネルギーを取り入れることで、より持続可能な実行力を維持できるでしょう。",
        "陰陽五行": "陽の火の特質を持つあなたは、行動力と情熱に満ちたエネルギーを備えています。上昇と変容を象徴する火の性質は、あなたの実行力と決断の速さに表れています。五行の中で、あなたは火の「礼」の徳を体現し、周囲に活力と明るさをもたらします。火は金（構造）を溶かし、土（安定）を生み出します。したがって、固定的な枠組みを流動的に変化させ、新たな安定した状態へと物事を進める役割を担っています。バランスを保つためには、水（熟考）の要素を取り入れ、木（計画性）のエネルギーも活用することが賢明です。"
    },
    "創造者型": {
        "英語名": "Creator",
        "説明": "新しいアイデアを生み出し、革新的な解決策を考案する能力に優れています。",
        "強み": ["・創造性と革新性", "・柔軟な思考力", "・変化に対する適応力"],
        "推奨役割": ["・イノベーション部門", "・製品開発チーム", "・クリエイティブディレクター"],
        "育成ポイント": ["・実行力を強化する", "・詳細への注意を高める", "・プロジェクト管理スキルを向上させる"],
        "四柱推命": "あなたは天干の「乙」と地支の「卯」の特質を持ち合わせており、曲がりながらも成長する木の気を象徴しています。創造者型のあなたは「乙卯」の持つ「柔軟性」と「創造性」を備えています。東方に位置する陰の木のエネルギーは、柳のように柔軟でありながらも強く、これがあなたの革新的な発想力と適応力に表れています。あなたの創造性は春の風のように新鮮で、周囲に新しい可能性をもたらします。ただし、木のエネルギーが過剰になると拡散することも。金（集中力）と土（現実性）のエネルギーを取り入れることで、アイデアを形にする力が増すでしょう。",
        "陰陽五行": "陰の木の特質を持つあなたは、柔軟かつ創造的なエネルギーを備えています。成長と適応を象徴する木の性質は、あなたの革新性と柔軟な思考に表れています。五行の中で、あなたは木の「仁」の徳を柔らかな形で体現し、周囲に新しい視点と可能性をもたらします。木は土（慣習）を突き破り、火（ひらめき）を育みます。したがって、伝統的な考え方に挑戦し、新しいアイデアや創造的なエネルギーを生み出す役割を担っています。バランスを保つためには、金（規律）の要素を取り入れ、水（直感）のエネルギーをより活用することが有効です。"
    },
    "調整者型": {
        "英語名": "Coordinator",
        "説明": "チーム内の協力を促進し、効果的なコミュニケーションを確立する能力に優れています。",
        "強み": ["・対人関係スキル", "・チームワークの促進能力", "・異なる視点の統合力"],
        "推奨役割": ["・チームファシリテーター", "・人事部門", "・顧客関係管理"],
        "育成ポイント": ["・個人での決断力を強化する", "・直接的なフィードバック能力を高める", "・プロジェクト管理技術を習得する"],
        "四柱推命": "あなたは天干の「己」と地支の「未」の特質を持ち合わせており、これは土の気が強く、調和と安定を象徴します。調整者型のあなたは「己未」の持つ「調和」と「包容力」を備えています。中央に位置する土のエネルギーは四方をつなぎ、統合する性質があり、これがあなたのチームを結びつける能力と多様な視点を統合する力に表れています。あなたの存在は晩夏の大地のように実り多く豊かで、周囲に安定感をもたらします。ただし、土のエネルギーが過剰になると停滞することも。木（創造性）と金（明確さ）のエネルギーを取り入れることで、より活力ある調整者になれるでしょう。",
        "陰陽五行": "陰の土の特質を持つあなたは、調和と受容のエネルギーを備えています。安定と養育を象徴する土の性質は、あなたの協調性と人々を結びつける能力に表れています。五行の中で、あなたは土の「信」の徳を体現し、周囲に信頼と安心感をもたらします。土は水（不確実性）を堰き止め、金（構造）を育みます。したがって、混乱や不安定さを収め、明確な構造とルールを育てる役割を担っています。バランスを保つためには、木（変化）の要素を取り入れ、火（情熱）のエネルギーもより活用することで、革新と安定のバランスが取れるでしょう。"
    },
    "安定者型": {
        "英語名": "Stabilizer",
        "説明": "一貫性と信頼性を持って業務を遂行し、安定した結果を提供する能力に優れています。",
        "強み": ["・信頼性と一貫性", "・忍耐力", "・堅実な業務遂行能力"],
        "推奨役割": ["・品質管理", "・財務管理", "・リスク管理"],
        "育成ポイント": ["・変化への抵抗を減らす", "・柔軟性を高める", "・新しいアイデアを受け入れる姿勢を養う"],
        "四柱推命": "あなたは天干の「戊」と地支の「辰」の特質を持ち合わせており、これは土の気が強く、安定と耐久性を象徴します。安定者型のあなたは「戊辰」の持つ「堅実さ」と「忍耐力」を備えています。中央に位置する陽の土のエネルギーは山のように動かず、これがあなたの信頼性と一貫した行動力の源となっています。あなたの存在は大地のように揺るぎなく、周囲に安心感と安定をもたらします。ただし、土のエネルギーが過剰になると硬直することも。木（柔軟性）と水（適応力）のエネルギーを取り入れることで、変化にも対応できる安定感を維持できるでしょう。",
        "陰陽五行": "陽の土の特質を持つあなたは、安定と堅実さのエネルギーを備えています。支持と基盤を象徴する土の性質は、あなたの信頼性と一貫した業務遂行能力に表れています。五行の中で、あなたは土の「信」の徳を力強く体現し、周囲に確実性と信頼をもたらします。土は木（変化）を抑制し、金（精度）を生み出します。したがって、過度な変動や不安定さを抑え、確かな結果と精密さを生み出す役割を担っています。バランスを保つためには、木（革新）と水（流動性）の要素をより取り入れることで、安定しながらも時代の変化に対応できる柔軟性が育まれるでしょう。"
    },
    "完遂者型": {
        "英語名": "Finisher",
        "説明": "高い品質基準を持ち、細部に注意を払いながらプロジェクトを完遂する能力に優れています。",
        "強み": ["・細部への注意力", "・品質への強いこだわり", "・締め切りの厳守"],
        "推奨役割": ["・品質保証スペシャリスト", "・プロジェクト完了責任者", "・編集・校正担当"],
        "育成ポイント": ["・完璧主義を和らげる", "・大局的な視点を養う", "・効率性と品質のバランスを取る"],
        "四柱推命": "あなたは天干の「庚」と地支の「申」の特質を持ち合わせており、これは金の気が強く、精密さと完璧さを象徴します。完遂者型のあなたは「庚申」の持つ「正確さ」と「緻密さ」を備えています。西方に位置する金のエネルギーは秋の収穫のように実りをもたらし、これがあなたのプロジェクトを完璧に仕上げる能力に表れています。あなたの仕事は刃物のように鋭く明確で、不要なものを切り落とし本質を残します。ただし、金のエネルギーが過剰になると硬直することも。火（創造性）と木（成長）のエネルギーを取り入れることで、完璧さを追求しつつも柔軟性を持つことができるでしょう。",
        "陰陽五行": "陽の金の特質を持つあなたは、精密さと完全性のエネルギーを備えています。収斂と純化を象徴する金の性質は、あなたの細部への注意力と品質へのこだわりに表れています。五行の中で、あなたは金の「義」の徳を体現し、周囲に正確さと質の高さをもたらします。金は木（無秩序）を制御し、水（知恵）を生み出します。したがって、曖昧さや不完全さを排除し、明晰な知識と精度の高い結果を生み出す役割を担っています。バランスを保つためには、火（情熱）と土（寛容さ）の要素をより取り入れることで、完璧を追求しつつも柔軟性と大局観を持つことができるでしょう。"
    },
    "触媒型": {
        "英語名": "Catalyst",
        "説明": "変化を促進し、他者にインスピレーションを与える能力に優れています。",
        "強み": ["・他者を動機づける能力", "・変化を促進する力", "・熱意と活力"],
        "推奨役割": ["・変革マネージャー", "・コーチやメンター", "・営業・マーケティングリーダー"],
        "育成ポイント": ["・長期的なフォローアップ能力を養う", "・詳細への注意を高める", "・現実的な期待設定を心がける"],
        "四柱推命": "あなたは天干の「丁」と地支の「巳」の特質を持ち合わせており、これは火の気が強く、情熱と影響力を象徴します。触媒型のあなたは「丁巳」の持つ「感化力」と「輝き」を備えています。南方に位置する陰の火のエネルギーは灯りのように周囲を明るく照らし、これがあなたの他者を鼓舞し変化を促す能力に表れています。あなたの存在は初夏の暖かな日差しのように人々に活力を与え、成長を促します。ただし、火のエネルギーが過剰になるとエネルギーを消費しすぎることも。水（持続力）と土（安定）のエネルギーを取り入れることで、長期的な影響力を維持できるでしょう。",
        "陰陽五行": "陰の火の特質を持つあなたは、人々を温め、照らすエネルギーを備えています。変容と啓発を象徴する火の性質は、あなたの他者に影響を与え、変化を促す能力に表れています。五行の中で、あなたは火の「礼」の徳を優美に体現し、周囲に洞察と気づきをもたらします。火は木（潜在力）から生まれ、土（形態）を生み出します。したがって、潜在的な可能性を顕在化させ、新しい具体的な形に変える役割を担っています。バランスを保つためには、水（深さ）と金（緻密さ）の要素をより取り入れることで、情熱と冷静さ、変化と継続のバランスが取れた影響力を発揮できるでしょう。"
    }
}

# ロゴ表示関数
def display_logo():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 class="main-title">AI継続力タイプ診断</h1>
            <h2 class="sub-title">あなたの仕事への取り組み方を分析し、最適な継続力タイプを特定します</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )

# 継続力タイプ分析を行う関数
def analyze_personality_type():
    # OpenAI APIを使用して分析を行う
    try:
        # ユーザーの回答を整形
        user_responses = []
        for q_idx, answer in st.session_state.answers.items():
            question = questions[q_idx]["質問"]
            rating = answer
            rating_text = ""
            if rating == 1:
                rating_text = "全くそう思わない"
            elif rating == 2:
                rating_text = "あまりそう思わない"
            elif rating == 3:
                rating_text = "どちらともいえない"
            elif rating == 4:
                rating_text = "ややそう思う"
            elif rating == 5:
                rating_text = "とてもそう思う"
            
            user_responses.append(f"質問: {question}\n回答: {rating} ({rating_text})")
        
        # 全回答をまとめる
        all_responses = "\n\n".join(user_responses)
        
        # プロンプトの作成
        system_prompt = """
あなたは性格診断の専門家です。ユーザーの回答パターンを分析し、8つの継続力タイプ（指揮官型、分析者型、実行者型、創造者型、調整者型、安定者型、完遂者型、触媒型）から最も適切なタイプを特定してください。

各タイプの特徴:
1. 指揮官型 (Commander): 目標設定とリーダーシップに優れ、他者を導く能力がある
2. 分析者型 (Analyzer): 論理的分析と詳細な検討を得意とする
3. 実行者型 (Implementer): 計画を具体的な行動に移し、効率的に実行する
4. 創造者型 (Creator): 新しいアイデアと革新的な解決策を生み出す
5. 調整者型 (Coordinator): チーム内の協力促進と効果的なコミュニケーションを確立する
6. 安定者型 (Stabilizer): 一貫性と信頼性をもって業務を遂行し、安定した結果を提供する
7. 完遂者型 (Finisher): 高い品質基準を持ち、細部に注意しながらプロジェクトを完遂する
8. 触媒型 (Catalyst): 変化を促進し、他者にインスピレーションを与える

以下の回答に基づいて、最も当てはまる継続力タイプを1つ決定し、なぜそのタイプだと判断したかの理由も説明してください。また、各タイプのスコア（0-100の数値）も提供してください。
"""
        
        user_prompt = f"以下はユーザーの回答です：\n\n{all_responses}\n\nこの回答パターンから判断される継続力タイプとその理由、および各タイプのスコアを教えてください。"
        
        # OpenAI APIの呼び出し
        response = openai.ChatCompletion.create(
            model="gpt-4",  # または利用可能な最新モデル
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        # レスポンスからタイプ情報を抽出
        analysis_text = response.choices[0].message.content
        
        # 主要タイプを抽出（最初に言及されたタイプを採用）
        main_type = None
        for type_name in personality_types.keys():
            if type_name in analysis_text:
                main_type = type_name
                break
        
        # バックアップ: 主要タイプが見つからなかった場合はスコア計算
        if main_type is None:
            # 従来のスコア計算方法でバックアップ
            type_scores = {t: 0 for t in personality_types.keys()}
            type_counts = {t: 0 for t in personality_types.keys()}
            
            for q_idx, answer in st.session_state.answers.items():
                q_type = questions[q_idx]["タイプ"]
                type_scores[q_type] += answer
                type_counts[q_type] += 1
            
            # 平均スコアを計算
            for t in type_scores:
                if type_counts[t] > 0:
                    type_scores[t] = type_scores[t] / type_counts[t]
            
            # 主要タイプを特定
            main_type = max(type_scores, key=type_scores.get)
        
        # スコア情報を抽出 (例: "指揮官型: 85%")
        scores = {}
        for type_name in personality_types.keys():
            # パーセント表記を探す
            pattern = f"{type_name}[：:]\s*(\d+)[％%]"
            import re
            match = re.search(pattern, analysis_text)
            if match:
                scores[type_name] = int(match.group(1))
            else:
                # 数字のみを探す（LLMの出力形式が変わるかもしれないため）
                pattern = f"{type_name}[：:]\s*(\d+)"
                match = re.search(pattern, analysis_text)
                if match:
                    scores[type_name] = int(match.group(1))
                else:
                    # バックアップ値
                    scores[type_name] = 50
        
        # すべてのタイプのスコアが見つからない場合、最もスコアの高いタイプを100%として他を相対的に設定
        if not scores or max(scores.values(), default=0) == 0:
            # バックアップとして単純な計算方法を使用
            type_scores = {t: 0 for t in personality_types.keys()}
            type_counts = {t: 0 for t in personality_types.keys()}
            
            for q_idx, answer in st.session_state.answers.items():
                q_type = questions[q_idx]["タイプ"]
                type_scores[q_type] += answer
                type_counts[q_type] += 1
            
            # 平均スコアを計算
            for t in type_scores:
                if type_counts[t] > 0:
                    type_scores[t] = type_scores[t] / type_counts[t]
            
            # 最高スコアを100%として正規化
            max_score = max(type_scores.values())
            
            if max_score > 0:
                scores = {t: int((s / max_score) * 100) for t, s in type_scores.items()}
            else:
                scores = {t: 50 for t in personality_types.keys()}
        
        # 最終結果の作成
        result = {
            "main_type": main_type,
            "english_name": personality_types[main_type]["英語名"],
            "description": personality_types[main_type]["説明"],
            "scores": scores,
            "strengths": personality_types[main_type]["強み"],
            "recommended_roles": personality_types[main_type]["推奨役割"],
            "growth_points": personality_types[main_type]["育成ポイント"],
            "analysis_text": analysis_text  # AI分析のテキスト全体も保存
        }
        
        return result
        
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {str(e)}")
        # エラー発生時はバックアップの分析方法を使用
        
        # タイプごとのスコアを集計
        type_scores = {
            "指揮官型": 0,
            "分析者型": 0,
            "実行者型": 0,
            "創造者型": 0,
            "調整者型": 0,
            "安定者型": 0,
            "完遂者型": 0,
            "触媒型": 0
        }
        
        # 回答からスコアを計算
        type_counts = {t: 0 for t in type_scores.keys()}
        
        for q_idx, answer in st.session_state.answers.items():
            q_type = questions[q_idx]["タイプ"]
            type_scores[q_type] += answer
            type_counts[q_type] += 1
        
        # 平均スコアを計算
        for t in type_scores:
            if type_counts[t] > 0:
                type_scores[t] = type_scores[t] / type_counts[t]
        
        # 最高スコアを100%として正規化
        max_score = max(type_scores.values())
        
        if max_score > 0:
            normalized_scores = {t: (s / max_score) * 100 for t, s in type_scores.items()}
        else:
            normalized_scores = type_scores
        
        # 主要タイプを特定
        main_type = max(type_scores, key=type_scores.get)
        
        result = {
            "main_type": main_type,
            "english_name": personality_types[main_type]["英語名"],
            "description": personality_types[main_type]["説明"],
            "scores": normalized_scores,
            "strengths": personality_types[main_type]["強み"],
            "recommended_roles": personality_types[main_type]["推奨役割"],
            "growth_points": personality_types[main_type]["育成ポイント"],
            "analysis_text": "AIによる分析を行えませんでした。基本的な統計分析の結果を表示しています。"
        }
        
        return result

# 結果表示関数
def display_result(result):
    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
    
    st.markdown(f'<h2 class="personality-title">{result["main_type"]} ({result["english_name"]})</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 継続力タイプの概要")
        st.write(result["description"])
        
        st.markdown("### 強み")
        for strength in result["strengths"]:
            st.markdown(f'<div class="strength-item">{strength}</div>', unsafe_allow_html=True)
        
        st.markdown("### 推奨役割")
        for role in result["recommended_roles"]:
            st.markdown(f'<div class="role-item">{role}</div>', unsafe_allow_html=True)
        
        st.markdown("### 育成ポイント")
        for point in result["growth_points"]:
            st.markdown(f'<div class="growth-item">{point}</div>', unsafe_allow_html=True)
        
        # 四柱推命と陰陽五行の解釈を追加
        st.markdown("### 四柱推命からの解釈")
        st.markdown(f'<div class="eastern-philosophy-item">{personality_types[result["main_type"]]["四柱推命"]}</div>', unsafe_allow_html=True)
        
        st.markdown("### 陰陽五行からの解釈")
        st.markdown(f'<div class="eastern-philosophy-item">{personality_types[result["main_type"]]["陰陽五行"]}</div>', unsafe_allow_html=True)
        
        # AI分析結果の表示（新規追加）
        if "analysis_text" in result:
            st.markdown("### AIによる詳細分析")
            st.markdown(f'<div class="ai-analysis-item">{result["analysis_text"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        st.markdown("#### スコア分布")
        
        # スコア分布のグラフを作成
        scores = result["scores"]
        
        # 各タイプのスコアを表示
        for type_name, score in scores.items():
            st.markdown(f"##### {type_name}")
            st.progress(int(score))
            st.write(f"{int(score)}%")
            st.write("")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# メイン関数
def main():
    display_logo()
    
    # サイドバー
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1594824476967-48c8b964273f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=987&q=80", use_container_width=True)
        st.markdown("## AI継続力タイプ診断")
        st.markdown("このアプリはAIを活用して、あなたの仕事への取り組み方を分析し、8つの継続力タイプから最適なタイプを診断します。")
        st.markdown("### 使い方")
        st.markdown("1. 質問に順番に回答していきます")
        st.markdown("2. 各質問に1〜5の5段階で評価してください")
        st.markdown("3. すべての質問に回答すると、AIがあなたの継続力タイプを分析します")
        st.markdown("4. 診断結果とその解説が表示されます")
        
        # リセットボタン
        if st.button("診断をリセット"):
            st.session_state.messages = []
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.analysis_complete = False
            st.session_state.type_result = None
            st.rerun()
    
    # メインコンテンツ
    if not st.session_state.analysis_complete:
        # 質問応答フェーズ
        if st.session_state.current_question < len(questions):
            # 現在の質問を表示
            current_q = questions[st.session_state.current_question]["質問"]
            
            # 質問表示用のカード
            st.markdown(
                f"""
                <div style="background-color: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #000000; font-weight: 600; margin-bottom: 15px;">質問 {st.session_state.current_question + 1}/{len(questions)}</h2>
                    <p style="color: #000000; font-size: 1.2rem; font-weight: 500;">{current_q}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # 5段階評価のボタンを表示
            st.markdown("あなたの考えに最も当てはまるものを選んでください：")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("1: 全くそう思わない", key=f"rating_1_{st.session_state.current_question}"):
                    # 回答を記録
                    if len(st.session_state.messages) % 2 == 0:
                        ai_message = f"質問 {st.session_state.current_question + 1}/{len(questions)}: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                    # ユーザーの回答を追加
                    user_message = f"1: 全くそう思わない"
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.answers[st.session_state.current_question] = 1
                    
                    # 次の質問へ
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # すべての質問が終了した場合、分析を実行
                        with st.spinner("あなたの継続力タイプを分析中..."):
                            result = analyze_personality_type()
                            st.session_state.type_result = result
                            st.session_state.analysis_complete = True
                    
                    st.rerun()
            
            with col2:
                if st.button("2: あまりそう思わない", key=f"rating_2_{st.session_state.current_question}"):
                    # 回答を記録
                    if len(st.session_state.messages) % 2 == 0:
                        ai_message = f"質問 {st.session_state.current_question + 1}/{len(questions)}: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                    # ユーザーの回答を追加
                    user_message = f"2: あまりそう思わない"
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.answers[st.session_state.current_question] = 2
                    
                    # 次の質問へ
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # すべての質問が終了した場合、分析を実行
                        with st.spinner("あなたの継続力タイプを分析中..."):
                            result = analyze_personality_type()
                            st.session_state.type_result = result
                            st.session_state.analysis_complete = True
                    
                    st.rerun()
            
            with col3:
                if st.button("3: どちらともいえない", key=f"rating_3_{st.session_state.current_question}"):
                    # 回答を記録
                    if len(st.session_state.messages) % 2 == 0:
                        ai_message = f"質問 {st.session_state.current_question + 1}/{len(questions)}: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                    # ユーザーの回答を追加
                    user_message = f"3: どちらともいえない"
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.answers[st.session_state.current_question] = 3
                    
                    # 次の質問へ
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # すべての質問が終了した場合、分析を実行
                        with st.spinner("あなたの継続力タイプを分析中..."):
                            result = analyze_personality_type()
                            st.session_state.type_result = result
                            st.session_state.analysis_complete = True
                    
                    st.rerun()
            
            with col4:
                if st.button("4: ややそう思う", key=f"rating_4_{st.session_state.current_question}"):
                    # 回答を記録
                    if len(st.session_state.messages) % 2 == 0:
                        ai_message = f"質問 {st.session_state.current_question + 1}/{len(questions)}: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                    # ユーザーの回答を追加
                    user_message = f"4: ややそう思う"
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.answers[st.session_state.current_question] = 4
                    
                    # 次の質問へ
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # すべての質問が終了した場合、分析を実行
                        with st.spinner("あなたの継続力タイプを分析中..."):
                            result = analyze_personality_type()
                            st.session_state.type_result = result
                            st.session_state.analysis_complete = True
                    
                    st.rerun()
            
            with col5:
                if st.button("5: とてもそう思う", key=f"rating_5_{st.session_state.current_question}"):
                    # 回答を記録
                    if len(st.session_state.messages) % 2 == 0:
                        ai_message = f"質問 {st.session_state.current_question + 1}/{len(questions)}: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                    # ユーザーの回答を追加
                    user_message = f"5: とてもそう思う"
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.answers[st.session_state.current_question] = 5
                    
                    # 次の質問へ
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # すべての質問が終了した場合、分析を実行
                        with st.spinner("あなたの継続力タイプを分析中..."):
                            result = analyze_personality_type()
                            st.session_state.type_result = result
                            st.session_state.analysis_complete = True
                    
                    st.rerun()
        
    else:
        # 分析結果の表示
        st.markdown("## あなたの継続力タイプ診断結果")
        display_result(st.session_state.type_result)
        
        # ソーシャルシェアボタン（実際の機能はクライアントサイドJSで実装）
        st.markdown("""
        <div style="text-align: center; margin-top: 30px;">
            <h3>結果をシェアする</h3>
            <button style="background-color: #1DA1F2; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px;">Twitter</button>
            <button style="background-color: #4267B2; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px;">Facebook</button>
            <button style="background-color: #0077B5; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px;">LinkedIn</button>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
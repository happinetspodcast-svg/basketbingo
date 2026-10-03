import streamlit as st
import random
import textwrap
import json
import urllib.parse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- ページ設定 ---
st.set_page_config(page_title="バスケ・スタッツビンゴ", layout="centered")

# --- カスタムCSSによるデザイン刷新 ---
st.markdown("""
<style>
    .stApp {
        background-color: #fafbfc;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        letter-spacing: -0.5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] {
        background-color: #f4f6f8;
    }
</style>
""", unsafe_allow_html=True)

# --- サイドバー：YouTubeチャンネルへの誘導 ---
with st.sidebar:
    st.markdown("### 🎙️ 関連チャンネル")
    st.write("熱いトークをチェックしよう！")
    st.link_button(
        "📺 ハピネッツ・トークby秋田ブースター", 
        "https://www.youtube.com/channel/UCJ6na2Xp35fzf4ZM2EFCLwg",
        type="primary"
    )
    st.markdown("---")

# --- セッションステート初期化 ---
if 'positives' not in st.session_state:
    st.session_state.positives = [
        "チーム総得点 80点以上", "チーム総失点 70点以下", "チームスリー成功数 10本以上", 
        "チームスリー成功率 35%以上", "チームFT成功率 80%以上", "チーム2P成功率 55%以上", 
        "チームFG成功率 50%以上", "チームアシスト数 20回以上", "前半で45点以上得点", 
        "前半の失点を30点以下に抑える", "第3Q単体のスコアで相手を上回る", "第4Q単体のスコアで20点以上得点", 
        "一度もリードを許さない", "最大リード差 15点以上", "連続10得点以上（10-0 Run）", 
        "チーム総リバウンド数 40本以上", "オフェンスリバウンド数 10本以上", "相手のオフェンスリバウンドを 10本以下に抑える", 
        "リバウンド総数で相手を＋5本以上上回る", "セカンドチャンスポイント 15点以上", "チームターンオーバー数 10回以下", 
        "相手のターンオーバー数 15回以上", "相手TOからの得点 15点以上", "ペイント内得点 35点以上", 
        "ファストブレイクポイント 10点以上", "チーム合計スティール数 10回以上", "チーム合計ブロック数 5回以上", 
        "相手のFG成功率を 40%以下に抑える", "相手のスリー成功率を 30%以下に抑える", "相手のFT試投数 10本以下", 
        "相手のファストブレイクポイント 5点以下", "相手に24秒バイオレーションを誘発", "チーム被ファウル数 20個以上", 
        "相手チームの個人ファウル合計 20個以上", "相手の最多得点選手の得点を 20点未満に抑える", "ベンチメンバー合計得点 30点以上", 
        "ベンチメンバーのスリー合計 5本以上", "個人で20得点以上の選手が出る", "二桁得点達成者がチームで5人以上", 
        "ダブルダブル達成者が出現", "個人スリーポイント 5本以上成功", "個人オフェンスリバウンド 5本以上", 
        "個人アシスト 5回以上", "個人スティール 5回以上", "個人ブロック 5回以上", 
        "FT成功率100%(5本以上試投)", "ベンチ入りメンバー全員出場 ＆ 全員得点達成", "個人PLUS/MINUS「+15」以上", 
        "前半だけで二桁得点の選手が出る", "第4Qだけで10得点以上の選手が出る", "第1Qをリードして終える", 
        "第2Qをリードして終える", "第3Qをリードして終える", "第4Q残り5分時点でリード", 
        "最終スコア 5点差以内の接戦を制する", "全Qの失点がすべて20点未満", "相手に1Qで25点以上与えたQが0回", 
        "チームのFT試投数 20本以上", "A/TO Ratioが 2.0以上", "試合に勝利（W）する"
    ]

if 'negatives' not in st.session_state:
    st.session_state.negatives = [
        "チーム総得点 65点未満", "チームFG成功率 40%未満", "チームスリー成功率 25%未満", 
        "チームFT成功率 60%未満", "チームターンオーバー数 15回以上", "相手のスティール数が 10回以上", 
        "相手のブロック数が 5本以上", "オフェンスリバウンド 5本未満", "チームアシスト数 10回以下", 
        "チーム得点が 10点未満のQがある", "前半の得点が 30点未満", "相手TOからの得点 5点未満", 
        "セカンドチャンスポイント 5点以下", "ファストブレイクポイント 5点以下", "チーム総失点 85点以上", 
        "相手のFG成功率 50%以上", "相手のスリー成功率 40%以上", "相手のスリー成功数 15本以上", 
        "相手のオフェンスリバウンド 15本以上", "リバウンド総数で相手に-10本以上負ける", "相手のペイント内得点 40点以上", 
        "相手のセカンドチャンスポイント 20点以上", "相手のファストブレイクポイント 15点以上", "相手選手に30得点以上許す", 
        "相手にフリースローを 20本以上打たれる", "30失点以上与えたQがある", "チームファウル合計 20個以上", 
        "前半だけでチームファウルが 10個を超えてしまう", "最大ビハインド差 15点以上", "インサイドを制圧されペイント内失点 45点以上"
    ]

if 'rares' not in st.session_state:
    st.session_state.rares = [
        "【延長戦】オーバータイム（OT）突入", "【大記録】トリプルダブル達成者出現", "【完璧】チームFT試投10本以上で成功率100%", 
        "【互角】両チームの総リバウンド数が同数", "【鉄人】プレイタイム40分00秒の選手が出る", "【百発百中】スリー5本以上試投で成功率100%", 
        "【被ファウル祭】1人で被ファウル10回以上", "【代償】5ファウル(退場)が両チーム計3人以上", "【沈黙】どちらかのチームの1Q得点が5点以下", 
        "【劇的】残り0:00での得点が記録される"
    ]

if 'player_quests' not in st.session_state:
    st.session_state.player_quests = {
        "#0 トロイ・マーフィージュニア": {"text": "#0 マーフィー選手がダンクを決める", "enabled": True},
        "#2 栗原翼": {"text": "#2 栗原選手が10得点 or 5アシスト以上を記録する", "enabled": True},
        "#5 田口成浩": {"text": "#5 田口選手がスリー成功率50%以上で2本以上決める", "enabled": True},
        "#6 赤穂雷太": {"text": "#6 赤穂選手がプラスマイナスでチーム内上位3位以内に入る", "enabled": True},
        "#7 堀田尚秀": {"text": "#7 堀田選手がスリー3本以上成功させる", "enabled": True},
        "#10 ヤニー・ウェッツェル": {"text": "#10 ウェッツェル選手がダブルダブルを達成する", "enabled": True},
        "#11 ジャオ バイチン": {"text": "#11 ジャオ選手がスリー2本以上成功し12得点以上を記録する", "enabled": True},
        "#12 元田大陽": {"text": "#12 元田選手がプラスマイナスでチーム内上位3位以内に入る", "enabled": True},
        "#13 マーク・スミス": {"text": "#13 スミス選手が20得点以上を記録する", "enabled": True},
        "#17 中山拓哉": {"text": "#17 中山選手が5得点・5リバウンド・5アシスト以上を記録する", "enabled": True},
        "#18 岩屋頼": {"text": "#18 岩屋選手が10得点 or 5アシスト以上を記録する", "enabled": True},
        "#22 リード・トラビス": {"text": "#22 トラビス選手がダブルダブルを記録する", "enabled": True},
    }

if 'bingo_items' not in st.session_state:
    st.session_state.bingo_items = None
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 3
if 'checked_states' not in st.session_state:
    st.session_state.checked_states = []

# --- ビンゴ判定ロジック ---
def check_bingo(checked, size):
    lines = 0
    for i in range(size):
        if all(checked[i * size + j] for j in range(size)):
            lines += 1
    for j in range(size):
        if all(checked[i * size + j] for i in range(size)):
            lines += 1
    if all(checked[i * size + i] for i in range(size)):
        lines += 1
    if all(checked[i * size + (size - 1 - i)] for i in range(size)):
        lines += 1
    return lines

# --- 画像生成関数 ---
def create_bingo_image(items, size, checked):
    img_size = 750
    cell_size = img_size // size
    img = Image.new('RGB', (img_size, img_size), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    grid_link_color = "#E6004D"
    checked_bg_color = "#FFE6EE"

    color_positive = "#C70039"
    color_negative = "#0052CC"
    color_rare = "#9900CC"
    color_free = "#222222"

    player_quest_texts = [val["text"] for val in st.session_state.player_quests.values()]

    for i in range(size):
        for j in range(size):
            index = i * size + j
            text = items[index]
            is_checked = checked[index] if index < len(checked) else False
            
            x1 = j * cell_size
            y1 = i * cell_size
            x2 = (j + 1) * cell_size
            y2 = (i + 1) * cell_size

            if is_checked or text == "FREE":
                draw.rectangle([x1, y1, x2, y2], fill=checked_bg_color)

            if text == "FREE":
                text_color = color_free
            elif text in st.session_state.positives or text in player_quest_texts:
                text_color = color_positive  # 選手別お題もポジティブと同じ赤・ピンク系に
            elif text in st.session_state.negatives:
                text_color = color_negative
            else:
                text_color = color_rare

            length = len(text)
            if size == 3:
                if length > 24:
                    font_size, wrap_width, spacing = 18, 12, 4
                elif length > 16:
                    font_size, wrap_width, spacing = 21, 11, 5
                else:
                    font_size, wrap_width, spacing = 24, 10, 6
            else:
                if length > 20:
                    font_size, wrap_width, spacing = 11, 11, 2
                elif length > 12:
                    font_size, wrap_width, spacing = 13, 10, 3
                else:
                    font_size, wrap_width, spacing = 15, 9, 3

            try:
                font = ImageFont.truetype("NotoSansJP-VariableFont_wght.ttf", font_size)
                if hasattr(font, "set_variation_by_axes"):
                    font.set_variation_by_axes([700])
            except IOError:
                font = ImageFont.load_default()

            if text == "FREE":
                wrapped_text = "FREE"
            else:
                wrapped_text = "\n".join(textwrap.wrap(text, width=wrap_width))
            
            x_center = x1 + (cell_size // 2)
            y_center = y1 + (cell_size // 2)
            
            try:
                draw.text((x_center, y_center), wrapped_text, fill=text_color, font=font, anchor="mm", align="center", spacing=spacing)
            except Exception:
                draw.text((x1+5, y1+5), wrapped_text, fill=text_color, font=font)

            if is_checked and text != "FREE":
                margin = cell_size * 0.1
                draw.ellipse([x1 + margin, y1 + margin, x2 - margin, y2 - margin], outline=grid_link_color, width=6)

    for i in range(size + 1):
        draw.line([(i * cell_size, 0), (i * cell_size, img_size)], fill=grid_link_color, width=4 if size == 5 else 5)
        draw.line([(0, i * cell_size), (img_size, i * cell_size)], fill=grid_link_color, width=4 if size == 5 else 5)

    return img

# --- タブの作成 ---
tab1, tab2, tab3 = st.tabs(["🎲 ビンゴ作成・〇つけ", "✏️ ネタ（お題）の編集", "📖 専門スタッツ解説"])

with tab1:
    st.title("🏀 バスケ・スタッツビンゴ")
    st.write("モードを選んでビンゴを生成し、試合中にチェックを入れて遊ぼう！")

    # --- トップページでの選手別お題ON/OFF設定（一括ボタン付き） ---
    with st.expander("【ハピブー用】秋田ノーザンハピネッツ 選手別お題の有効化切り替え（クリックして展開）"):
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("すべてONにする"):
                for pk in st.session_state.player_quests:
                    st.session_state.player_quests[pk]["enabled"] = True
                    st.session_state[f"top_toggle_{pk}"] = True
                st.rerun()
        with col_btn2:
            if st.button("すべてOFFにする"):
                for pk in st.session_state.player_quests:
                    st.session_state.player_quests[pk]["enabled"] = False
                    st.session_state[f"top_toggle_{pk}"] = False
                st.rerun()
        
        st.markdown("---")
        cols_player = st.columns(2)
        idx_p = 0
        for player_key in list(st.session_state.player_quests.keys()):
            current_status = st.session_state.player_quests[player_key]["enabled"]
            with cols_player[idx_p % 2]:
                new_status = st.checkbox(player_key, value=current_status, key=f"top_toggle_{player_key}")
                st.session_state.player_quests[player_key]["enabled"] = new_status
            idx_p += 1

    st.markdown("---")
    grid_option = st.radio("ビンゴのサイズを選択", ["3 × 3 マス (9マス)", "5 × 5 マス (25マス)"], horizontal=True)
    selected_size = 3 if "3" in grid_option else 5

    if st.button("今週のビンゴを生成！", type="primary"):
        st.session_state.grid_size = selected_size
        total_cells = selected_size * selected_size
        
        active_player_items = [val["text"] for val in st.session_state.player_quests.values() if val["enabled"]]
        extended_positives = st.session_state.positives + active_player_items
        
        if selected_size == 3:
            sel_pos = random.sample(extended_positives, min(5, len(extended_positives)))
            sel_neg = random.sample(st.session_state.negatives, min(3, len(st.session_state.negatives)))
            sel_rare = random.sample(st.session_state.rares, min(1, len(st.session_state.rares)))
            items = sel_pos + sel_neg + sel_rare
            random.shuffle(items)
        else:
            free_index = 12
            num_pos = 15
            num_neg = 7
            num_rare = 2
            
            sel_pos = random.sample(extended_positives, min(num_pos, len(extended_positives)))
            sel_neg = random.sample(st.session_state.negatives, min(num_neg, len(st.session_state.negatives)))
            sel_rare = random.sample(st.session_state.rares, min(num_rare, len(st.session_state.rares)))
            
            pool = sel_pos + sel_neg + sel_rare
            random.shuffle(pool)
            
            items = pool[:free_index] + ["FREE"] + pool[free_index:]
            
        st.session_state.bingo_items = items
        st.session_state.checked_states = [False] * total_cells
        if selected_size == 5:
            st.session_state.checked_states[12] = True

    if st.session_state.bingo_items:
        size = st.session_state.grid_size
        items = st.session_state.bingo_items

        st.markdown("### 📝 〇つけパネル")
        st.caption("試合中に達成したお題のチェックボックスを押してください！")

        for i in range(size):
            cols = st.columns(size)
            for j in range(size):
                idx = i * size + j
                with cols[j]:
                    if items[idx] == "FREE":
                        st.checkbox("⭐ FREE", value=True, disabled=True, key=f"cell_{idx}")
                        st.session_state.checked_states[idx] = True
                    else:
                        is_checked = st.checkbox(f"{items[idx]}", value=st.session_state.checked_states[idx], key=f"cell_{idx}")
                        st.session_state.checked_states[idx] = is_checked

        bingo_count = check_bingo(st.session_state.checked_states, size)
        if bingo_count > 0:
            st.success(f"🎉 おめでとうございます！ **{bingo_count} BINGO** 達成中！ 🥳")

        st.markdown("---")
        st.subheader("🖼️ ビンゴカード画像プレビュー")
        
        img = create_bingo_image(items, size, st.session_state.checked_states)
        st.image(img, caption=f"生成されたビンゴカード ({size}x{size})", use_container_width=True)
        
        col_dl, col_share = st.columns(2)
        
        with col_dl:
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 画像として保存 (PNG)",
                data=byte_im,
                file_name=f"basketball_bingo_checked_{size}x{size}.png",
                mime="image/png"
            )
            
        with col_share:
            tweet_text = f"バスケ・スタッツビンゴで観戦中！現在「{bingo_count} BINGO」達成！ 🏀🔥\n#バスケスタッツビンゴ #Bリーグ #秋田ノーザンハピネッツ"
            encoded_text = urllib.parse.quote(tweet_text)
            twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            
            st.markdown(f"""
            <a href="{twitter_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #000000; color: white; padding: 9px 16px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 14px; margin-top: 0px;">
                    𝕏 で成果をシェアする
                </div>
            </a>
            """, unsafe_allow_html=True)

    st.markdown("---")
    active_player_count = sum(1 for v in st.session_state.player_quests.values() if v["enabled"])
    st.caption(f"現在の収録データ: ポジティブ {len(st.session_state.positives)}個 ＋ 選手別お題 {active_player_count}個有効 / ネガティブ {len(st.session_state.negatives)}個 / レア {len(st.session_state.rares)}個")

with tab2:
    st.title("✏️ ネタ（お題）の編集とバックアップ")
    
    st.warning("⚠️ **注意**: ブラウザを閉じたりページを更新すると、編集内容はデフォルトに戻ります。お気に入りのリストを維持したい場合は、下の **「設定のエクスポート」** のコードをコピーしてメモ帳などに保存してください。")
    
    pos_text = st.text_area("🟢 ポジティブなお題プール（改行区切り）", value="\n".join(st.session_state.positives), height=180)
    neg_text = st.text_area("🔴 ネガティブなお題プール（改行区切り）", value="\n".join(st.session_state.negatives), height=150)
    rare_text = st.text_area("🌟 レアなお題プール（改行区切り）", value="\n".join(st.session_state.rares), height=120)

    # --- レアなお題の下に選手関連のお題編集を配置 ---
    st.markdown("---")
    st.markdown("### 👤 選手別お題の内容編集")
    st.caption("選手ごとの個別お題のテキストを直接編集できます。")
    
    for player_key in list(st.session_state.player_quests.keys()):
        new_text = st.text_input(f"{player_key}", value=st.session_state.player_quests[player_key]["text"], key=f"edit_text_{player_key}")
        st.session_state.player_quests[player_key]["text"] = new_text

    st.session_state.positives = [line.strip() for line in pos_text.split("\n") if line.strip()]
    st.session_state.negatives = [line.strip() for line in neg_text.split("\n") if line.strip()]
    st.session_state.rares = [line.strip() for line in rare_text.split("\n") if line.strip()]

    st.markdown("---")
    st.subheader("📦 データセットのバックアップ・復元（コピペ用）")
    
    current_data = {
        "positives": st.session_state.positives,
        "negatives": st.session_state.negatives,
        "rares": st.session_state.rares,
        "player_quests": st.session_state.player_quests
    }
    json_str = json.dumps(current_data, ensure_ascii=False, indent=2)
    
    st.text_area("📤 設定のエクスポート（このコードをすべてコピーして保存）", value=json_str, height=100)
    
    import_str = st.text_area("📥 設定のインポート（保存したコードをここに貼り付け）", placeholder="ここにJSONコードを貼り付けてください", height=100)
    if st.button("🔄 コードから設定を復元する"):
        try:
            loaded_data = json.loads(import_str)
            if "positives" in loaded_data and "player_quests" in loaded_data:
                st.session_state.positives = loaded_data["positives"]
                st.session_state.negatives = loaded_data.get("negatives", st.session_state.negatives)
                st.session_state.rares = loaded_data.get("rares", st.session_state.rares)
                st.session_state.player_quests = loaded_data["player_quests"]
                st.success("設定を正常に読み込みました！ページを更新するか「ビンゴ作成」タブにお戻りください。")
                st.rerun()
            else:
                st.error("データの形式が正しくありません。")
        except Exception as e:
            st.error(f"読み込みに失敗しました（JSONの形式を確認してください）: {e}")

with tab3:
    st.title("📖 専門スタッツ用語の解説")
    st.write("バスケットボールの観戦やスタッツビンゴをより深く楽しむための用語集です。")
    
    st.markdown("""
    ### 📊 アシスト・ボールコントロール系
    - **A/TO Ratio (アシスト・ターンオーバー・レシオ)**
      - **計算式：** アシスト数 ÷ ターンオーバー数
      - **意味：** ボールをどれだけ安全にパスで回せているかを示す指標。一般的に **「2.0以上」** なら非常に優秀（ミスの半分以上の数アシストを産んでいる）とされ、**「1.0未満」** だとパスミスやボールを失う回数の方が多い不安定な状態を意味します。
    - **チームターンオーバー (TO)**
      - 味方のパスミスやトラベリング、3秒バイオレーションなどで**攻撃権を相手に譲ってしまった回数**です。

    ### 🎯 シュート・確率系
    - **FG (フィールドゴール) 成功率**
      - フリースローを除くすべてのシュート（2ポイントシュート ＋ 3ポイントシュート）の試投数に対する成功割合です。
    - **2P / 3P 成功率**
      - それぞれ2ポイントシュート、3ポイントシュートの成功割合。現代バスケでは3Pの確率（35%以上など）が勝敗を大きく左右します。
    - **FT (フリースロー) 成功率**
      - ファウルによって得られたフリースローの成功割合。接戦の終盤ではここを100%決めきれるかが勝負の分かれ目になります。

    ### 🧱 リバウンド・インサイド系
    - **OR (オフェンスリバウンド) / DR (ディフェンスリバウンド)**
      - シュートが外れた際に、自チームの攻撃権を継続するために奪い取るのがオフェンスリバウンド（OR）、相手の攻撃を終わらせるために取るのがディフェンスリバウンド（DR）です。
    - **セカンドチャンスポイント**
      - オフェンスリバウンドを奪った後、そのままゴールにねじ込んで獲得した得点のこと。ここが多いチームは泥臭く強いオフェンスができています。
    - **ペイント内得点 (インサイド得点)**
      - ゴール下の長方形のエリア（ペイントエリア）内で決めた得点。インサイドをどれだけ支配できているかのバロメーターになります。

    ### ⚡ 展開・個人スタッツ系
    - **ファストブレイクポイント (速攻得点)**
      - 相手のディフェンスが整う前に、素早く攻め込んで奪った得点（トランジションオフェンス）。
    - **ダブルダブル**
      - 得点、リバウンド、アシスト、スティール、ブロックの主要5項目のうち、**「2つの項目で二桁（10以上）」**を達成すること（例：15得点 11リバウンド）。
    - **トリプルダブル**
      - 上記5項目のうち**「3つの項目で二桁」**を達成する超大記録（例：20得点 10リバウンド 10アシスト）。
    - **PLUS/MINUS (プラス・マイナス)**
      - その選手がコートに出ている時間帯に、チームが相手を何点引き離したか（または離されたか）の収支。「+15」であれば、その選手がいる間にチームが15点リードを広げたことを表します。
    """)
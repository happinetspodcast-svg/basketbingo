import streamlit as st
import random
import textwrap
import json
import os
import urllib.parse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- ページ設定 ---
st.set_page_config(page_title="バスケ・スタッツビンゴ", layout="centered")

# --- カスタムCSSによるデザイン刷新（ダークモード対応・スマホ最適化） ---
st.markdown("""
<style>
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117;
            color: #fafbfc;
        }
    }
    @media (prefers-color-scheme: light) {
        .stApp {
            background-color: #fafbfc;
            color: #111111;
        }
    }
    
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        letter-spacing: -0.5px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .streamlit-expanderHeader {
        font-weight: bold;
        border-radius: 8px;
    }

    .stCheckbox label span {
        font-size: 15px !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- セッションステート初期化（難易度調整反映版） ---
if 'positives' not in st.session_state:
    st.session_state.positives = [
        "チーム総得点 80点以上", "チーム総失点 70点以下", "チームスリー成功数 9本以上", 
        "チームスリー成功率 35%以上", "チームFT成功率 75%以上", "チーム2P成功率 50%以上", 
        "チームFG成功率 45%以上", "チームアシスト数 18回以上", "前半で40点以上得点", 
        "前半の失点を32点以下に抑える", "第3Q単体のスコアで相手を上回る", "第4Q単体のスコアで18点以上得点", 
        "一度もリードを許さない", "最大リード差 12点以上", "連続8得点以上（8-0 Run）", 
        "チーム総リバウンド数 38本以上", "オフェンスリバウンド数 10本以上", "相手のオフェンスリバウンドを 10本以下に抑える", 
        "リバウンド総数で相手を＋5本以上上回る", "セカンドチャンスポイント 12点以上", "チームターンオーバー数 10回以下", 
        "相手のターンオーバー数 13回以上", "相手TOからの得点 12点以上", "ペイント内得点 32点以上", 
        "ファストブレイクポイント 8点以上", "チーム合計スティール数 7回以上", "チーム合計ブロック数 3回以上", 
        "相手のFG成功率を 43%以下に抑える", "相手のスリー成功率を 32%以下に抑える", "相手のFT試投数 14本以下", 
        "相手のファストブレイクポイント 8点以下", "相手に24秒バイオレーションを誘発", "チーム被ファウル数 18個以上", 
        "相手チームの個人ファウル合計 18個以上", "相手の最多得点選手の得点を 18点未満に抑える", "ベンチメンバー合計得点 25点以上", 
        "ベンチメンバーのスリー合計 4本以上", "個人で18得点以上の選手が出る", "二桁得点達成者がチームで4人以上", 
        "ダブルダブル達成者が出現", "個人スリーポイント 3本以上成功", "個人オフェンスリバウンド 3本以上", 
        "個人アシスト 5回以上", "個人スティール 3回以上", "個人ブロック 2回以上", 
        "FT成功率100%(3本以上試投)", "ベンチ入りメンバー全員出場", "個人PLUS/MINUS「+10」以上", 
        "前半だけで二桁得点の選手が出る", "第4Qだけで8得点以上の選手が出る", "第1Qをリードして終える", 
        "第2Qをリードして終える", "第3Qをリードして終える", "第4Q残り5分時点でリード", 
        "最終スコア 5点差以内の接戦を制する", "全Qの失点がすべて20点未満", "相手に1Qで22点以上与えたQが0回", 
        "チームのFT試投数 18本以上", "A/TO Ratioが 1.8以上", "試合に勝利（W）する"
    ]

if 'negatives' not in st.session_state:
    st.session_state.negatives = [
        "チーム総得点 65点未満", "チームFG成功率 40%未満", "チームスリー成功率 25%未満", 
        "チームFT成功率 60%未満", "チームターンオーバー数 15回以上", "相手のスティール数が 8回以上", 
        "相手のブロック数が 4本以上", "オフェンスリバウンド 5本未満", "チームアシスト数 10回以下", 
        "チーム得点が 10点未満のQがある", "前半の得点が 30点未満", "相手TOからの得点 5点未満", 
        "セカンドチャンスポイント 5点以下", "ファストブレイクポイント 5点以下", "チーム総失点 85点以上", 
        "相手のFG成功率 50%以上", "相手のスリー成功率 40%以上", "相手のスリー成功数 12本以上", 
        "相手のオフェンスリバウンド 12本以上", "リバウンド総数で相手に-10本以上負ける", "相手のペイント内得点 38点以上", 
        "相手のセカンドチャンスポイント 18点以上", "相手のファストブレイクポイント 12点以上", "相手選手に25得点以上許す", 
        "相手にフリースローを 20本以上打たれる", "25失点以上与えたQがある", "チームファウル合計 20個以上", 
        "前半だけでチームファウルが 10個を超えてしまう", "最大ビハインド差 15点以上", "インサイドを制圧されペイント内失点 40点以上"
    ]

if 'rares' not in st.session_state:
    st.session_state.rares = [
        "【延長戦】オーバータイム（OT）突入", "【大記録】トリプルダブル達成者出現", "【完璧】チームFT試投10本以上で成功率100%", 
        "【互角】両チームの総リバウンド数が同数", "【鉄人】プレイタイム32分以上の選手が出る", "【百発百中】スリー4本以上試投で成功率100%", 
        "【被ファウル祭】1人で被ファウル8回以上", "【代償】5ファウル(退場)が両チーム計3人以上", "【沈黙】どちらかのチームの1Q得点が8点以下", 
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
                text_color = color_positive
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

            font_path = "NotoSansJP-VariableFont_wght.ttf"
            try:
                font = ImageFont.truetype(font_path, font_size)
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
        
        # 新しくビンゴを生成した際に、前のチェック状態をリセットする
        for i in range(total_cells):
            if f"cell_{i}" in st.session_state:
                st.session_state[f"cell_{i}"] = False

    if st.session_state.bingo_items:
        size = st.session_state.grid_size
        items = st.session_state.bingo_items

        # 画像を描画する前に、現在のチェック状態（セッションステート）を先読みする
        current_checked = []
        for idx in range(len(items)):
            if items[idx] == "FREE":
                current_checked.append(True)
            else:
                current_checked.append(st.session_state.get(f"cell_{idx}", False))

        # --- ① 上部に ビンゴカード画像プレビュー を描画 ---
        st.subheader("🖼️ ビンゴカード画像プレビュー")
        
        img = create_bingo_image(items, size, current_checked)
        st.image(img, caption=f"生成されたビンゴカード ({size}x{size})", use_container_width=True)
        
        # --- 画像保存ボタン ---
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 画像として保存 (PNG)",
            data=byte_im,
            file_name=f"basketball_bingo_checked_{size}x{size}.png",
            mime="image/png"
        )

        st.markdown("---")

        # --- ② その下に 〇つけパネル を描画 ---
        st.markdown("### 📝 〇つけパネル")
        st.caption("試合中に達成したお題のチェックボックスを押してください！")

        for i in range(size):
            cols = st.columns(size)
            for j in range(size):
                idx = i * size + j
                with cols[j]:
                    if items[idx] == "FREE":
                        st.checkbox("⭐ FREE", value=True, disabled=True, key=f"cell_{idx}")
                    else:
                        st.checkbox(f"{items[idx]}", key=f"cell_{idx}")

        bingo_count = check_bingo(current_checked, size)
        if bingo_count > 0:
            st.success(f"🎉 おめでとうございます！ **{bingo_count} BINGO** 達成中！ 🥳")

        st.markdown("---")

        # --- ③ X（Twitter）シェアボタン ＆ YouTube誘導ボタン ---
        has_active_players = any(v["enabled"] for v in st.session_state.player_quests.values())
        if has_active_players:
            hashtags = "#バスケビンゴ #Bリーグ #akitanh #秋田ノーザンハピネッツ"
        else:
            hashtags = "#バスケビンゴ #Bリーグ"

        tweet_text = f"バスケ・スタッツビンゴで観戦中！現在「{bingo_count} BINGO」達成！ 🏀🔥\n{hashtags}"
        encoded_text = urllib.parse.quote(tweet_text)
        twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        
        st.markdown(f"""
        <a href="{twitter_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #000000; color: white; padding: 10px 16px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 10px;">
                𝕏 でシェアする
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://www.youtube.com/channel/UCJ6na2Xp35fzf4ZM2EFCLwg" target="_blank" style="text-decoration: none;">
            <div style="background-color: #FF0000; color: white; padding: 10px 16px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 14px;">
                📺 ハピネッツ・トークby秋田ブースター チャンネルはこちら
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

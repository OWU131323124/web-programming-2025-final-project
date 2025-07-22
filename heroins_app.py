import streamlit as st
import pandas as pd
import os
import base64

#ページ設定
st.set_page_config(page_title="推しおすすめアプリ", layout="centered")

#シュワシュワ
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #ffe4f0, #ffc0cb, #ff99cc);
    position: relative;
    overflow: hidden;
    height: 100vh;
}

/* 泡用固定コンテナ */
.bubble-container {
    pointer-events: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
}

/* 泡 */
.bubble {
    position: absolute;
    bottom: 0;
    background: rgba(255,255,255,0.3);
    border-radius: 50%;
    opacity: 0;
    animation-name: rise;
    animation-timing-function: ease-in;
    animation-iteration-count: infinite;
}

/* 泡の上昇アニメーション */
@keyframes rise {
    0% {
        transform: translateY(0) scale(1);
        opacity: 0;
    }
    20% {
        opacity: 0.4;
    }
    50% {
        opacity: 0.8;
    }
    100% {
        transform: translateY(-110vh) scale(1.2);
        opacity: 0;
    }
}

/* 100個の泡ランダム設定 */
""" + "\n".join([
    f""".bubble:nth-child({i}) {{
        left: {i * 0.9}%;
        width: {5 + (i % 10)}px;
        height: {5 + (i % 10)}px;
        animation-duration: {8 + (i % 10) * 1.0}s;
        animation-delay: {i * 0.3}s;
    }}""" for i in range(1, 101)
]) + """
}
</style>

<div class="bubble-container">
""" + "\n".join(["<div class='bubble'></div>" for _ in range(100)]) + """
</div>
""", unsafe_allow_html=True)



#CSS
st.markdown("""
<style>
.oshi-card {
    background-color: #ffe4e1;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(255, 182, 193, 0.5);
    text-align: center;
    margin-top: 20px;
    animation: fadeZoomIn 0.8s ease forwards;
}
.oshi-name {
    font-size: 28px;
    font-weight: bold;
    color: #ff1493;
    margin-bottom: 10px;
}
.oshi-intro {
    font-size: 18px;
    font-style: italic;
    color: #c71585;
    margin: 15px 0;
}
.sns-button {
    background-color: #ff69b4;
    color: white;
    padding: 8px 18px;
    margin: 5px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
    display: inline-block;
    transition: background-color 0.3s ease;
}
.sns-button:hover {
    background-color: #ff1493;
}
.image-container {
    text-align: center;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

#ロゴ画像
st.markdown("<div class='image-container'>", unsafe_allow_html=True)
st.image("images/heroins.png", width=300)
st.markdown("</div>", unsafe_allow_html=True)

#タイトル
st.markdown("<h1 style='text-align: center; color: #ff69b4;'>HEROINSE推しメンバー</h1>", unsafe_allow_html=True)

#データ読み込み
oshi_df = pd.read_csv("oshi_data.csv")
sns_df = pd.read_csv("oshi_sns.csv")

#SNS
sns_links = {}
for _, row in sns_df.iterrows():
    name = row["名前"]
    sns_type = row["プラットフォーム"]
    url = row["リンク"]
    if name not in sns_links:
        sns_links[name] = {}
    sns_links[name][sns_type] = url

#画像変換
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        b64_str = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{b64_str}"

#入力UI
st.subheader("🎀タイプ選択🎀")
col1, col2 = st.columns(2)
with col1:
    selected_seikaku = st.selectbox("🌟 ビジュアルで選ぶ", options=oshi_df["ビジュアル"].unique())
    selected_tokugi = st.selectbox("🎤 タイプで選ぶ", options=oshi_df["タイプ"].unique())
with col2:
    selected_miryoku = st.selectbox("💫 魅力で選ぶ", options=oshi_df["魅力"].unique())
    selected_tsuyomi = st.selectbox("🔥 強みで選ぶ", options=oshi_df["強み"].unique())

#推しをおすすめ
if st.button("✨ あなたの推しは？"):
    #完全一致フィルタ
    filtered_df = oshi_df[
        (oshi_df["ビジュアル"] == selected_seikaku) &
        (oshi_df["タイプ"] == selected_tokugi) &
        (oshi_df["魅力"] == selected_miryoku) &
        (oshi_df["強み"] == selected_tsuyomi)
    ]

    if not filtered_df.empty:
        sample_df = filtered_df.sample(min(3, len(filtered_df)))
    else:
        st.markdown("### 🔍 該当なし…　")
        st.markdown("<p style='font-size: 16px; color: gray;'>条件に近いメンバーを紹介！：</p>", unsafe_allow_html=True)

        #類似度を計算
        def calc_score(row):
            score = 0
            if row["ビジュアル"] == selected_seikaku:
                score += 1
            if row["タイプ"] == selected_tokugi:
                score += 1
            if row["魅力"] == selected_miryoku:
                score += 1
            if row["強み"] == selected_tsuyomi:
                score += 1
            return score

        oshi_df["score"] = oshi_df.apply(calc_score, axis=1)
        sample_df = oshi_df[oshi_df["score"] > 0].sort_values(by="score", ascending=False).head(3)

    if not sample_df.empty:
        for _, oshi in sample_df.iterrows():
            st.markdown(f"<div class='oshi-card' style='transform: scale(0.95);'>"
                        f"<div class='oshi-name'>{oshi['名前']} ちゃん</div>", unsafe_allow_html=True)

            image_path = os.path.join("images", oshi["画像ファイル"])
            if os.path.exists(image_path):
                b64_img = image_to_base64(image_path)
                st.markdown(f"""
                <div style="
                    width: 180px; height: 180px;
                    border-radius: 50%; 
                    overflow: hidden;
                    margin: 0 auto 15px auto;
                    box-shadow: 0 4px 10px rgba(255, 105, 180, 0.4);
                ">
                    <img src="{b64_img}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"画像ファイルが見つかりません: {image_path}")

            st.markdown(f"<p><strong>ビジュアル：</strong>{oshi['ビジュアル']}｜"
                        f"<strong>タイプ：</strong>{oshi['タイプ']}｜"
                        f"<strong>魅力：</strong>{oshi['魅力']}｜"
                        f"<strong>強み：</strong>{oshi['強み']}</p>", unsafe_allow_html=True)

            st.markdown(f"<p class='oshi-intro'>{oshi['紹介文']}</p>", unsafe_allow_html=True)

            links = sns_links.get(oshi['名前'], {})
            for label, url in links.items():
                st.markdown(f"<a href='{url}' target='_blank' class='sns-button'>{label}</a>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("条件に合う推しが見つかりませんでした😢")

import streamlit as st
import requests

API_URL = "https://clothing-store-api-uznd.onrender.com"

st.set_page_config(
    page_title="MELLOW | Clothing Store",
    page_icon="🤍",
    layout="wide"
)

# 韓系簡約風格 CSS
st.markdown("""
<style>
.stApp {
    background-color: #F8F7F3;
    color: #252525;
}
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
h1, h2, h3 {
    color: #252525;
}
.hero {
    background: #EEECE5;
    padding: 42px 35px;
    border-radius: 5px;
    margin-bottom: 28px;
}
.hero-title {
    font-size: 38px;
    font-weight: 700;
    letter-spacing: 5px;
}
.hero-subtitle {
    font-size: 13px;
    letter-spacing: 3px;
    color: #777;
    margin-top: 10px;
}
.product-name {
    font-size: 15px;
    font-weight: 600;
    margin-top: 8px;
}
.product-brand {
    color: #888;
    font-size: 12px;
}
.product-price {
    font-size: 19px;
    font-weight: 700;
    margin-top: 8px;
}
.product-stock {
    color: #999;
    font-size: 12px;
}
section[data-testid="stSidebar"] {
    background-color: #F0EFE9;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border-color: #E9E7E0;
}
</style>
""", unsafe_allow_html=True)

# 頂部品牌區
st.markdown("""
<div class="hero">
    <div class="hero-title">MELLOW.</div>
    <div class="hero-subtitle">
        SIMPLE STYLE · EVERYDAY FASHION
    </div>
    <p style="margin-top:22px;color:#555;">
        找到屬於你的日常穿搭風格。
    </p>
</div>
""", unsafe_allow_html=True)

# API 資料
@st.cache_data(ttl=60)
def get_categories():
    response = requests.get(
        f"{API_URL}/categories", timeout=60
    )
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=60)
def get_products(category_id=None, keyword=None):
    params = {"limit": 100}

    if category_id:
        params["category_id"] = category_id

    if keyword:
        params["keyword"] = keyword

    response = requests.get(
        f"{API_URL}/products",
        params=params,
        timeout=60
    )
    response.raise_for_status()
    return response.json()

# 左側篩選
st.sidebar.markdown("## 商品探索")
st.sidebar.caption("DISCOVER YOUR STYLE")

try:
    categories = get_categories()

    category_options = {"全部商品": None}

    for category in categories:
        category_options[
            category["category_name"]
        ] = category["category_id"]

    selected_category = st.sidebar.selectbox(
        "商品分類",
        list(category_options.keys())
    )

    keyword = st.sidebar.text_input(
        "搜尋商品",
        placeholder="輸入商品名稱..."
    )

    category_id = category_options[selected_category]

    products = get_products(category_id, keyword)

    # 商品區標題
    st.markdown("### NEW COLLECTION")
    st.caption("日常穿搭，簡單就很好看。")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"目前共有 **{len(products)}** 件商品")

    with col2:
        sort_option = st.selectbox(
            "排序方式",
            ["商品編號", "價格由低到高", "價格由高到低"],
            label_visibility="collapsed"
        )

    if sort_option == "價格由低到高":
        products.sort(key=lambda p: float(p["price"]))
    elif sort_option == "價格由高到低":
        products.sort(
            key=lambda p: float(p["price"]),
            reverse=True
        )

    st.divider()

    if not products:
        st.info("目前沒有符合條件的商品。")

    # 四欄商品卡片
    cols = st.columns(4, gap="medium")

    for index, product in enumerate(products):
        with cols[index % 4]:
            with st.container(border=True):

                image_url = product.get("image_url")

                if image_url:
                    st.image(
                        image_url,
                        use_container_width=True
                    )
                else:
                    st.info("暫無商品圖片")

                st.markdown(
                    f"<div class='product-name'>"
                    f"{product['product_name']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='product-brand'>"
                    f"{product.get('brand_name') or 'MELLOW'}"
                    f"　|　"
                    f"{product.get('category_name') or '服飾'}"
                    f"</div>",
                    unsafe_allow_html=True
                )

                price = float(product["price"])

                st.markdown(
                    f"<div class='product-price'>"
                    f"NT$ {price:,.0f}</div>",
                    unsafe_allow_html=True
                )

                st.caption(
                    f"庫存：{product.get('stock', 0)} 件"
                )

except requests.exceptions.RequestException:
    st.error("目前無法連接商品資料庫，請稍後再試。")

except Exception as e:
    st.error(f"發生錯誤：{e}")

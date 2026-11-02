
import streamlit as st
import requests

# API 網址
API_URL = "https://clothing-store-api-uznd.onrender.com"

st.set_page_config(
    page_title="服飾商品商城",
    page_icon="👕",
    layout="wide"
)

st.title("👕 服飾商品商城")
st.caption("Clothing Store - 商品資料庫系統")

# 取得分類
@st.cache_data
def get_categories():
    response = requests.get(f"{API_URL}/categories", timeout=60)
    response.raise_for_status()
    return response.json()

# 取得商品
@st.cache_data
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

# 側邊欄
st.sidebar.header("商品篩選")

try:
    categories = get_categories()
    category_options = {"全部商品": None}

    for category in categories:
        category_options[category["category_name"]] = category["category_id"]

    selected_category = st.sidebar.selectbox(
        "選擇商品分類",
        list(category_options.keys())
    )

    keyword = st.sidebar.text_input("搜尋商品名稱")

    category_id = category_options[selected_category]

    products = get_products(category_id, keyword)

    st.subheader(f"商品列表（共 {len(products)} 件）")

    if not products:
        st.info("目前沒有符合條件的商品。")

    # 商品卡片
    cols = st.columns(4)

    for index, product in enumerate(products):
        with cols[index % 4]:
            with st.container(border=True):
                image_url = product.get("image_url")

                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.info("暫無商品圖片")

                st.markdown(f"**{product['product_name']}**")
                st.caption(
                    f"{product.get('brand_name') or '未分類品牌'}｜"
                    f"{product.get('category_name') or '未分類'}"
                )
                st.markdown(f"### NT$ {product['price']}")

                st.caption(f"庫存：{product['stock']}")

except requests.exceptions.RequestException as e:
    st.error("目前無法連接商品 API，請稍後再試。")
    st.caption(str(e))
except Exception as e:
    st.error(f"發生錯誤：{e}")

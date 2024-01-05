import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import copy
import os
import json


# 讀取設定檔
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

import toml
from toml import TomlDecodeError

# 初始化身份驗證
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
#global login
#login = 0

# 初始化使用者資訊
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "shopping_cart": [],
        "order_history": [],
        "favorite_products": []
    }

# 用戶訂單歷史檔案路徑
orders_path = "./orders/"

# 確保訂單目錄存在
if not os.path.exists(orders_path):
    os.makedirs(orders_path)

# 加載用戶訂單歷史
def load_user_order_history(username):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        return pd.read_csv(order_history_file)
    return pd.DataFrame(columns=["title", "quantity"])


# 保存用戶訂單歷史
def save_user_order_history(username, current_orders):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        # 如果檔案已存在，則讀取並附加新訂單
        existing_orders = pd.read_csv(order_history_file)
        # 新增訂單時間列
        current_orders["order_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_orders = pd.concat([existing_orders, current_orders], ignore_index=True)
    else:
        # 如果檔案不存在，則創建新的 DataFrame
        # 新增訂單時間列
        current_orders["order_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_orders = pd.DataFrame(current_orders)

    # 保存更新後的訂單歷史
    updated_orders.to_csv(order_history_file, index=False)



def credit_counting(credit_used):
    df = load_user_order_history(st.session_state.user_info["name"])
    df["credit"] = df["total_price"] * 0.005
    total_credit = df["credit"].sum()
    total_credit -=credit_used
    return total_credit


#搜尋歷史功能
def update_history(query):
    history = st.session_state.get('history', [])
    history.append(query)
    st.session_state['history'] = history


def show_history():
    history = st.session_state.get('history', [])
    if history:
        st.write("Search History:")
        for item in reversed(history):
            st.write(f"- {item}")
    else:
        st.write("No search history yet.")
    popular_searches = get_popular_searches(history)
    st.write("Popular Searches:")
    for popular_search in popular_searches:
        st.write(f"- {popular_search}")


def get_popular_searches(history):
    search_counts = {}
    for item in history:
        search_counts[item] = search_counts.get(item, 0) + 1

    # Sort the searches by frequency and get the top 3
    popular_searches = sorted(search_counts, key=search_counts.get, reverse=True)[:3]
    return popular_searches

def login_page():
    # 在登入頁面以對話框的形式顯示用戶消息
    page =  st.sidebar.radio("選擇頁面", [  "商品總覽", "購物車", "訂單記錄","會員中心", "留言板", "最愛商品"])
    if page == "商品總覽":
        view_products()
    elif page == "訂單記錄":        
        order_history()
    elif page == "購物車":
        shopping_cart_page()
    elif page == "會員中心":
        membership_page()
    elif page == "留言板":
        message_board()
    elif page == "最愛商品":  
        favorite_products_page()



import csv

csv_file_path_book = 'book.csv'
csv_file_path_bonus = 'bonus.csv'
# 讀取CSV檔案，將資料存入DataFrame

books = pd.read_csv(csv_file_path_book)
bonus = pd.read_csv(csv_file_path_bonus)

# 初始化 session_state
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = []
#初始化 my_bonus
if "my_bonus" not in st.session_state:
        st.session_state.my_bonus = []
# 定義各頁面
    
# 首頁
def home():
    st.title("麗文書局團購系統")
    st.write("歡迎光臨麗文書局團購系統！")
    
# 獲取商品詳細資訊    
def get_product_info(title):
    # 在 books DataFrame 中尋找商品
    product_info = books[books['title'] == title].to_dict(orient='records')[0]
    return product_info

# 商品總覽
# 商品總覽
def view_products():
    st.title("商品總覽")
    # Search input on the main page
    search_input_key = 'search-input'
    query = st.text_input("請輸入商品名稱:", key=search_input_key)
    if st.button("Search"):
        update_history(query)
        show_history()
    # 部分匹配商品名稱
        filtered_books = books[books['title'].str.contains(query, case=False, na=False)]
        # 判斷搜尋內容是否存在相關產品
        if not filtered_books.empty:
            st.write(f"顯示與 '{query}' 相關的商品：")
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    # 過濾出包含搜索詞的商品
                    for index, row in filtered_books.iterrows():
                        st.markdown(f"<h2 style='font-size:20px;'>{row['title']}</h2>", unsafe_allow_html=True)
                        st.image(row["image"], caption=str(row["title"]), width=300)

                with col2:
                    # 顯示搜索到的商品
                    for index, row in filtered_books.iterrows():
                        st.write("")
                        st.write("")
                        st.write("")
                        st.write("")
                        st.write(f"**品牌:** {row['brand']}")
                        st.write(f"**類型:** {row['genre']}")
                        st.write(f"**金額:** {row['price']}")
                        st.write(f"**開團人數:** {row['group_size']}")
        else:
            # 在沒有匹配的情況下，顯示相應的消息
            st.write(f"顯示與 '{query}' 相關的商品：")
            st.write("沒有找到相應的商品，請嘗試其他搜索詞。")
    st.markdown("---")

    # 設定每行顯示的商品數量
    items_per_row = 3

    # 迴圈處理商品顯示
    for i in range(0, len(books), items_per_row):
        # 使用st.container建立3欄
        with st.container():
            row_columns = st.columns(3)
            # 每行顯示指定數量的商品
            for j in range(items_per_row):
                index = i + j
                if index < len(books):
                    # 在每個欄位中顯示商品資訊
                    with row_columns[j]:
                        st.markdown(f"<h2 style='font-size:20px;'>{books.at[index, 'title']}</h2>",
                                    unsafe_allow_html=True)
                        st.image(books.at[index, "image"], caption=str(books.at[index, "title"]), width=200)
                        st.write(f"**品牌:** {books.at[index, 'brand']}")
                        st.write(f"**類型:** {books.at[index, 'genre']}")
                        st.write(f"**金額:** {books.at[index, 'price']}")
                        st.write(f"**開團人數:** {books.at[index,'group_size']}")

                        quantity = st.number_input(f"購買數量", min_value=1, value=1, key=f"quantity_{index}")

                        if st.button(f"購買 {books.at[index, 'title']}", key=f"buy_button_{index}"):
                            if "shopping_cart" not in st.session_state:
                                st.session_state.shopping_cart = []
                            st.session_state.shopping_cart.append({
                                "title": books.at[index, "title"],
                                "quantity": quantity,
                                "total_price": int(books.at[index, 'price']) * int(quantity)  # Total price calculation
                            })
                            st.write(f"已將 {quantity} 項 {books.at[index, 'title']} 加入購物車")
                        # 加入我的最愛按鈕
                        if st.button("♡ 加入最愛", key=f"favorite_button_{index}"):
                            if "favorite_products" not in st.session_state.user_info:
                                st.session_state.user_info["favorite_products"] = []
                            product_title = books.at[index, 'title']
                            product_info = get_product_info(product_title)
                            st.session_state.user_info["favorite_products"].append(product_info)
                            st.write(f"已將 {product_title} 加入最愛")
            # 在每一行之後添加一個空行
            st.markdown("---")


# 顯示訂單
def display_order(selected_items_df):
    st.title("訂單明細")

    # 顯示購物車中的被勾選商品
    for index, row in selected_items_df.iterrows():
        st.write(f" {row['title']} *{row['quantity']}")

    # 顯示其他訂單相關資訊，例如總金額、訂單時間等
    total_expense = selected_items_df["total_price"].sum()
    st.write(f"總金額: {total_expense}")

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"訂單時間: {order_time}")

# 購物車頁面
def shopping_cart_page():
    st.title("購物車")
    clear_button = st.button("清空購物車")
    if clear_button:
        # 清空購物車
        st.session_state.shopping_cart = []
        st.write("購物車已清空！")
    if not st.session_state.shopping_cart:
        st.write("購物車是空的，快去選購您喜歡的書籍吧！")
    else:
        
        # Create a Pandas DataFrame from the shopping cart data
        df = pd.DataFrame(st.session_state.shopping_cart)

        # 使用 st.columns 將畫面分成兩個 column
        checkbox_column, table_column = st.columns([1, 12])  # 調整列寬比例

        # 在 DataFrame 中新增一列勾選框，同時設定 checkbox 的寬度
        with checkbox_column:
            st.write("")
            st.write("")
            df["勾選"] = [st.checkbox("", key=f"select_{index}") for index in df.index]
            selected_items_df = df[df["勾選"]]
        # 在 table_column 中顯示表格
        with table_column:
            st.dataframe(df, width=800)
        
        pay = st.button('結帳')

        if pay:
            st.session_state.show_payment = True
        if 'show_payment' in st.session_state and st.session_state.show_payment:
            Payment_page(selected_items_df)


# 結帳頁面
def Payment_page(selected_items_df):
    st.title("結帳")
    # 初始化 credit_history
    with st.form(key="購物清單") as form:
        購買詳情 = display_order(selected_items_df)
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay','貨到付款'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
    if submitted:
        # 只處理被勾選的商品
        selected_items_df = selected_items_df[selected_items_df["勾選"]]
        if not selected_items_df.empty:
            # 移除 "勾選" 列
            selected_items_df = selected_items_df.drop(columns=["勾選"])
            # 執行結帳操作
            st.session_state.show_payment = False  # 重置 show_payment 狀態
            order_history_df = pd.DataFrame(selected_items_df)
            # 保存用戶訂單歷史
            save_user_order_history(st.session_state.user_info["name"], order_history_df)
            st.session_state.shopping_cart = []
            st.write("交易成功！")
if "credit_used" not in st.session_state:
    st.session_state.credit_used = 0

#會員中心頁面            
def membership_page():
    st.title("會員中心")
    tab1, tab2, tab3 = st.tabs(["揪麗點數",'點數兌換', "我的商品券"])

    with tab1:
        st.subheader("揪麗點數累計")
        with st.container():
            df = load_user_order_history(st.session_state.user_info["name"])
            df["credit"] = df["total_price"] * 0.005
            total_credit = round(df["credit"].sum(), 2)
            df["credit"] = "+" + df["credit"].astype(str)
            used_credit = 0
            if "my_bonus" in st.session_state:
                for item in st.session_state.my_bonus:
                    used_credit = item.get("total_credit")
            total_credit -= used_credit
            #依照時間倒序排列
            df_sorted = df.sort_values(by='order_time', ascending=False)
            # 顯示表格
            st.dataframe(df_sorted, width = 800)
            st.subheader(f"總點數： {total_credit}")

    with tab2:
        st.subheader(f"點數兌換商品 可使用點數：{total_credit}")
        with st.container():
            items_per_row = 3

    # 迴圈處理兌換商品
        for i in range(0, len(bonus), items_per_row):
            # 使用st.container建立3欄
            with st.container():
                row_columns = st.columns(3)
                # 每行顯示指定數量的商品
                for j in range(items_per_row):
                    index = i + j
                    if index < len(bonus):
                        # 在每個欄位中顯示商品資訊
                        with row_columns[j]:
                            st.markdown(f"<h2 style='font-size:20px;'>{bonus.at[index, 'name']}</h2>",
                                        unsafe_allow_html=True)
                            st.image(bonus.at[index, "image"], caption=str(bonus.at[index, "name"]), width=200)
                            st.write(f"**點數:** {bonus.at[index, 'credit']}")
                            st.write(f"**活動至:** {bonus.at[index, 'time']}")

                            quantity = st.number_input(f"兌換數量", min_value=1, value=1, key=f"quantity_{index}")
                            used_credit = quantity * bonus.at[index, "credit"]

                            if st.button(f"兌換 {bonus.at[index, 'name']}", key=f"buy_button_{index}"):
                                
                                if "my_bonus" not in st.session_state:
                                    st.session_state.my_bonus = []
                                if total_credit>= used_credit:
                                    st.session_state.my_bonus.append({
                                        "name": bonus.at[index, "name"],
                                        "quantity": quantity,
                                        "total_credit": used_credit
                                    })
                                    st.write(f" {quantity} 項 {bonus.at[index, 'name']} 已加入我的商品券中")
                                else:
                                    st.warning("點數不足，無法兌換此商品")

                # 在每一行之後添加一個空行
                st.markdown("---")

    with tab3:
        st.subheader("我的商品券")
        with st.container():
            items_per_row_coupon = 3

            # 迴圈顯示商品券
            for i in range(0, len(st.session_state.my_bonus), items_per_row_coupon):
                # 使用st.container建立3欄
                with st.container():
                    row_columns = st.columns(3)
                    # 每行顯示指定數量的商品券
                    for j in range(items_per_row_coupon):
                        index = i + j
                        if index < len(st.session_state.my_bonus):
                        # 在每個欄位中顯示商品券資訊
                            with row_columns[j]:
                                # 使用商品券名稱（name）作為索引，找到對應的圖片和文字
                                coupon_name = st.session_state.my_bonus[index]['name']
                                coupon_info = bonus[bonus['name'] == coupon_name].iloc[0]
                                st.markdown(f"<h2 style='font-size:20px;'>{coupon_info['name']}</h2>",
                                            unsafe_allow_html=True)
                                st.image(coupon_info['image'], caption=str(coupon_info['name']), width=200)
                                st.write(f"**數量:** {st.session_state.my_bonus[index]['quantity']}")
                    # 在每一行之後添加一個空行
                    st.markdown("---")


# 留言頁
def message_board():
    # 初始化 session_state
    if "past_messages" not in st.session_state:
        st.session_state.past_messages = []

    # 在應用程式中以對話框的形式顯示用戶消息
    with st.chat_message("user"):
        st.write("歡迎來到留言板！")

    # 接收用戶輸入
    prompt = st.text_input("在這裡輸入您的留言")

    # 如果用戶有輸入，則將留言加入 session_state 中
    if prompt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.past_messages.append({"user": "user", "message": f"{timestamp} - {prompt}"})

    # 留言板中顯示過去的留言
    with st.expander("過去的留言"):
        # 顯示每條留言
        for message in st.session_state.past_messages:
            with st.chat_message(message["user"]):
                st.write(message["message"])

#最愛商品
def favorite_products_page():
    st.title("我的最愛")

    if not st.session_state.user_info["favorite_products"]:
        st.write("您還沒有添加最愛的商品。快去商品總覽頁面尋找您喜歡的商品吧！")
    else:
        st.write("您的最愛商品清單：")
        for product_info in st.session_state.user_info["favorite_products"]:
            st.image(product_info["image"], width=200)  # 顯示商品圖片
            st.subheader(f" {product_info['title']}")
            st.write(f"**品牌:** {product_info['brand']}")
            st.write(f"**類型:** {product_info['genre']}")
            st.write(f"**金額:** {product_info['price']}")
            st.write("---")

# 訂單歷史頁面
def order_history():
    st.title("訂單歷史")
    # 將訂單資料轉換為 DataFrame
    df = load_user_order_history(st.session_state.user_info["name"])

    # 顯示表格
    st.dataframe(df, width = 800)

def main():
    
    st.title("麗文書店團購系統")
    st.write("歡迎光臨揪麗團購系統！")   
    st.image("https://allez.one/wp-content/uploads/2022/04/%E9%9B%BB%E5%95%86%E7%B6%93%E7%87%9F1.jpg")
    st.session_state.login = False
    
    # 登入
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.login = authentication_status
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.session_state.user_info["name"] = name
        # 加載用戶訂單歷史
        st.session_state.user_info["order_history"] = load_user_order_history(username)
        st.write(f'Welcome *{name}*')  
        login_page()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()




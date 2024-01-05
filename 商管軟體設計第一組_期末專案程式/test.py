import streamlit as st
import pandas as pd

# st.data_editor 函數的參數 num_rows 被設置為 "dynamic"。這會使得編輯界面的行數隨著數據的多寡而動態調整
df = pd.DataFrame(
    [
       {"course": "Chinese", "rating": 4, "Done_Today": True},
       {"course": "English", "rating": 5, "Done_Today": False},
       {"course": "Math", "rating": 3, "Done_Today": False},
   ]
)
edited_df = st.data_editor(df, num_rows="dynamic")

favorite_course = edited_df.loc[edited_df["rating"].idxmax()]["course"]
st.markdown(f"Your favorite course is **{favorite_course}** 🎈")
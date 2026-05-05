import streamlit as st
import pandas as pd

df = pd.DataFrame({"A": [1, -2, 3], "B": ["a", "b", "c"]})
def color_negative_red(val):
    color = 'red' if val < 0 else 'black'
    return f'color: {color}'

try:
    event = st.dataframe(df.style.map(color_negative_red, subset=['A']), on_select="rerun", selection_mode="single-row")
    st.write("Selected rows:", event.selection.rows)
except Exception as e:
    st.write("Error:", e)

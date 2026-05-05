import streamlit as st
import pandas as pd

df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
event = st.dataframe(df, on_select="rerun", selection_mode="single-row")
st.write(event)

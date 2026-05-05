import FinanceDataReader as fdr
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')
try:
    df = fdr.DataReader("069500", today)
    print(df)
except Exception as e:
    print(e)

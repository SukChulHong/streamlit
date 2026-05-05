import FinanceDataReader as fdr

try:
    df_krx = fdr.StockListing('KRX')
    print("KRX matches:", df_krx[df_krx['Name'].str.contains('KODEX 200', na=False)][['Code', 'Name']])
except Exception as e:
    print(e)

try:
    df_etf = fdr.StockListing('ETF/KR')
    print("ETF/KR matches:", df_etf[df_etf['Name'].str.contains('KODEX 200', na=False)][['Symbol', 'Name']])
except Exception as e:
    print("ETF error:", e)

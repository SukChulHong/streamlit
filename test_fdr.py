import FinanceDataReader as fdr

def get_symbol_by_name(name):
    df_krx = fdr.StockListing('KRX')
    # Name column contains the Korean names
    result = df_krx[df_krx['Name'] == name]
    if not result.empty:
        return result.iloc[0]['Code'] # Or 'Symbol' depending on FDR version
    return None

print(fdr.StockListing('KRX').head())

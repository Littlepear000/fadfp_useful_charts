import imf_datatools
import pandaspro as cpd
import pandas as pd
from fadfpdata import cname_to_ifs

update_date = '20251117'
download = 0

if download == 1:
    ticker = cpd.pwread(r'EMBIG/Bloomberg EMBIG tickers.xlsx', sheet_name='filtered_list')[0]
    ticker_list = ticker['ticker'].values.tolist()
    ticker_dict = dict(zip(ticker["ticker"], ticker[["country", "ifscode"]].values.tolist()))

    embig_raw = imf_datatools.get_edi_bloomberg_data(ticker_list, 'PX_LAST')
    embig_raw.columns = [col.replace("PX_LAST.D", "") for col in embig_raw.columns]
    rename_map = {ticker.upper(): values[0] for ticker, values in ticker_dict.items()}
    embig_raw.rename(columns=rename_map, inplace=True)

    embig_raw.to_csv(fr'EMBIG/EMBIG_raw_{update_date}.csv')
if download == 0:
    embig_raw = pd.read_csv(fr'EMBIG/EMBIG_raw_{update_date}.csv')
    embig_raw = embig_raw.set_index("dates")
    embig_raw.index = pd.to_datetime(embig_raw.index)

monthly = embig_raw.resample("M").mean().reset_index()
monthly_long = monthly.melt(
    id_vars='dates',
    value_name='embig',
    var_name='country'
)
monthly_long['ifscode'] = monthly_long['country'].map(cname_to_ifs)
monthly_long.loc[monthly_long['country']=='Global', 'ifscode'] = 1
monthly_long = monthly_long[['dates', 'country', 'ifscode', 'embig']]
monthly_long.to_csv(fr'EMBIG/EMBIG_monthly_{update_date}.csv', index=False)


monthly_long['year'] = monthly_long['dates'].dt.year
monthly_long['month'] = monthly_long['dates'].dt.month
monthly_long_temp = monthly_long[['ifscode', 'year', 'month', 'embig']]
monthly_long_temp.to_csv(fr"C:\Users\xli7\OneDrive - International Monetary Fund (PRD)\Balasundharam, Vybhavi's files - FM - Spreads\Data\Cleaned Datasets\EMBIG_monthly_{update_date}.csv", index=False)



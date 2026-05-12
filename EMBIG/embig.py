from imf_datatools import idata_utilities
import pandaspro as cpd
import pandas as pd
from fadfpdata import cname_to_ifs

update_date = '20260512'
download = 1

if download == 1:
    idata_utilities.PRIVATE = True

    ticker_raw = cpd.pwread(r'EMBIG/Bloomberg EMBIG tickers.xlsx', sheet_name='filtered_list')[0]
    ticker_raw['ticker'] = ticker_raw['ticker'].str.upper().str.replace(' ', '_')
    ticker_list = '+'.join(ticker_raw['ticker'].values.tolist())
    ticker_dict = dict(zip(ticker_raw["ticker"], ticker_raw[["country", "ifscode"]].values.tolist()))

    embig_raw = idata_utilities.get_idata_data('IMF.CSF:BBGDL', key=ticker_list + '.PX_LAST.D')
    embig_raw.columns = [col.replace(".PX_LAST.D", "") for col in embig_raw.columns]
    rename_map = {ticker.upper(): values[0] for ticker, values in ticker_dict.items()}
    embig_raw.rename(columns=rename_map, inplace=True)

    embig_raw.to_csv(fr'EMBIG/daily/EMBIG_raw_{update_date}.csv')
    print('Download completed.')
if download == 0:
    embig_raw = pd.read_csv(fr'EMBIG/daily  /EMBIG_raw_{update_date}.csv')
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
monthly_long_temp.to_csv(fr"EMBIG\monthly\EMBIG_monthly_{update_date}.csv", index=False)



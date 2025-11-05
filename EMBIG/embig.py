import imf_datatools
import pandaspro as cpd

ticker = cpd.pwread(r'EMBIG/Bloomberg EMBIG tickers.xlsx', sheet_name='filtered_list')[0]
ticker_list = ticker['ticker'].values.tolist()
ticker_dict = dict(zip(ticker["ticker"], ticker[["country", "ifscode"]].values.tolist()))

embig_raw = imf_datatools.get_edi_bloomberg_data(ticker_list, 'PX_LAST')
embig_raw.columns = [col.replace("PX_LAST.D", "") for col in embig_raw.columns]
rename_map = {ticker.upper(): values[0] for ticker, values in ticker_dict.items()}
embig_raw.rename(columns=rename_map, inplace=True)

embig_raw.to_csv(r'EMBIG/EMBIG_raw_20251105.csv')

monthly = embig_raw.resample("M").mean()

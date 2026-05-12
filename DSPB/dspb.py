from fadfpdata import iData, Dummy
import numpy as np
import pandaspro as cpd
import pandas as pd

update_date = '20260324'
excelfile = fr'DSPB/DSPB_{update_date}.xlsx'

weo = iData()
dum = Dummy()
inc_dict = {
    'Global': dum.noagg,
    'Advanced Economies': dum.ae,
    'Emerging Markets': dum.em,
    'Low-Income Developing Countries': dum.lic
}

dspb = weo.copy()
dspb['g'] = dspb.groupby('ifscode')['ngdp'].pct_change()
dspb['ggxwdg_l'] = dspb.groupby('ifscode')['ggxwdg'].shift(1)
dspb['ggxwdg_gdp_l'] = dspb.groupby('ifscode')['ggxwdg_gdp'].shift(1)
dspb['r'] = np.where(dspb['ggxwdg_l'] == 0, np.nan, dspb['ggei'] / dspb['ggxwdg_l'])
dspb['rlessg'] = np.where((1 + dspb['g']) == 0, np.nan,
                          (dspb['r'] - dspb['g']) / (1 + dspb['g']) * 100)
dspb['dspb'] = dspb['ggxwdg_gdp_l'] * dspb['rlessg'] / 100
dspb['pb_minus_dspb'] = dspb['ggxonlb_gdp'] - dspb['dspb']
dspb.loc[dspb['pb_minus_dspb'] <= -10, 'pb_minus_dspb'] = np.nan    #exclude outliers


def summarize_pb_stats_by_year(df, inc_dict):
    results = []
    for group, countries in inc_dict.items():
        sub = df[df['ifscode'].isin(countries)].copy()
        if sub.empty:
            continue

        world_gdp_by_year = df.groupby('year')['ngdpd'].sum()

        # Loop through each year
        for year, sub_y in sub.groupby('year'):
            # --- 1. Percentage of countries with pb_minus_dspb > 0 ---
            total_countries = sub_y['ifscode'].nunique()
            pos_countries = sub_y.loc[sub_y['pb_minus_dspb'] < 0, 'ifscode'].nunique()
            pct_countries_pos = pos_countries / total_countries * 100 if total_countries > 0 else np.nan

            # --- 2. Share of NGDPD from countries with pb_minus_dspb > 0 ---
            ngdpd_total = world_gdp_by_year.get(year, np.nan)
            ngdpd_pos = sub_y.loc[sub_y['pb_minus_dspb'] < 0, 'ngdpd'].sum()
            print(f'====={year} global gdp {ngdpd_total}; {group} dspb gdp {ngdpd_pos}')
            pct_ngdpd_pos = ngdpd_pos / ngdpd_total * 100 if ngdpd_total > 0 else np.nan

            # --- 3. Distribution statistics ---
            sub_neg = sub_y.loc[sub_y['pb_minus_dspb'] < 0]
            if not sub_neg.empty:
                desc = sub_neg['pb_minus_dspb'].describe(percentiles=[0.25, 0.5, 0.75])
                q25 = desc['25%']
                median = desc['50%']
                q75 = desc['75%']
                mean = desc['mean']
                iqr = q25 - q75
            else:
                q25 = median = q75 = mean = iqr = np.nan

            results.append({
                'year': year,
                'group': group,
                'Share of Countries': pct_countries_pos,
                # 'Share of GDP': pct_ngdpd_pos,
                '25th': q25,
                'Median': median,
                '75th': q75,
                'Mean': mean,
                'IQR': iqr
            })

    # Combine all results into a single DataFrame
    result_df = cpd.FramePro(results)

    # --- Define the custom group order ---
    group_order = [
        'Global',
        'Advanced Economies',
        'Emerging Markets',
        'Low-Income Developing Countries'
    ]

    # Convert 'Group' column to categorical with the defined order
    result_df['group'] = pd.Categorical(result_df['group'], categories=group_order, ordered=True)

    # Sort by Year and Group order
    result_df = result_df.sort_values(['year', 'group']).reset_index(drop=True)
    return result_df


summary_all = summarize_pb_stats_by_year(dspb, inc_dict)
summary_1year = summary_all.query('year==2029')

ps = cpd.PutxlSet(excelfile)
ps.putxl(summary_1year, sheet_name='chart', cell='B1', index=False)

dspb.loc[dspb['ifscode'].isin(dum.ae), 'inc_group'] = 'AE'
dspb.loc[dspb['ifscode'].isin(dum.em), 'inc_group'] = 'EM'
dspb.loc[dspb['ifscode'].isin(dum.lic), 'inc_group'] = 'LIDC'
dspb_clean = dspb.noagg[['ifscode', 'inc_group', 'year', 'ggxonlb_gdp', 'dspb', 'pb_minus_dspb']].query('year>=2000')
ps.putxl(dspb_clean, sheet_name='data', cell='A1', index=False)

check = dspb.inlist('year', 2029).inlist('ifscode', dum.em)
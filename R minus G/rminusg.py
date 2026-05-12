from fadfpdata import iData, Dummy
import numpy as np
import pandaspro as cpd

update_date = '20260324'
excelfile = fr'R minus G/R minus G_{update_date}.xlsx'

weo = iData()
dum = Dummy()
inc_dict = {
    'Global': dum.noagg,
    'Advanced Economies': dum.ae,
    'Emerging Markets': dum.em,
    'Low-Income Developing Countries': dum.lic
}

rminusg = weo[['ifscode', 'year', 'ggei', 'ggxwdg', 'ngdp', 'ggxcnl_gdp', 'ngdp_fy_usd']]
rminusg['g'] = rminusg.groupby('ifscode')['ngdp'].pct_change()
rminusg['ggxwdg_l'] = rminusg.groupby('ifscode')['ggxwdg'].shift(1)
rminusg['r'] = np.where(rminusg['ggxwdg_l'] == 0, np.nan, rminusg['ggei'] / rminusg['ggxwdg_l'])
rminusg['rlessg'] = np.where((1 + rminusg['g']) == 0, np.nan,
                             (rminusg['r'] - rminusg['g']) / (1 + rminusg['g']) * 100)
rminusg['rlessg_abs'] = (rminusg['r'] - rminusg['g']) * 100

target_var = 'rlessg_abs'

agg = rminusg.agg_mean(target_var, group_dict=inc_dict).query('year>=2000')
ps = cpd.PutxlSet(excelfile)
ps.putxl(agg, sheet_name='chart', cell='B1', index=True)

rminusg.loc[rminusg['ifscode'].isin(dum.ae), 'inc_group'] = 'AE'
rminusg.loc[rminusg['ifscode'].isin(dum.em), 'inc_group'] = 'EM'
rminusg.loc[rminusg['ifscode'].isin(dum.lic), 'inc_group'] = 'LIDC'
rminusg_clean = rminusg.noagg[['ifscode', 'inc_group', 'year', 'ggei', 'ggxwdg', 'ngdp', 'g', 'rlessg_abs', 'rlessg']].query('year>=2000')
ps.putxl(rminusg_clean, sheet_name='data', cell='A1', index=False)

agg_detail = rminusg.query('year>=2000').export_agg_detail(
    indicator=target_var,
    group_dict=inc_dict,
    excel_file=excelfile,
    sheet_name='detail',
    start_cell='A2'
)
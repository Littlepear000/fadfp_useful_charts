from fadfpdata import EcosData, Dummy
import numpy as np
import pandaspro as cpd

update_date = '20251017'
excelfile = fr'R minus G/R minus G_{update_date}.xlsx'

ecos = EcosData()
dum = Dummy()
inc_dict = {
    'Global': dum.noagg,
    'Advanced Economies': dum.ae,
    'Emerging Markets': dum.em,
    'Low-Income Developing Countries': dum.lic
}

rminusg = ecos[['ifscode', 'year', 'ggei', 'ggxwdg', 'ngdp', 'ggxcnl_gdp', 'ngdp_fy_usd']]
rminusg['g'] = rminusg.groupby('ifscode')['ngdp'].pct_change()
rminusg['ggxwdg_l'] = rminusg.groupby('ifscode')['ggxwdg'].shift(1)
rminusg['r'] = np.where(rminusg['ggxwdg_l'] == 0, np.nan, rminusg['ggei'] / rminusg['ggxwdg_l'])
rminusg['rlessg'] = np.where((1 + rminusg['g']) == 0, np.nan,
                             (rminusg['r'] - rminusg['g']) / (1 + rminusg['g']) * 100)

agg = rminusg.agg_mean('rlessg', group_dict=inc_dict).query('year>=2000')
ps = cpd.PutxlSet(excelfile)
ps.putxl(agg, sheet_name='chart', cell='B1', index=True)

agg_detail = rminusg.export_agg_detail(
    indicator='rlessg',
    group_dict=inc_dict,
    excel_file=f'R minus G_{update_date}.xlsx',
    sheet_name='detail',
    start_cell='A2'
)
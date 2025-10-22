from fadfpdata import EcosData, Dummy, ifs_to_cname
import pandaspro as cpd

update_date = '20251020'
excelfile = fr'R minus G/R minus G_{update_date}.xlsx'

ecos = EcosData()
dum = Dummy()
inc_dict = {
    'Global': dum.noagg,
    'Advanced Economies': dum.ae,
    'Emerging Markets': dum.em,
    'Low-Income Developing Countries': dum.lic
}

rminusg = ecos[['ifscode', 'year', 'ggei', 'ggxwdg', 'ngdp_dpch', 'ngdp_fy_usd']]
rminusg['rlessg'] = rminusg['ggei'] / rminusg['ggxwdg'] * 100 - rminusg['ngdp_dpch']

agg = rminusg.agg_mean('rlessg', group_dict=inc_dict).query('year>=2000')
ps = cpd.PutxlSet(excelfile)
ps.putxl(agg, sheet_name='chart', cell='B1', index=True)

rminusg.loc[rminusg['ifscode'].isin(dum.ae), 'inc_group'] = 'AE'
rminusg.loc[rminusg['ifscode'].isin(dum.em), 'inc_group'] = 'EM'
rminusg.loc[rminusg['ifscode'].isin(dum.lic), 'inc_group'] = 'LIDC'
rminusg_clean = rminusg.noagg[['ifscode', 'inc_group', 'year', 'ggei', 'ggxwdg', 'ngdp_dpch', 'rlessg']].query('year>=2000')
ps.putxl(rminusg_clean, sheet_name='data', cell='A1', index=False)


agg_detail = rminusg.query('year>=2000').export_agg_detail(
    indicator='rlessg',
    group_dict=inc_dict,
    excel_file=excelfile,
    sheet_name='detail',
    start_cell='A2'
)


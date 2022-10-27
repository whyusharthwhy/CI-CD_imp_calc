import os
import re
import xlrd
import xlutils.copy
import glob

import pandas as pd
import numpy as np
import camelot

chrom_headers_shimadzu = ['Name','Ret. Time','Area']
area_headers_shimadzu = ['Name','Area']
chrom_headers_empower = ['Name','RT','Area']
area_headers_empower = ['SampleName', 'Area']

# Master sheets
df_rrf = pd.read_excel(os.path.join(os.getcwd(),'imp_calc', 'files', 'Templates', 'RRF-template.xlsx'))
df_sample_prep = pd.read_excel(os.path.join(os.getcwd(),'imp_calc', 'files', 'Templates', 'RS-sample-preparation.xlsx'))

def _getOutCell(outSheet, colIndex, rowIndex):
    """ HACK: Extract the internal xlwt cell representation. """
    row = outSheet._Worksheet__rows.get(rowIndex)
    if not row: return None

    cell = row._Row__cells.get(colIndex)
    return cell

def setOutCell(outSheet, col, row, value):
    """ Change cell value without changing formatting. """
    # HACK to retain cell style.
    previousCell = _getOutCell(outSheet, col, row)
    # END HACK, PART I

    outSheet.write(row, col, value)

    # HACK, PART II
    if previousCell:
        newCell = _getOutCell(outSheet, col, row)
        if newCell:
            newCell.xf_idx = previousCell.xf_idx

def shift_row_to_top(df, index_to_shift):
    """ Shifts the row with the compound to the the top"""
    idx = df.index.tolist()
    idx.remove(index_to_shift)
    df = df.reindex([index_to_shift] + idx)
    return df

def table_extratcor(tables, headers):
    """ Extracts tables from the PDFs using the camelot module"""
    df_result_table =''
    result_tables = []
    for table in tables:
        df_table = table.df
        search = df_table.where(df_table==headers[0]).dropna(how='all').dropna(axis=1)
        inx = list(search.index)
        if(inx):
            inx= inx[0]
            new_header = df_table.iloc[inx]
            new_start_inx = inx+1
            df_table = df_table[new_start_inx:]
            df_table.columns = new_header
            df_table = df_table[headers]
            result_tables.append(df_table)
        else:
            continue
    try:
        df_result_table = pd.concat(result_tables, ignore_index=True)
    except ValueError as ve:
        print("No tables/values found in this file\n")
        return pd.DataFrame()

    return df_result_table

def calc_results (df_peak, sample_input_list, inputs, compound, df_area_table, base_rt, unit):
    """ Calculates the impurity values following the impurity vs impurity method"""
    rrt_master = []
    impurity_master = []
    rrf_master = []
    ignore_compounds = []
    sample_wt, sample_v1, sample_v2, sample_v3, sample_v4, sample_v5, sample_v6, sample_v7, label_claim, unit, arr_no, b_no, condition = tuple(sample_input_list)

    for index, row in df_peak.iterrows():
        name =row[0]
        if(name.lower() == compound.lower()):
            impurity_master.append(0)
            rrt_master.append(1)
            rrf_master.append(0)
            continue
        if(name == np.nan or name == ''):
            continue
#             impurity_master.append(0)
#             rrt_master.append(0)

        area = float(row[2])
        try:
            average_area = round(df_area_table['Area'][df_area_table['Name'].str.contains(name, re.IGNORECASE)].mean())
        except:
            average_area = round(df_area_table['Area'][df_area_table['Name'].str.contains(compound, re.IGNORECASE)].mean())

        rt = float(row[1])
        rrf_cond_1 = df_rrf['Compound'].str.contains(compound, flags = re.IGNORECASE)
        rrf_cond_2 = df_rrf['Impurity/Active Name'].str.contains(name, flags = re.IGNORECASE)
        rrf = df_rrf['RRF'][rrf_cond_1 & rrf_cond_2].values.tolist()
        if(not(rrf)):
            impurity_master.append(0)
            rrt_res = round(rt/base_rt, ndigits=2)
            rrt_master.append(rrt_res)
            rrf_master.append(0)
            ignore_compounds.append(name)
            continue
        rrf = float(rrf[0])
        input_list =  inputs[name] if name.lower() != 'unknown' else inputs[compound]
        input_list[0:7] = [float(input_value) for input_value in input_list[0:7]]
        constant_1 = (input_list[0]/input_list[1]) * (input_list[2]/input_list[3]) * (input_list[4]/input_list[5])
        constant_2 = (sample_v1/sample_wt) * (sample_v3/sample_v2) * (sample_v5/sample_v4) * (sample_v7/sample_v6) * (input_list[6]/label_claim)
        impurity = round((area/average_area) * constant_1 * constant_2 * (unit/rrf), ndigits=2)
        rrt_res = round(rt/base_rt, ndigits=2)
        impurity_master.append(impurity)
        rrt_master.append(rrt_res)
        rrf_master.append(rrf)

    return impurity_master, rrt_master, rrf_master, ignore_compounds

def fill_ivi_sheet(output_sheet, df_area_table, df_peak_table, sample_input_list, inputs, compound, base_rt):
    table_col = 2
    keys = {
    'Ketorolac Tromethamine':['Related Compound-A','Related Compound-B','Related Compound-C','Related Compound-D','Ketorolac Tromethamine'],
    'Propofol': ['Related Compound-A','Related Compound-B', 'Propofol']
    }
    keys = keys[compound]
    #poject name
    setOutCell(output_sheet, 2, 3, compound)
    #Date
    setOutCell(output_sheet, 2, 4, inputs['Details'][1])
    #Method
    setOutCell(output_sheet, 2, 5, inputs['Details'][2])
    for key in keys:
        df_comp_areas = df_area_table[df_area_table['Name'].str.contains(key, flags= re.IGNORECASE)]
        average_area = round(df_comp_areas['Area'].mean())
        SD = round(df_comp_areas['Area'].std())
        RSD = round((SD/average_area)*100, ndigits=2)

        area_input = list(df_comp_areas['Area'])
        input_list = inputs[key]
        # WS ID No.
        setOutCell(output_sheet, table_col, 9, input_list[7])
        # std_wt
        setOutCell(output_sheet, table_col, 10, input_list[0])
        #  v1
        setOutCell(output_sheet, table_col, 11, input_list[1])
        # v2
        setOutCell(output_sheet, table_col, 12, input_list[2])
        #  v3
        setOutCell(output_sheet, table_col, 13, input_list[3])
        #  v4
        setOutCell(output_sheet, table_col, 14,  input_list[4])
        # v5
        setOutCell(output_sheet, table_col, 15, input_list[5])
        # potency
        setOutCell(output_sheet, table_col, 16, input_list[6])
        # areas
        setOutCell(output_sheet, table_col, 18, area_input[0])
        setOutCell(output_sheet, table_col, 19, area_input[1])
        setOutCell(output_sheet, table_col, 20, area_input[2])
        setOutCell(output_sheet, table_col, 21, area_input[3])
        setOutCell(output_sheet, table_col, 22, area_input[4])
        setOutCell(output_sheet, table_col, 23, area_input[5])
        setOutCell(output_sheet, table_col, 24, average_area)
        setOutCell(output_sheet, table_col, 25, SD)
        setOutCell(output_sheet, table_col, 26, RSD)

        table_col +=1

    # AR NO
    setOutCell(output_sheet, 1, 30, sample_input_list[10])
    # Batch NO
    setOutCell(output_sheet, 3, 30, sample_input_list[11])
    # Condition
    setOutCell(output_sheet, 4, 30, sample_input_list[12])
    # Label Claim
    setOutCell(output_sheet, 5, 30, sample_input_list[8])
    # sample_wt
    setOutCell(output_sheet, 2, 31, sample_input_list[0])
    #  v1
    setOutCell(output_sheet, 2, 32, sample_input_list[1])
    # v2
    setOutCell(output_sheet, 4, 31, sample_input_list[2])
    #  v3
    setOutCell(output_sheet, 4, 32, sample_input_list[3])
    #  v4
    setOutCell(output_sheet, 6, 31, sample_input_list[4])
    # v5
    setOutCell(output_sheet, 6, 32, sample_input_list[5])
    if(compound == 'Ketorolac Tromethamine'):
        # per unit
        setOutCell(output_sheet, 7, 30, sample_input_list[9])
        # v6
        setOutCell(output_sheet, 8, 31, sample_input_list[6])
        # v7
        setOutCell(output_sheet, 8, 32, sample_input_list[7])
    if(compound == 'Propofol'):
        # RT
        setOutCell(output_sheet, 2, 34, base_rt)
#   Impurity table
    table_row = 37
    table_limit = 76 if compound == 'Ketorolac Tromethamine' else 54
    for index, row in df_peak_table.iterrows():
        if(table_row > table_limit):
            break
        setOutCell(output_sheet, 1, table_row, row[0])
        setOutCell(output_sheet, 2, table_row, row[1])
        setOutCell(output_sheet, 3, table_row, row[2])
        setOutCell(output_sheet, 4, table_row, row[3])
        setOutCell(output_sheet, 5, table_row, row[4])
        setOutCell(output_sheet, 6, table_row, row[5])
        table_row +=1

    sum_of_impurities = str(round(df_peak_table["% w/w"].sum(), ndigits=2))
    setOutCell(output_sheet, 6, table_limit+1, sum_of_impurities)

def initiate_report_creation(chrom_inputs, area_inputs, inputs):
    compound = inputs['Details'][-1]
    software = inputs['Details'][0]
    sample_wt = df_sample_prep['Sample Volume'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v1 = df_sample_prep['v1'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v2 = df_sample_prep['v2'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v3 = df_sample_prep['v3'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v4 = df_sample_prep['v4'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v5 = df_sample_prep['v5'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v6 = df_sample_prep['v6'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    sample_v7 = df_sample_prep['v7'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    label_claim = df_sample_prep['label claim'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    unit = df_sample_prep['per unit'][df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0]
    ivi_template_input = xlrd.open_workbook(os.path.join(os.getcwd(), 'files', 'Templates','{}-template.xls'.format(compound)), formatting_info=True)
    ivi_template = xlutils.copy.copy(ivi_template_input)
    # area tables extraction
    area_tables =  []
    area_headers = area_headers_shimadzu if software == 'Lab Solutions' else area_headers_empower
    for area_input in area_inputs:
        tables = camelot.read_pdf(area_input, pages= 'all', line_scale = 30)
        df_area = table_extratcor(tables, area_headers)
        df_area.columns = area_headers_shimadzu
        df_area = df_area[['Name','Area']]
        area_tables.append(df_area)
    df_area_table = pd.concat(area_tables)
    df_area_table = df_area_table.drop(df_area_table[df_area_table['Name'] == ''].index)
    df_area_table["Area"] = df_area_table["Area"].astype(float)
    batch_size = len(chrom_inputs)
    outputs = []
    worksheets = ivi_template._Workbook__worksheets
    chrom_headers = chrom_headers_shimadzu if software == 'Lab Solutions' else chrom_headers_empower
    for index, chrom_input in enumerate(chrom_inputs):
        # worksheet_name = chrom_input.split("\\")[-1].strip(".pdf")
        worksheet_name =  re.split(r'/|\\', chrom_input)[-1].strip(".pdf")
        print(worksheet_name)
        # peak tables extratcion
        tables = camelot.read_pdf(chrom_input, pages= 'all', line_scale =30)
        df_peak_table = table_extratcor(tables, chrom_headers)
        if (df_peak_table.empty):
            continue
        df_peak_table = df_peak_table.drop_duplicates(keep="first")
        df_peak_table.columns = chrom_headers_shimadzu
        try:
            base_rt = float(df_peak_table['Ret. Time'][df_peak_table['Name'].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0])
        except IndexError as ie:
            print("\"{}\" might not be present in the tables of the file {}.Please check this file".format(compound,worksheet_name))
            continue
        cond_1 = df_peak_table["Name"] == ''
        cond_2 = df_peak_table["Name"] == np.nan
        cond_3 = df_peak_table["Name"].str.contains(compound, flags = re.IGNORECASE)

        inxs_to_remove = df_peak_table[cond_1 | cond_2 | cond_3].index
        df_peak_table = df_peak_table.drop(inxs_to_remove)
        try:
            arr_no = worksheet_name.split("-")[0]
            condition = worksheet_name.split("-")[-1]
            inx_1 = worksheet_name.index(arr_no) + len(arr_no)
            inx_2 = worksheet_name.index(condition)
            b_no = worksheet_name[inx_1:inx_2].strip("-")
        except IndexError as ie:
            arr_no = worksheet_name
            b_no = ''
            condition = ''
        sample_input_list = [sample_wt, sample_v1, sample_v2, sample_v3, sample_v4, sample_v5, sample_v6, sample_v7, label_claim, unit, arr_no, b_no, condition ]

        # impurity calculation
        impurities, rrts, rrfs, ignore_compounds = calc_results(df_peak_table, sample_input_list, inputs, compound, df_area_table, base_rt, unit)
        df_peak_table['RRT'] = rrts
        df_peak_table['RRF'] = rrfs
        df_peak_table["% w/w"] = impurities
        for ic in ignore_compounds:
            inx_to_remove = df_peak_table[df_peak_table['Name'] == ic].index
            df_peak_table = df_peak_table.drop(inx_to_remove)
        df_peak_table = df_peak_table[['Name', 'Ret. Time','RRT', 'RRF', 'Area', '% w/w']]

        # writing to output sheet
        ivi_template_sheet = ivi_template.get_sheet(index)
        ivi_template_sheet.protect = True
        ivi_template_sheet.password = "Welcomeanthea*08"
        if(compound == 'Ketorolac Tromethamine'):
            fill_ivi_sheet(ivi_template_sheet, df_area_table, df_peak_table, sample_input_list, inputs, compound, base_rt)
        elif(compound == 'Propofol'):
            fill_ivi_sheet(ivi_template_sheet, df_area_table, df_peak_table, sample_input_list, inputs, compound, base_rt)
        if(b_no != '' and condition != ''):
            worksheets[index].name = b_no +"_" + condition
        else:
            worksheets[index].name = worksheet_name

    ivi_template._Workbook__worksheets = [worksheet for worksheet in ivi_template._Workbook__worksheets if "Sheet" not in worksheet.name ]
    ivi_template.active_sheet = 0
    return ivi_template

import os
import re
import xlrd
import xlutils.copy
import glob

import pandas as pd
import numpy as np
import camelot

# RS template sheet
# rs_template_input = xlrd.open_workbook(os.path.join(os.getcwd(), "files", "Templates",'RS-template.xls'), formatting_info=True)
# rs_template = xlutils.copy.copy(rs_template_input)
# imp_b_rs_template = xlutils.copy.copy(rs_template_input)

# Master sheets
df_rrf = pd.read_excel(os.path.join(os.getcwd(),'imp_calc', 'files', 'Templates', 'RRF-template.xlsx'))
df_sample_prep = pd.read_excel(os.path.join(os.getcwd(),'imp_calc', 'files', 'Templates', 'RS-sample-preparation.xlsx'))
# Chromatogram headers
chrom_headers_shimadzu = ['Name','Ret. Time','Area']
area_headers_shimadzu = ['Title','Area']
chrom_headers_empower = ['Name','RT','Area']
area_headers_empower = ['SampleName', 'Area']

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
    df_result_table = None
    result_tables = []

    # Picking the impurity tables/ area tables from all the tables found in the PDF
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
            try:
                df_table = df_table[headers]
                result_tables.append(df_table)
            except KeyError as ke:
                print("Please check this file\n")
                flash("Please check this file")
                return pd.DataFrame([], columns =headers)
        else:
            continue
    try:
        df_result_table = pd.concat(result_tables, ignore_index=True)
    except ValueError as ve:
        print("No tables/values found in this file\n")
        flash("No tables/values found in this file\n")
        return pd.DataFrame()

    return df_result_table

def calc_results (df_peak, df_rrf, compound, average_area, constant_1, constant_2, unit):
    """ Calculates the impurity values following the RS method"""

    base_rt = float(df_peak['Ret. Time'][df_peak['Name'].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0])

    # columns to be filled in the output excel
    rrt_master = []
    impurity_master = []
    rrf_master = []
    ignore_compounds = []

    # Impurity calculation
    for index, row in df_peak.iterrows():
        name =row[0]
        if(re.match('unknown[-]*|unkown[-]*', name.lower())):
            name = 'Unknown'
        if(name.lower() == compound.lower()):
            impurity_master.append(0)
            rrt_master.append(1)
            rrf_master.append(0)
            continue
        if(name == np.nan or name == ''):
            continue
        try:
            area = float(row[2])
        except ValueError as ve:
            impurity_master.append(0)
            rrt_master.append(1)
            rrf_master.append(0)
            continue
        rrf_cond_1 = df_rrf['Compound'].str.contains(compound, flags = re.IGNORECASE)
        rrf_cond_2 = df_rrf['Impurity/Active Name'].str.contains(name, flags = re.IGNORECASE)
        rrf = df_rrf['RRF'][rrf_cond_1 & rrf_cond_2].values.tolist()
        rt = float(row[1])

        if(not(rrf)):
            ignore_compounds.append(name)
            continue

        rrf = float(rrf[0])
        impurity = round((area/average_area) * constant_1 * constant_2 * (unit/rrf), ndigits=2)
        rrt_res = round(rt/base_rt, ndigits=2)
        impurity_master.append(impurity)
        rrt_master.append(rrt_res)
        rrf_master.append(rrf)

    return impurity_master, rrt_master, rrf_master, ignore_compounds

def fill_rs_sheet(output_sheet, df_area_table, df_peak_table, sample_input_list, input_list):
    average_area = float(df_area_table["Area"][df_area_table["Title"] == "Average"].values.tolist()[0])
    area_input = list(df_area_table['Area'])
    project_name = 'Acyloivr'
    if(len(area_input) != 9):
        area_input.insert(3, '')
        area_input.insert(4, '')
        area_input.insert(5, '')
        project_name = 'Impurity-B (Acyloivr)'

    #poject name
    setOutCell(output_sheet, 2, 3, project_name)
    #Date
    setOutCell(output_sheet, 2, 4, input_list[11])
    #Method
    setOutCell(output_sheet, 2, 5, input_list[12])
    # WS ID No.
    setOutCell(output_sheet, 1, 9, input_list[13])
    # potency
    setOutCell(output_sheet, 3, 9, input_list[10])
    # use before date
    setOutCell(output_sheet, 5, 9, input_list[14])
    # Average area
    setOutCell(output_sheet, 7, 9, average_area)
    # std_wt
    setOutCell(output_sheet, 2, 10, input_list[0])
    #  v1
    setOutCell(output_sheet, 2, 11, input_list[1])
    # v2
    setOutCell(output_sheet, 4, 10, input_list[2])
    #  v3
    setOutCell(output_sheet, 4, 11, input_list[3])
    #  v4
    setOutCell(output_sheet, 6, 10,  input_list[4])
    # v5
    setOutCell(output_sheet, 6, 11, input_list[5])
    # v6
    setOutCell(output_sheet, 8, 10, input_list[6])
    # v7
    setOutCell(output_sheet, 8, 11, input_list[7])
    # factor
    setOutCell(output_sheet, 9, 10, input_list[8])
    # factor
    setOutCell(output_sheet, 9, 11, input_list[9])
    # AR NO
    setOutCell(output_sheet, 1, 14, sample_input_list[10])
    # Batch NO
    setOutCell(output_sheet, 3, 14, sample_input_list[11])
    # Condition
    setOutCell(output_sheet, 4, 14, sample_input_list[12])
    # Label Claim
    setOutCell(output_sheet, 5, 14, sample_input_list[8])
    # per unit
    setOutCell(output_sheet, 7, 14, sample_input_list[9])
    # sample_wt
    setOutCell(output_sheet, 2, 15, sample_input_list[0])
    #  v1
    setOutCell(output_sheet, 2, 16, sample_input_list[1])
    # v2
    setOutCell(output_sheet, 4, 15, sample_input_list[2])
    #  v3
    setOutCell(output_sheet, 4, 16, sample_input_list[3])
    #  v4
    setOutCell(output_sheet, 6, 15, sample_input_list[4])
    # v5
    setOutCell(output_sheet, 6, 16, sample_input_list[5])
    # v6
    setOutCell(output_sheet, 8, 15, sample_input_list[6])
    # v7
    setOutCell(output_sheet, 8, 16, sample_input_list[7])
#     areas
    setOutCell(output_sheet, 12, 5, area_input[0])
    setOutCell(output_sheet, 12, 6, area_input[1])
    setOutCell(output_sheet, 12, 7, area_input[2])
    setOutCell(output_sheet, 12, 8, area_input[3])
    setOutCell(output_sheet, 12, 9, area_input[4])
    setOutCell(output_sheet, 12, 10, area_input[5])
    setOutCell(output_sheet, 12, 11, area_input[6])
    setOutCell(output_sheet, 12, 12, area_input[7])
    setOutCell(output_sheet, 12, 13, area_input[8])
#   Impurity table
    table_row = 20
    for index, row in df_peak_table.iterrows():
        if(table_row > 60):
            break
        setOutCell(output_sheet, 1, table_row, row[0])
        setOutCell(output_sheet, 2, table_row, row[1])
        setOutCell(output_sheet, 3, table_row, row[2])
        setOutCell(output_sheet, 4, table_row, row[3])
        setOutCell(output_sheet, 5, table_row, row[4])
        setOutCell(output_sheet, 6, table_row, row[5])
        table_row +=1

    # final sum
    sum_of_impurities = str(round(df_peak_table["% w/w"].sum(), ndigits=2))
    setOutCell(output_sheet, 6, 61, sum_of_impurities)

def initiate_report_creation(chrom_inputs, area_input, area_input_imp_b, input_list):

    """ Begins the report creation process following the defined business logics"""
    rs_template_input = xlrd.open_workbook(os.path.join(os.getcwd(), "imp_calc","files", "Templates",'RS-template.xls'), formatting_info=True)
    rs_template = xlutils.copy.copy(rs_template_input)
    imp_b_rs_template = xlutils.copy.copy(rs_template_input)
    software = input_list[0]
    compound = input_list[1]
    strength = input_list[2]
    input_list_imp_b = input_list[20:]
    input_list = input_list[3:18]
    cond_1 = df_sample_prep["Compound"].str.contains(compound, flags = re.IGNORECASE)
    cond_2 = df_sample_prep["Strength"] == strength
    sample_wt = df_sample_prep['Sample Volume'][cond_1 & cond_2].values.tolist()[0]
    sample_v1 = df_sample_prep['v1'][cond_1 & cond_2].values.tolist()[0]
    sample_v2 = df_sample_prep['v2'][cond_1 & cond_2].values.tolist()[0]
    sample_v3 = df_sample_prep['v3'][cond_1 & cond_2].values.tolist()[0]
    sample_v4 = df_sample_prep['v4'][cond_1 & cond_2].values.tolist()[0]
    sample_v5 = df_sample_prep['v5'][cond_1 & cond_2].values.tolist()[0]
    sample_v6 = df_sample_prep['v6'][cond_1 & cond_2].values.tolist()[0]
    sample_v7 = df_sample_prep['v7'][cond_1 & cond_2].values.tolist()[0]
    label_claim = df_sample_prep['label claim'][cond_1 & cond_2].values.tolist()[0]
    unit = df_sample_prep['per unit'][cond_1 & cond_2].values.tolist()[0]

    constant_1 = (input_list[0]/input_list[1]) * (input_list[2]/input_list[3]) * (input_list[4]/input_list[5])*(input_list[6]/input_list[7]) * (input_list[8]/input_list[9])
    constant_2 = (sample_v1/sample_wt) * (sample_v3/sample_v2) * (sample_v5/sample_v4) * (sample_v7/sample_v6) * (input_list[10]/label_claim)
    constant_3 = (input_list_imp_b[0]/input_list_imp_b[1]) * (input_list_imp_b[2]/input_list_imp_b[3]) * (input_list_imp_b[4]/input_list_imp_b[5])*(input_list_imp_b[6]/input_list_imp_b[7]) * (input_list_imp_b[8]/input_list_imp_b[9])

    # area table extraction for acyclovir
    tables = camelot.read_pdf(area_input, pages= 'all', line_scale =30)
    area_headers = area_headers_shimadzu if software == 'Lab Solutions' else area_headers_empower
    df_area_table = table_extratcor(tables, area_headers)
    df_area_table.columns = area_headers_shimadzu
    df_area_table = df_area_table[['Title','Area']]
    sols_count = df_area_table.shape[0] - 3
    areas = list(df_area_table["Area"])
    if(sols_count < 6):
        while(sols_count<6):
            areas.insert(sols_count, 0)
            sols_count+=1
    titles = ['Standard Solution_01','Standard Solution_02','Standard Solution_03','Standard Solution_04','Standard Solution_05','Standard Solution_06','Average', '%RSD','Standard Deviation']
    if(software == 'Empower'):
        areas[7], areas[8] = areas[8], areas[7]
    df_area_table = pd.DataFrame({'Title':titles, 'Area': areas })
    average_area = float(df_area_table["Area"][df_area_table["Title"] == "Average"].values.tolist()[0])

    # area table extraction for impurity b
    tables = camelot.read_pdf(area_input_imp_b, pages= 'all', line_scale =30)
    df_area_table_imp_b = table_extratcor(tables, area_headers)
    df_area_table_imp_b.columns = area_headers_shimadzu
    df_area_table_imp_b = df_area_table_imp_b[['Title','Area']]
    sols_count = df_area_table_imp_b.shape[0] - 3
    areas = list(df_area_table_imp_b["Area"])
    if(sols_count < 6):
        while(sols_count<6):
            areas.insert(sols_count, 0)
            sols_count+=1
    titles = ['Standard Solution_01','Standard Solution_02','Standard Solution_03','Standard Solution_04','Standard Solution_05','Standard Solution_06','Average', '%RSD','Standard Deviation']
    if(software == 'Empower'):
        areas[7], areas[8] = areas[8], areas[7]
    df_area_table_imp_b = pd.DataFrame({'Title':titles, 'Area': areas })
    average_area_imp_b = float(df_area_table_imp_b["Area"][df_area_table_imp_b["Title"] == "Average"].values.tolist()[0])

    batch_size = len(chrom_inputs)
    outputs = []
    chrom_headers = chrom_headers_shimadzu if software == 'Lab Solutions' else chrom_headers_empower
    worksheets_acyclovir = rs_template._Workbook__worksheets
    worksheets_imp_b = imp_b_rs_template._Workbook__worksheets
    for index, chrom_input in enumerate(chrom_inputs):
        # worksheet_name =  chrom_input.split("\\")[-1].strip(".pdf")
        worksheet_name =  re.split(r'/|\\', chrom_input)[-1].strip(".pdf")
        print(worksheet_name)
        # peak tables extratcion
        tables = camelot.read_pdf(chrom_input, pages= 'all', line_scale =30)
        df_peak_table = table_extratcor(tables, chrom_headers)
        if (df_peak_table.empty):
            continue
        df_peak_table.columns = chrom_headers_shimadzu
        df_peak_table = df_peak_table.drop_duplicates(keep="first")
        try:
            inx_to_shift = df_peak_table[df_peak_table["Name"].str.contains(compound, flags = re.IGNORECASE)].index[0]
        except IndexError as ie:
            print("\"{}\" might not be present in the tables of the file {}.Please check this file".format(compound,worksheet_name))
            flash("\"{}\" might not be present in the tables of the file {}.Please check this file".format(compound,worksheet_name))
            
            continue
        df_peak_table = shift_row_to_top(df_peak_table, inx_to_shift)
        cond_1 = df_peak_table["Name"] == ''
        cond_2 = df_peak_table["Name"] == np.nan
        inxs_to_remove = df_peak_table[cond_1 | cond_2].index
        df_peak_table = df_peak_table.drop(inxs_to_remove)

        # impurity calculation for acyclovir
        impurities, rrts, rrfs, ignore_compounds = calc_results(df_peak_table, df_rrf, compound, average_area, constant_1, constant_2, unit)
        for ic in ignore_compounds:
            inx_to_remove = df_peak_table[df_peak_table['Name'] == ic].index
            df_peak_table = df_peak_table.drop(inx_to_remove)
        df_peak_table['RRT'] = rrts
        df_peak_table['RRF'] = rrfs
        df_peak_table['% w/w'] = impurities
        df_peak_table = df_peak_table[['Name', 'Ret. Time','RRT', 'RRF', 'Area', '% w/w']]
        df_impurity_b = df_peak_table[df_peak_table['Name'].str.contains('Impurity-B', flags= re.IGNORECASE)]
        df_peak_table = df_peak_table.drop( df_peak_table[df_peak_table['Name'].str.contains('Impurity-B', flags= re.IGNORECASE)].index)

        # impurity calculation for impurity B
        df_impurity_b['RRF'] = [1]
        imp_b_area = float(df_impurity_b['Area'][df_impurity_b['Name'].str.contains('Impurity-B', flags= re.IGNORECASE)].values.tolist()[0])
        impurity = round((imp_b_area/average_area_imp_b) * constant_3 * constant_2 * (unit/1), ndigits=2)
        df_impurity_b['% w/w'] = [impurity]

        # writing to output sheet acyclovir
        rs_template_sheet = rs_template.get_sheet(index)
        rs_template_sheet.protect = True
        rs_template_sheet.password = "Welcomeanthea*08"
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
        sample_input_list = [sample_wt, sample_v1, sample_v2, sample_v3, sample_v4, sample_v5, sample_v6, sample_v7, label_claim, unit, arr_no,b_no,condition]
        fill_rs_sheet(rs_template_sheet, df_area_table, df_peak_table, sample_input_list, input_list)
        worksheets_acyclovir[index].name = worksheet_name

        # writing to output sheet impurity B
        imp_b_sheet = imp_b_rs_template.get_sheet(index)
        imp_b_sheet.protect = True
        imp_b_sheet.password = "Welcomeanthea*08"
        fill_rs_sheet(imp_b_sheet, df_area_table_imp_b, df_impurity_b, sample_input_list, input_list_imp_b)
        if(b_no != '' and condition != ''):
            worksheets_imp_b[index].name = b_no +"_" + condition
        else:
            worksheets_imp_b[index].name = worksheet_name

    rs_template._Workbook__worksheets = [worksheet for worksheet in rs_template._Workbook__worksheets if "Sheet" not in worksheet.name ]
    rs_template.active_sheet = 0
    imp_b_rs_template._Workbook__worksheets = [worksheet for worksheet in imp_b_rs_template._Workbook__worksheets if "Sheet" not in worksheet.name ]
    imp_b_rs_template.active_sheet = 0
    return rs_template,imp_b_rs_template

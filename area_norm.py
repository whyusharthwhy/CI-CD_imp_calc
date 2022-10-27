import os
import re
import xlrd
import xlutils.copy
import glob

import pandas as pd
import numpy as np
import camelot

# Area norm template sheet


# Chromatogram headers
chrom_headers_shimadzu = ['Name','Ret. Time','Area']
chrom_headers_empower = ['Name','RT','Area']

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

def calc_results (df_peak, compound, main_peak, factor, base_rt):
    """ Calculates the impurity values following the RS method"""
    rrt_master = []
    area_percent__master = []
    sum_of_areas = round(df_peak["Area"].sum(), ndigits=2)
    constant_1 = (factor * main_peak) + sum_of_areas
    sum =0
    for index, row in df_peak.iterrows():
        rt = float(row[1])
        area = row[2]
        area_res = (area/constant_1)*100
        sum+=area_res
        rrt_res = round(rt/base_rt, ndigits=2)
        rrt_master.append(rrt_res)
        area_percent__master.append(round(area_res, ndigits=2))

    return  rrt_master, area_percent__master, round(sum, ndigits=2)

def check_transpose(df_table, headers):
    """ To check if the transposed form of the table has the desired values"""
    df_table_t = df_table.T
    search = df_table_t.where(df_table_t==headers[1]).dropna(how='all').dropna(axis=1)
    inx = list(search.index)
    if(inx):
        inx= inx[0]
        new_header = df_table_t.iloc[inx]
        if('Ret. Time' and 'Area' in list(new_header)):
            if(inx == df_table_t.shape[0]-1):
                return df_table.T.reindex(index=df_table_t.index[::-1]).reset_index()
            else:
                return df_table.T
        else:
            return df_table
    else:
        return df_table

def table_extratcor(tables, headers):
    df_result_table = ''
    result_tables = []
    for table in tables:
        df_table = table.df
        df_table = check_transpose(df_table, headers)
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
                return pd.DataFrame([], columns =headers)
        else:
            continue
    try:
        df_result_table = pd.concat(result_tables, ignore_index=True)
    except ValueError as ve:
        print("No tables/values found in this file\n")
        return pd.DataFrame()
    return df_result_table

def fill_rs_sheet(output_sheet, df_peak_table, user_input_list, ap_sum):
    # ARR no
    setOutCell(output_sheet, 1, 0, user_input_list[6])
    # B.No
    setOutCell(output_sheet, 3, 0, user_input_list[7])
    # # Condition
    # setOutCell(output_sheet, 3, 0, user_input_list[8])
    # main peak area
    setOutCell(output_sheet, 3, 2, user_input_list[0])
    # Base RT
    setOutCell(output_sheet, 5, 2, user_input_list[5])
    # Factor
    setOutCell(output_sheet, 4, 2, user_input_list[4])
    # Date of Analysis
    setOutCell(output_sheet, 5, 0, user_input_list[3])
#   RRT table
    table_row = 5
    for index, row in df_peak_table.iterrows():
        if(table_row > 62):
            break
        setOutCell(output_sheet, 0, table_row, row[0])
        setOutCell(output_sheet, 1, table_row, row[1])
        setOutCell(output_sheet, 2, table_row, row[2])
        setOutCell(output_sheet, 3, table_row, row[3])
        setOutCell(output_sheet, 4, table_row, row[4])
        table_row +=1

    sum_of_areas = round(df_peak_table["Area"].sum(), ndigits=2)
    sum_of_percentage = df_peak_table["Area%"].sum()
    sum_of_rrt = round(((user_input_list[4]*user_input_list[0]) / ((user_input_list[4] * user_input_list[0])+sum_of_areas))*100, ndigits=1)

    setOutCell(output_sheet, 1, table_row, "SUM")
    setOutCell(output_sheet, 2, table_row, sum_of_areas)
    setOutCell(output_sheet, 3, table_row, ap_sum)
    setOutCell(output_sheet, 4, table_row  , sum_of_rrt)

    table_row += 1
    compound_percentage = ((user_input_list[0] * user_input_list[4])/((user_input_list[0] * user_input_list[4])+sum_of_areas))*100
    compound_percentage = round(compound_percentage, ndigits=2 )
    setOutCell(output_sheet, 1, table_row, "Vancomycin-B (%)")
    setOutCell(output_sheet, 2, table_row, compound_percentage)

def initiate_report_creation(chrom_inputs, input_list):
    """ Begins the report creation process following the defined business logics"""
    area_norm_template_input = xlrd.open_workbook(os.path.join(os.getcwd(),'imp_calc', "files", "Templates",'area-norm-template.xls'), formatting_info=True)
    area_norm_template = xlutils.copy.copy(area_norm_template_input)
    software = input_list[0]
    compound = input_list[1]
    dil_s01 = input_list[2]
    dil_s02 = input_list[3]
    factor = dil_s01/dil_s02
    mp_list = input_list[5:]
    batch_size = len(chrom_inputs)
    worksheets = area_norm_template._Workbook__worksheets
    chrom_headers = chrom_headers_shimadzu if software == 'Lab Solutions' else chrom_headers_empower
    for index, chrom_input in enumerate(chrom_inputs):
        # worksheet_name = chrom_input.split("\\")[-1].strip(".pdf")
        worksheet_name =  re.split(r'/|\\', chrom_input)[-1].strip(".pdf")
        main_peak = mp_list[index]
        print(worksheet_name)
        # peak tables extratcion
        tables = camelot.read_pdf(chrom_input, pages= 'all', line_scale = 30)
        df_peak_table = table_extratcor(tables, chrom_headers)
        if(df_peak_table.empty):
            continue
        df_peak_table = df_peak_table.drop_duplicates(keep="first")
        df_peak_table.columns = chrom_headers_shimadzu
        try:
            base_rt = float(df_peak_table['Ret. Time'][df_peak_table["Name"].str.contains(compound, flags = re.IGNORECASE)].values.tolist()[0])
        except IndexError as ie:
            print("\"{}\" might not be present in the tables of the file {}. Please check this file".format(compound,worksheet_name))
            continue

        compound_row = df_peak_table[df_peak_table["Name"].str.contains(compound, flags = re.IGNORECASE)].index
        df_peak_table = df_peak_table.drop(compound_row)
        cond_1 = df_peak_table["Name"] == ''
        cond_2 = df_peak_table["Name"] == np.nan
        inxs_to_remove = df_peak_table[cond_1 | cond_2].index
        df_peak_table = df_peak_table.drop(inxs_to_remove)
        df_peak_table["Area"] = [float(area) for area in df_peak_table["Area"]]
        # df_peak_table["Area%"] = [float(area) for area in df_peak_table["Area%"]]

        # RRT calculation
        rrts,area_percents,ap_sum = calc_results(df_peak_table, compound, main_peak, factor, base_rt)
        df_peak_table['RRT'] = rrts
        df_peak_table["Area%"] = area_percents
        df_peak_table = df_peak_table[['Ret. Time','Name','Area', 'Area%', 'RRT']]

        # writing to output sheet
        area_norm_sheet = area_norm_template.get_sheet(index)
        area_norm_sheet.protect = True
        area_norm_sheet.password = "Welcomeanthea*08"
        try:
            arr_no = worksheet_name.split("-")[0]
            b_no_condition = worksheet_name[len(arr_no):].strip('-')
        except IndexError as ie:
            arr_no = worksheet_name
            b_no_condition = ''
        user_input_list = [main_peak] + input_list[2:5] + [factor,base_rt,arr_no,b_no_condition]
        fill_rs_sheet(area_norm_sheet, df_peak_table, user_input_list, ap_sum)
        if(b_no_condition != ''):
            worksheets[index].name = b_no_condition
        else:
            worksheets[index].name = worksheet_name

    area_norm_template._Workbook__worksheets = [worksheet for worksheet in area_norm_template._Workbook__worksheets if "Sheet" not in worksheet.name ]
    area_norm_template.active_sheet = 0

    return area_norm_template

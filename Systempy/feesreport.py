from failtools import file_download, get_df_index
import pandas as pd
from builder_classes import SplitBuild, ClientFee, FeeBuild
from feestools import *
import time
import os.path
from os import remove
from openpyxl import Workbook
import csv

start_time = time.time()

def feesreportgen():
# ----------------------------------------------- Download all sales and report from Split Endpoint ------------------ #

    #Check if download has been made to create datafrane
    try:
        #Create dataframe from Splits Report
        my_file = '../Files/Queries/report.csv'
        if os.path.exists(my_file) == True:
            print('Split Report already downloaded')
            print('     10% Finished', '\n')
        else:
            raise Exception

    except:
        #Downloading Split Report generated from query treatment
        print('Downloading Split Report', '\n')
        my_file = '../Files/Queries/report.csv'
        split_url = 'https://banking-report-gps.stone.com.br:3443/report.csv'
        file_download(split_url, my_file)                # -> Debug: Deactivated for now download is finished
    
        #Create dataframe from Splits Report
        print('     10% Finished', '\n')

    print('Loading Fee History', '\n')
    #Create aux df with fees
    aux1 = pd.read_csv('../Business-Rules/Fee2-DB.csv', delimiter=';', encoding='cp1252')
    #Set the index as Sup. Stonecode column
    fee_hist = aux1.set_index(['Stonecode Fornecedor'], drop=False)
    #Format date to datetime object
    fee_hist['Update'] = pd.to_datetime(fee_hist['Update'])
    #Group by Suplier stonecode column        
    fee_group = fee_hist.groupby(fee_hist.columns[0])
    print('     15% Finished', '\n')

    # ----------------- Firts parallelization ---------------------------------

    #Create aux df with fees
    aux = pd.read_csv('../Business-Rules/FeeRule-DB.csv', delimiter=';', encoding='cp1252')
    #Set the index as Merchant ID column to iterate on it
    bool_fee = aux.set_index(['Stonecode Fornecedor'], drop=False)

    #Remove unnecessary columns
    auxdf = pd.read_csv(my_file, delimiter=';')
    auxdf.drop(auxdf.columns[[4,5,6,7,8,9,10,11,13,17,18,19,]], axis=1, inplace=True)
    auxdf.to_csv(my_file, index=False)

    chunksize1 = 50000
    chunks = []
    j=1

    for report in pd.read_csv(my_file, chunksize=chunksize1):

        #Convert date of split do datetime object
        report['Data da Venda'] = pd.to_datetime(report['Data da Venda'])
        #Convert date of split do datetime object
        report[report.columns[7]] = pd.to_datetime(report[report.columns[7]])
        #Print report dtype
        #print(report.dtypes)

        #Create a dictionary with all fees mapped
        rules_dict = frulesdict(bool_fee)

        #Create series for each used column to append in the right
        # of the report after the fees calculation
        supsc = report[report.columns[1]]
        splitdate = report[report.columns[0]]
    
        merge = [supsc, splitdate]
        datensc = pd.concat(merge, axis=1)

        suplier = supsc.apply(maprules, args=(rules_dict,'suplier'))
        ecgroup = supsc.apply(maprules, args=(rules_dict,'ecgroup'))
        supgroup = supsc.apply(maprules, args=(rules_dict,'supgroup'))
        nature = supsc.apply(maprules, args=(rules_dict,'nature'))
        whopay = supsc.apply(maprules, args=(rules_dict,'whopay'))
        updates = supsc.apply(maprules, args=(rules_dict,'updates'))   

        frames = [report,supgroup,ecgroup,nature,whopay,updates]

        report = pd.concat(frames, axis=1)

        chunks.append(report)
        print(' ---------- Processing large dataset', j, '\n')
        j+=1

    print('     40% Finished', '\n')
    print('Loading auxiliary tools', '\n')
    report = pd.concat(chunks,axis=0)

    report.columns.values[2] = 'Fornecedor'
    report.columns.values[9] = 'Grupo Fornecedor'
    report.columns.values[10] = 'Grupo - EC'
    report.columns.values[11] = 'Natureza da Op.'
    report.columns.values[12] = 'Quem paga a Fee'
    report.columns.values[13] = 'Updates'

    #Create lite dictionary with only fees
    fee_hists = fee_hist.drop_duplicates(subset=['Stonecode Fornecedor'])
    fdictsimple = feesdict(fee_hists)

    #Groupby report where updates > 1 and apply mapfees only where updates > 1, if updates = 0 just use a dictionary
    #print(report.dtypes)     
    try:
        report_group = report.groupby(report.columns[13])
    except:
        pass

    # ----------------- Second parallelization ----------------------------------------------------------------------

                # ------------------ Layer report 1 : Dataset without updates -------------------

    #Create subset file to iterate over
    try:
        report1 = report_group.get_group(0)
    except:
        report1 = report.copy()

    #Create auxiliary column with Suplier stonecodes
    supsc1 = report1[report1.columns[1]]
    #Create fees column using dicitonary for clients without updates
    fees1 = supsc1.apply(mapfees1, args=(fdictsimple,))   
    #Create list with dfs to concat after
    frames1 = [report1,fees1]
    #Concat dataframes
    report1 = pd.concat(frames1, axis=1)
    #Rename column
    report1.columns.values[14] = 'F'
    #Remove column
    report1.drop(report1.columns[13], axis=1, inplace=True)
    #Save file to be used in third step
    out1 = '../Files/Fees/report1.csv'
    report1.to_csv(out1, index=False)

    print('     45% Finished', '\n')

    #output = '../Files/auxfile.csv'
    #report.to_csv(output, index=False)
    #report.to_excel('../Files/auxfile.xlsx', index=False)


    print('Calculating total revenue of Clients DB', '\n')
    chunksize2 = chunksize1*5
    chunks = []

    for report1 in pd.read_csv(out1, chunksize=chunksize2):

        #Rename columns by index to apply the opt. eval function
        report1.columns.values[4] = 'S'
        #Aply eval to multiply columns
        report1.eval('T = (F*S)', inplace = True)
        chunks.append(report1)
        print(' ---------- Processing large dataset', j, '\n')
        j+=1


    print('Processing first block', '\n')
    report1 = pd.concat(chunks,axis=0)
    #report1.to_excel('../Files/input-cobranca-v9A.xlsx', index=False)

                   # ------------------ Layer report 2 : Dataset with updates -------------------

    #Create group2 of clients with fees updates
    try:
        report2 = report_group.get_group(1)
    except:
        report2 = report.copy()

    #Create auxiliary column with Suplier stonecodes and dates
    supsc2 = report2[report2.columns[1]]
    splitdate = report2[report2.columns[0]]
    
    merge = [supsc2, splitdate]
    datensc = pd.concat(merge, axis=1)
    #print(datensc[0:5])

    #Create fees column using dicitonary for clients without updates
    fees2 = datensc.apply(mapfees2, args=(fee_group,), axis=1)

    #Create list with dfs to concat after
    frames2 = [report2,fees2]
    #Concat dataframes
    report2 = pd.concat(frames2, axis=1)

    report2.drop(report2.columns[13], axis=1, inplace=True)
    out2 = '../Files/Fees/report2.csv'
    report2.to_csv(out2, index=False)

    print('Calculating total revenue of Clients DB', '\n')

    chunksize3 = chunksize1*3

    chunks = []

    #report2.to_excel('../Files/testereport3.xlsx', index=False)

    print('     65% Finished', '\n')

    for report2 in pd.read_csv(out2, chunksize=chunksize3):

        #Rename columns by index to apply the opt. eval function
        report2.columns.values[13] = 'F'
        report2.columns.values[4] = 'S'
        #Aply eval to multiply columns
        report2.eval('T = (F*S)', inplace = True)
        chunks.append(report2)
        print(' ---------- Processing large dataset', j, '\n')
        j+=1

    print('Processing second block', '\n')
    report2 = pd.concat(chunks,axis=0)
    #report2.to_excel('../Files/input-cobranca-v9B.xlsx', index=False)

    print('     80% Finished', '\n')

    # ----------------- Concat both of three parallelizations into one file ----------------------------------------

    report2 = pd.concat(chunks,axis=0)
    finalframe = [report1,report2]
    report = pd.concat(finalframe,axis=0)

    report.columns.values[4] = 'Valor Direcionado ao Fornecedor (R$)'
    report.columns.values[13] = 'Fee Rate(%)'
    report.columns.values[14] = 'Taxa (R$)'

    #print(report.dtypes)

    #Reorder columns in dataframe, then save csv and finally convert to xlsx

    #Columns names
    saledate = report.columns[0]
    supsc = report.columns[1]
    sup = report.columns[2]
    supcnpj = report.columns[3]
    splitvalue = report.columns[4]
    ecname = report.columns[5]
    eccnpj = report.columns[6]
    pmtdate = report.columns[7]
    ecsc = report.columns[8]
    supgroup = report.columns[9]
    ecgroup = report.columns[10]
    nature = report.columns[11]
    whopays = report.columns[12]
    feerate = report.columns[13]
    fee = report.columns[14]
  
    report = report[[pmtdate, splitvalue, ecname, eccnpj, ecsc, ecgroup, sup, supcnpj, supsc, supgroup, nature, whopays, feerate, fee, saledate]]
    
    #report[fee] = report[fee].apply(lambda x: (str(round(x,16)).replace('.',',')))
    
    #report[splitvalue] = report[splitvalue].apply(lambda x: (str(round(x,16)).replace('.',',')))
    
    #report[feerate] = report[feerate].apply(lambda x: (str(x).replace('.',',')))

    report[pmtdate] = report[pmtdate].apply(lambda x: str(x).replace('-','/'))

    report[saledate] = report[saledate].apply(lambda x: str(x).replace('-','/'))

    report.to_csv('../Files/Fees/input-cobranca-split.csv', index=False, encoding='cp1252')

    try:
        os.remove('../Files/Fees/report1.csv')
        os.remove('../Files/Fees/report2.csv')
    except:
        print('Cant delete Reports in Fees Folder')


    '''
    wb = Workbook()
    ws = wb.active
    with open('../Files/input-cobranca-split.csv', 'r') as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save('../Files/input-cobranca-split.xlsx')
    try:
        os.remove('../Files/input-cobranca-split.csv')
    except:
        print('Cant delete input file')
    '''

    print("--- %s seconds running ---" % (time.time() - start_time))

    print('     100% Finished', '\n')
    
    return 
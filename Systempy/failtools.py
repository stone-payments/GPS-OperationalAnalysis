#Download input system dataframes: All-Sales & Report.
import requests
import os
import pandas as pd
from datetime import datetime as dt
import datetime
from builder_classes import TrxBuild, SaleTrx, BusinessBuild, ClientInfo
import csv
import glob
#import win32com.client as win32

def folders():
    makemydir('../Files/')
    makemydir('../Files/Fees')
    makemydir('../Files/Reports')
    makemydir('../Files/Queries')
    makemydir('../Files/RAV')
    return

# file_download Args: url, output path / filename
def file_download(url, filepath):

    response = requests.get(url)

    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)

    return print('File downloaded from', str(url))


def sniffers(csvfile):

    with open(csvfile, newline='') as f:

        csv_reader = csv.reader(f)

        try:
            csv_headings = next(csv_reader)
            first_line = next(csv_reader)
            strings = ''.join(first_line)
        except:
            strings = 'error, handling'


    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(strings)

    return dialect.delimiter


# Filter splits and sales by range of dates
def dffilter(filepath, Datecol, dateformat, duplicates, output, daterange, deltadi, deltadf, dropdup=0):
    #Daterange = 0 default to daily analysis and >0 to more days in analysis

    #Generating All sales (OR SPLITS) Dataframes from CSVs filtered by range of dates
    #sales_report_filepath = '../Files/allsales.csv'
    df_sales = pd.read_csv(str(filepath), delimiter=sniffers(str(filepath)))

    #If case, Remove Duplicated StoneIDs - boolean analysis and reset index
    if dropdup == 0:
        df_sales.drop_duplicates(subset=[str(duplicates)], inplace=True)

    df_sales = df_sales.reset_index(drop=True)

    #Convert Merchant ID into integers
    #df_sales['Merchant ID'] = df_sales['Merchant ID'].astype(int)

    df_sales[str(Datecol)] = pd.to_datetime(df_sales[str(Datecol)])
    #Remove hours from datetime dates objects
    df_sales[str(Datecol)] = df_sales[str(Datecol)].apply(lambda x: x.date())

    #Convert dates into timestamp
    df_sales[str(Datecol)] = pd.to_datetime(df_sales[str(Datecol)])

    #Set Dates column as index to filter D-1 or D-1 to D-3 in analysis
    df_sales.set_index([str(Datecol)], drop=False)

    #create today's date object and quantify weekdays. (Monday analysis gets 3 previous days)
    today = datetime.date.today()

    weekday = today.weekday()

    #Create range of dates to filter dates

    #At Monday gets sales from friday to sunday and other days only the previous day. I daterange <> 0 then analyse more days
    #in the past
    if daterange == 0:

        first_date = datetime.date.today() - datetime.timedelta(deltadf)

        first_date = str(first_date.strftime(dateformat))

        last_date = datetime.date.today() - datetime.timedelta(deltadi)

        last_date = str(last_date.strftime(dateformat))

        #print(first_date, last_date)

        df_sales_ok = df_sales[(df_sales[str(Datecol)] > first_date) & (df_sales[str(Datecol)] < last_date)]

    else:

        first_date = datetime.date.today() - datetime.timedelta(daterange)

        first_date = str(first_date.strftime(dateformat))

        last_date = datetime.date.today() + datetime.timedelta(1)

        last_date = str(last_date.strftime(dateformat))

        #print(first_date, last_date)

        df_sales_ok = df_sales[(df_sales[str(Datecol)] > first_date) & (df_sales[str(Datecol)] <= last_date)]


    # ----------------------------------------------- Format input data to be used in analysis ----------------------------------- #

    #Create dataframe with transactions in date range
    #filepathout = '../Files/' + str(output) + '_filtered.csv'
    #df_sales_ok.to_csv(filepathout, index=False)

    #filepathout = '../Files/' + str(output) + '_filtered.xlsx'
    #df_sales_ok.to_excel(filepathout, sheet_name='Sheet1', index=False)

    return df_sales_ok


#Compare splits and sales and return differences by stoneid
def dfcompare(filtered_splits,filtered_sales,filepathout):

    #print(filepath1,filepath2,filepathout)

    #All Splits
    #df1 = pd.read_csv(str(filepath1), delimiter=',')
    df1 = filtered_splits
    #Create a copy
    s1 = df1[['StoneID']].copy()
    #Reset index
    s1.reset_index(drop=True)
    #Rename column
    s1.columns = ['Stone IDs']

    #All Sales
    #df2 = pd.read_csv(str(filepath2), delimiter=',')
    df2 = filtered_sales
    s2 = df2[['Stone ID']].copy()
    s2.reset_index(drop=True)
    s2.columns = ['Stone IDs']

    #Compare dataframes
    s3 = get_different_rows(s1,s2)

    #s4 = get_equal_rows(s1,s2)

    #s3.to_csv(filepathout,index=False)

    return s3


#Get difference between two series
def get_different_rows(source_df, new_df):
    merged_df = source_df.merge(new_df, indicator=True, how='outer')
    changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
    return changed_rows_df.drop('_merge', axis=1)


#Get same rows of two series
def get_equal_rows(source_df, new_df):
    merged_df = source_df.merge(new_df, indicator=True, how='outer')
    unchanged_rows_df = merged_df[merged_df['_merge'] != 'right_only']
    return unchanged_rows_df.drop('_merge', axis=1)


#Filter transactions by removing transactions without split contract
def filtertrx(s3, filtered_sales, aux):

    #Set the index as Merchant ID column to iterate on it
    bool_crules = aux.set_index(['Merchant-ID'], drop=False)

    for index , row in s3.iterrows():

        stoneid = row[0]

        #print('ind:', index)

        column = str(filtered_sales.columns[0])

        #get row index by stoneid in allsales
        final_index = get_df_index(filtered_sales, column, stoneid)

        #get brand, transaction type and merchantid from origin (allsales)
        sales_obj = TrxBuild(filtered_sales)
        merchant_ID = sales_obj.nrow(final_index).merchant_ID
        brand = str(sales_obj.nrow(final_index).brand)[:3]
        type = int(sales_obj.nrow(final_index).type)

        #verify if client splits debit (column 4 debit col 6 visa)
        test_debit = bool_crules.loc[merchant_ID][4]

        if test_debit == 0 and type == 1:
            s3.drop(index, inplace=True)

        test_visa = bool_crules.loc[merchant_ID][6]

        if test_visa == 0 and brand == 'Vis':
            s3.drop(index, inplace=True)

        if test_visa == 0 and brand.casefold() == 'cor':
            s3.drop(index, inplace=True)

    return s3


def splitvan(fails_report, baux):

    #van_trx = pd.DataFrame()
    #van_trx['Data da Venda'] = pd.Series([])
    #van_trx['Nome Fantasia do Fornecedor'] = pd.Series([])
    #van_trx['StoneID'] = pd.Series([])
    #van_trx['Parcela Atual'] = pd.Series([])
    #van_trx['Total de parcelas'] = pd.Series([])
    #van_trx['Bandeira'] = pd.Series([])
    #van_trx['Valor Bruto da Transacao'] = pd.Series([])
    #van_trx['Valor Bruto da Parcela'] = pd.Series([])
    #van_trx['Valor direcionado ao Fornecedor'] = pd.Series([])
    #van_trx['Taxa de contrato'] = pd.Series([])
    #van_trx['Tipo'] = pd.Series([])
    #van_trx['Ajuste Financeiro da Transacao'] = pd.Series([])
    #van_trx['StoneCode EC'] = pd.Series([])
    #van_trx['Split Status'] = pd.Series([])

    k=0

    #Set the index as Stonecode column to iterate on it
    bool_van = baux.set_index(['Stonecode-EC'], drop=False)
    bool_van.drop(bool_van.columns[[0,1,3,4,5,6,7,8,9]], axis=1, inplace=True)
    print('1 --------- ',bool_van)

    fails_report_wv = fails_report.copy()

    for index , row in fails_report_wv.iterrows():

        stonecode = row[12]
        brand = str(row[5])[:3]

        #verify if client splits debit (column 4 debit col 6 visa)
        test_van = bool_van.loc[stonecode][1]
        print('testvan', test_van)
        if test_van == 0 and brand == 'Elo':
            fails_report_wv.drop(fails_report_wv.index[k])
            print('deleted')
        k+=1

    return fails_report_wv


def aquirmode(row, dicts):

    #print('--------------- row', row)
    sc = row['StoneCode EC']
    #print('sc', sc)
    brand = str(row['Bandeira'])[:3]
    #print('brand', brand)

    if brand.casefold() == 'elo' and dicts[sc] == 1:
        return 'VAN'
    else:
        return 'STONE'

#Get index of value in a given df's column
def get_df_index(df, column, value):
    index = df[df[column]==value].index.item()
    return index


#Get total of parcels by stone id which failed
def totalparcs(df, id):

    dfgroup = df.groupby(df.columns[0])

    parcgroup = dfgroup.get_group(id)

    totparc = parcgroup[parcgroup.columns[6]].max()

    return totparc


#Create parcels dictionary
def parcdic(fail_list, fail_sales):

    parc_dict = {}

    j=0

    parcels_list = []

    for id in fail_list:
        parcels_list.append(totalparcs(fail_sales, id))

    for fail in fail_list:
        parc_dict[fail] = parcels_list[j]
        j+=1

    return parc_dict


#Get total of parcels by stone id which failed
def grosstrx(df,id):

    dfgroup = df.groupby(df.columns[0])

    parcgroup = dfgroup.get_group(id)

    gross_value = parcgroup[parcgroup.columns[3]].sum()

    return gross_value


#Create gross ammount dictionary
def grossdic(fail_list, fail_sales):

    gross_dict = {}

    j=0

    gross_list = []

    for id in fail_list:
        gross_list.append(grosstrx(fail_sales, id))

    for fail in fail_list:
        gross_dict[fail] = gross_list[j]
        j+=1

    return gross_dict


#Create report of fails similar to split report to apply metrics after that
# use https://stackoverflow.com/questions/13148429/how-to-change-the-order-of-dataframe-columns to reorder columns when creating report
def simfails(fail_sales, gross_dict,parc_dict):

    #Create empty df
    fails_report = pd.DataFrame()

    fails_report['Data da Venda'] = pd.Series([])
    fails_report['Nome Fantasia do Fornecedor'] = pd.Series([])
    fails_report['StoneID'] = pd.Series([])
    fails_report['Parcela Atual'] = pd.Series([])
    fails_report['Total de parcelas'] = pd.Series([])
    fails_report['Bandeira'] = pd.Series([])
    fails_report['Valor Bruto da Transacao'] = pd.Series([])
    fails_report['Valor Bruto da Parcela'] = pd.Series([])
    fails_report['Valor direcionado ao Fornecedor'] = pd.Series([])
    fails_report['Taxa de contrato'] = pd.Series([])
    fails_report['Tipo'] = pd.Series([])
    fails_report['Ajuste Financeiro da Transacao'] = pd.Series([])
    fails_report['StoneCode EC'] = pd.Series([])
    fails_report['Split Status'] = pd.Series([])

    i=0

    #Get business rules info about client (Debit split and Visa Split)
    aux = pd.read_csv('../Business-Rules/Regras-de-negocio_MID.csv', delimiter=';')

    #Set the index as Merchant ID column to iterate on it
    bool_crules = aux.set_index(['Merchant-ID'], drop=False)

    #verify if client splits debit (column 4 debit col 6 visa)

    for index, row in fail_sales.iterrows():

        if row[4] == 1:
            tipo = 'Debito'
        else:
            tipo = 'Credito'

        merchant_ID = row[2]

        gross = gross_dict[row[0]]
        parcs = parc_dict[row[0]]
        parcval = float(gross)/float(parcs)
        ratio = bool_crules.loc[merchant_ID][1]

        fails_report.loc[i,'Ajuste Financeiro da Transacao'] = parcval
        fails_report.loc[i,'Data da Venda'] = str(row[1])[:10]
        fails_report.loc[i,'StoneCode EC'] = bool_crules.loc[merchant_ID][10]
        fails_report.loc[i,'Nome Fantasia do Fornecedor'] = bool_crules.loc[merchant_ID][8]
        fails_report.loc[i,'StoneID'] = row[0]
        fails_report.loc[i,'Parcela Atual'] = row[6]
        fails_report.loc[i,'Total de parcelas'] = parc_dict[row[0]]
        fails_report.loc[i,'Bandeira'] = row[5]
        fails_report.loc[i,'Valor Bruto da Transacao'] = float(gross)
        fails_report.loc[i,'Valor Bruto da Parcela'] = parcval
        fails_report.loc[i,'Taxa de contrato'] = ratio
        fails_report.loc[i,'Valor direcionado ao Fornecedor'] = float(ratio) * parcval
        fails_report.loc[i,'Tipo'] = tipo
        fails_report.loc[i,'Split Status'] = 'Split fail'

        i+=1

    return fails_report


#Join split and split fails sales
def joindftrx(all_splits,fails_report, sufix):

    #all_splits.to_excel('../Files/split_report.xlsx',index=False)

    all_splits.drop(all_splits.columns[[1, 3, 8, 11, 14, 15, 16, 18]], axis=1, inplace=True)

    all_splits['Split Status'] = 'Split ok'

    all_trx = pd.concat([all_splits,fails_report], ignore_index=True)

    #fails_report.to_excel('../Files/fails_report.xlsx',index=False)

    #alltrxname = '../Files/All/all_trx_' + sufix + '.xlsx'

    #all_trx.to_excel(alltrxname,index=False)

    return all_trx


#Groupby agnostic function
def aggdfs(df,colind, filter):

    dfgroup = df.groupby(df.columns[colind])

    groupbykey = dfgroup.get_group(str(filter))

    #gross_value = parcgroup[parcgroup.columns[3]].sum()

    return groupbykey


#Create failed sales object with parcels level
def create_fail_sales(df, fail_list, column):

    fail_sales = df[df[column].isin(fail_list)]

    fail_sales = fail_sales.reset_index(drop=True)

    return fail_sales


def gethours(list, df, column):

    dfout = df[df[column].isin(list)]

    return dfout


def maphours(row, dict):

    return dict[row]


def errormsg():

    analysis_filepath = '../Files/Error_Message.txt'

    with open(analysis_filepath, 'w') as file:
        file.write('Error with input Files. Verify the AllSales, Report and queries.')

    return


def lookupfiles(path, format):

    k = 0
    df_list = []
    df_dict = {}

    #Look for files in folder convert them into DF
    for fn in os.listdir(path):

        ext = (-1)*len(format)

        if str(fn)[ext:] == format:

            filepath = str(path) + str(fn)

            dfname = 'rav' + str(k)

            df_dict[dfname] = pd.read_csv(filepath, delimiter=';')

            k+=1

    #Join all DFs remove duplicates and convert into list to compare
    for key in df_dict:
        #print(df_dict[key])
        df_list.append(df_dict[key])

    rav = pd.concat(df_list, axis=0)

    return rav


def makemydir(path):
    try:
        os.makedirs(path)
        print(' * Folder ', path, 'created.')
    except OSError:
        print(' * Folder at path:', path, 'already exists.')
        pass


def foldersufix(delta):

    analysis_date = datetime.date.today() - datetime.timedelta(delta)
    weekday = (analysis_date).weekday()

    if weekday == 0:
        sufix = 'Mon'
    elif weekday == 1:
        sufix = 'Tue'
    elif weekday == 2:
        sufix = 'Wed'
    elif weekday == 3:
        sufix = 'Thu'
    elif weekday == 4:
        sufix = 'Fri'
    elif weekday == 5:
        sufix = 'Sat'
    else:
        sufix = 'Sun'

    return sufix


'''
#Send e-mail via outlook
def mailler():

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = 'lucas.rocha@stone.com.br'
    mail.Subject = 'Python Message subject'
    mail.Body = 'Message body'
    mail.HTMLBody = 'Message Body HTML VIA FLASK'

    # To attach a file to the email (optional):
    #attachment  = path
    #mail.Attachments.Add(attachment)

    mail.Send()


    return

'''
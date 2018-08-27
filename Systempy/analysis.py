from failtools import *
from builder_classes import *
from datetime import datetime as dt
import datetime
import json
import os.path
import sys

def split_analysis(daterange, deltadi, deltadf):

    #Range differ daily from full analysis
    # Range input for Daily get range from 1 to 3 days (weekday or weekend) or Generic

    print('The Analysis is starting. This may take up to 5 minutes.', '\n')

    # ---------------------------------------------- Download all sales and report from Split Endpoint ------------------ #

    #Downloading Split Report generated from query treatment.
    outputpath = '../Files/Queries/'

    split_filepath = outputpath + 'report.csv'

    print('     10% Finished', '\n')

    #Downloading All sales Report generated from query

    sales_filepath = outputpath + 'allsales.csv'

    print('     20% Finished', '\n')

    # ------------------------------------------ Call function to filter last days of splits and all sales ---------------------------
    
    salesoutput = 'allsales'
    splitsoutput = 'splits'

    dateformat = '%Y-%m-%d'
    
    #Filter sales
    print('Applying filter to dataframes', '\n')
    filtered_sales = dffilter(sales_filepath, 'Data da venda', str(dateformat),'Stone ID',str(salesoutput),daterange, deltadi, deltadf) 
    filtered_sales = filtered_sales.reset_index(drop=True)

    #Filter splits
    try:
        filtered_splits = dffilter(split_filepath, 'Data da Venda', str(dateformat),'StoneID',str(splitsoutput),daterange, deltadi, deltadf)
        filtered_splits = filtered_splits.reset_index(drop=True)
    except:
        print(' ------------- Error filtering query, please check the files --------')
        sys.exit(1)
    print('     40% Finished', '\n')

    # ----------------------------  Compare both stoneids to output Split Fails  --------------------------------------------------
    
    print('Starting Comparisson', '\n')

    sufix = '_filtered.csv'

    #File name of splits filtered
    filteredout1 = outputpath + splitsoutput + sufix

    #File name of sales filtered
    filteredout2 = outputpath + salesoutput + sufix

    #File name of result file. List of difference between splits and sales (StoneIDs Fails list)
    result = outputpath + 'Split_fails.csv'

    # -------------------------  Create list with differences by Stone ID and filter trx without contracts  ------------------------------------------------------------------
    
    #Lits of differences by stoneids
    s3 = dfcompare(filtered_splits,filtered_sales,result)

    s3 = s3.reset_index(drop=True)

    #Get business rules info about client (Debit split and Visa Split)
    baux = pd.read_csv('../Business-Rules/Regras-de-negocio_MID.csv', delimiter=';')

    #Filter s3 to get list of real split fails
    s3 = filtertrx(s3,filtered_sales, baux)

    s3 = s3.reset_index(drop=True)

    fail_list = s3['Stone IDs'].tolist()

    print(fail_list)

    #Load new All Sales to get fail sales only
    new_df_sales = pd.read_csv(sales_filepath, delimiter=';')
    #Filter all sales only with fails to do split simulation
    fail_sales = create_fail_sales(new_df_sales,fail_list,'Stone ID')  
       
    print('     65% Finished', '\n')

    # -------------------------  Simulate splits for analysis -----------------------------------------------------------------

    print('Starting Simulation', '\n')

    #Get the number of rows to iterate in simulation
    numfails = len(s3.index)

    #Create dictionary with StoneID:Totalparc to iterate over it at simulation
    parc_dict = parcdic(fail_list, fail_sales)

    #Create dictionary with StoneID:Gross Ammount to iterate over it at simulation
    gross_dict = grossdic(fail_list, fail_sales)

    #Create fail_sales obj
    fails_obj = TrxBuild(fail_sales)

    #Create Fails Report simulation
    fails_report = simfails(fail_sales, gross_dict, parc_dict)
    
    #Create a Fails_report
    
    # -------------------------  Prepare files, variables and dicts for for analysis daily report ------------------------------------------------------------------
    
    today = datetime.date.today()

    delta = deltadf - 1
    
    analysis_date = datetime.date.today() - datetime.timedelta(delta)
    
    weekday = (analysis_date).weekday()

    analysis_date = str(analysis_date.strftime(dateformat))
    
    #Get string format for weekday
    if daterange ==0:
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
    else:
        sufix = 'All'
    
    #Create Day folders and subfolders to work in parametric way
    folname = '../Files/Reports/' + str(sufix)
    makemydir(folname)
    folnameall = folname + '/All'
    makemydir(folnameall)
    folnamefails = folname + '/Fails'
    makemydir(folnamefails)
    folnameresult = folname + '/Result'
    makemydir(folnameresult)

    #Argument dropdup = 1 given to remove duplicades
    all_splits = dffilter(split_filepath, 'Data da Venda', str(dateformat),'StoneID',str(splitsoutput),daterange, deltadi, deltadf, 1)

    all_trx = joindftrx(all_splits, fails_report, sufix)
  

    #van_trx = splitvan(fails_report, baux)

    allpath = folnameall + '/All_trx_' + sufix + '.xlsx'
    vanpath = folnameall + '/VAN_trx_' + sufix + '.xlsx'

    all_trx.to_excel(allpath,index=False)
    #van_trx.to_excel(vanpath,index=False)

    print('     85% Finished', '\n')

    print('Starting detailed analysis', '\n')

    kpi_dict = {}
            
    #Get all Contractual Sales by Split theoretical Value and num of trx (Debit)

    dict_ind = 'Analysis_' + sufix

    kpi_dict[dict_ind] = {}

    kpi_dict[dict_ind]['Date'] = {}

    kpi_dict[dict_ind]['Date'] = analysis_date

    kpi_dict[dict_ind]['All'] = {}
    kpi_dict[dict_ind]['Fail'] = {}
    kpi_dict[dict_ind]['Splitted'] = {}
    kpi_dict[dict_ind]['Fail_Statistics'] = {}
    kpi_dict[dict_ind]['Fail_Statistics_Lost'] = {}

    kpi_dict[dict_ind]['All']['Debit'] = {}
    kpi_dict[dict_ind]['All']['Credit'] = {}
    kpi_dict[dict_ind]['All']['Total'] = {}
    
    kpi_dict[dict_ind]['Fail']['Debit'] = {}
    kpi_dict[dict_ind]['Fail']['Credit'] = {}
    kpi_dict[dict_ind]['Fail']['Total'] = {}
    
    try:
        alldebit = aggdfs(all_trx,10,'Debito')
    except:
        print(' ---------- No debit transactions Found. Please check the queries. ----------')
        sys.exit(1)
    adsum = round(alldebit[alldebit.columns[8]].sum(),2)

    kpi_dict[dict_ind]['All']['Debit']['Sum'] = adsum

    adnum = alldebit.drop_duplicates(subset=[alldebit.columns[2]], inplace=False).shape[0]

    kpi_dict[dict_ind]['All']['Debit']['Number_of_trx'] = adnum

    try:
        allcredit = aggdfs(all_trx,10,'Credito')
    except:
        print(' -------- No credit transactions found. Please check the queries. ---------- ')
    acsum = round(allcredit[allcredit.columns[8]].sum(),2)

    kpi_dict[dict_ind]['All']['Credit']['Sum'] = acsum

    acnum = allcredit.drop_duplicates(subset=[allcredit.columns[2]], inplace=False).shape[0]

    kpi_dict[dict_ind]['All']['Credit']['Number_of_trx'] = acnum

    kpi_dict[dict_ind]['All']['Total']['Sum'] = round(adsum + acsum,2)
    kpi_dict[dict_ind]['All']['Total']['Number_of_trx'] = adnum + acnum

    #Get fails theoretical split value

    try:
        faildebit = aggdfs(fails_report,10,'Debito')

        fdsum = round(faildebit[faildebit.columns[8]].sum(),2)

        kpi_dict[dict_ind]['Fail']['Debit']['Sum'] = fdsum

        fdnum = faildebit.drop_duplicates(subset=[faildebit.columns[2]], inplace=False).shape[0]

        kpi_dict[dict_ind]['Fail']['Debit']['Number_of_trx'] = fdnum
    
    except:
        fdsum = 0
        fdnum = 0
        kpi_dict[dict_ind]['Fail']['Debit']['Sum'] = fdsum
        kpi_dict[dict_ind]['Fail']['Debit']['Number_of_trx'] = fdnum
        faildebit = pd.DataFrame()
        faildebit['Data da Venda'] = pd.Series([])
        faildebit['Nome Fantasia do Fornecedor'] = pd.Series([])
        faildebit['StoneID'] = pd.Series([])
        faildebit['Parcela Atual'] = pd.Series([])
        faildebit['Total de parcelas'] = pd.Series([])
        faildebit['Bandeira'] = pd.Series([])
        faildebit['Valor Bruto da Transacao'] = pd.Series([])
        faildebit['Valor Bruto da Parcela'] = pd.Series([])
        faildebit['Valor direcionado ao Fornecedor'] = pd.Series([])
        faildebit['Taxa de contrato'] = pd.Series([])
        faildebit['Tipo'] = pd.Series([])
        faildebit['Ajuste Financeiro da Transacao'] = pd.Series([])
        faildebit['StoneCode EC'] = pd.Series([])
        faildebit['Split Status'] = pd.Series([])

    try:
        failcredit = aggdfs(fails_report,10,'Credito')

        fcsum =  round(failcredit[failcredit.columns[8]].sum(),2)

        kpi_dict[dict_ind]['Fail']['Credit']['Sum'] = fcsum

        fcnum = failcredit.drop_duplicates(subset=[failcredit.columns[2]], inplace=False).shape[0]

        kpi_dict[dict_ind]['Fail']['Credit']['Number_of_trx'] = fcnum
    
    except:
        fcsum = 0
        fcnum = 0
        kpi_dict[dict_ind]['Fail']['Credit']['Sum'] = fcsum
        kpi_dict[dict_ind]['Fail']['Credit']['Number_of_trx'] = fcnum
        failcredit = pd.DataFrame()
        failcredit['Data da Venda'] = pd.Series([])
        failcredit['Nome Fantasia do Fornecedor'] = pd.Series([])
        failcredit['StoneID'] = pd.Series([])
        failcredit['Parcela Atual'] = pd.Series([])
        failcredit['Total de parcelas'] = pd.Series([])
        failcredit['Bandeira'] = pd.Series([])
        failcredit['Valor Bruto da Transacao'] = pd.Series([])
        failcredit['Valor Bruto da Parcela'] = pd.Series([])
        failcredit['Valor direcionado ao Fornecedor'] = pd.Series([])
        failcredit['Taxa de contrato'] = pd.Series([])
        failcredit['Tipo'] = pd.Series([])
        failcredit['Ajuste Financeiro da Transacao'] = pd.Series([])
        failcredit['StoneCode EC'] = pd.Series([])
        failcredit['Split Status'] = pd.Series([])


    #Get total sum and num of fails
    kpi_dict[dict_ind]['Fail']['Total']['Sum'] = round(fcsum + fdsum,2)
    kpi_dict[dict_ind]['Fail']['Total']['Number_of_trx'] = fcnum + fdnum

    kpi_dict[dict_ind]['Splitted']['Debit']  = {}
    kpi_dict[dict_ind]['Splitted']['Debit']['Sum'] = round(adsum - fdsum,2)
    kpi_dict[dict_ind]['Splitted']['Debit']['Number_of_trx'] = adnum - fdnum
 
    kpi_dict[dict_ind]['Splitted']['Credit'] = {}
    kpi_dict[dict_ind]['Splitted']['Credit']['Sum'] = round(acsum - fcsum,2)
    kpi_dict[dict_ind]['Splitted']['Credit']['Number_of_trx'] = acnum - fcnum

    kpi_dict[dict_ind]['Splitted']['Total'] = {}
    kpi_dict[dict_ind]['Splitted']['Total']['Sum'] = round((acsum + adsum) - (fcsum + fdsum),2)
    kpi_dict[dict_ind]['Splitted']['Total']['Number_of_trx'] = (acnum + adnum) - (fcnum + fdnum)
    
    
    #Copy StoneIDs column of debit fails only
    didfails = faildebit[faildebit.columns[2]].copy()
    #Convert series pandas values to list
    list_didfails = didfails.values.tolist()
    p = 0
    for id in list_didfails:
        list_didfails[p] = str(id)[:-2]
        p+=1
    #Remove "[]" and converts list to joint str 
    str_didfails = ''.join(str(list_didfails))[1:-1]
    #Copy StoneIDs column of credit fails only
    cidfails = failcredit[failcredit.columns[2]].copy()
    #Remove duplicates of parcels if exists
    try:
        cidfails2 = cidfails.drop_duplicates()
    except:
        pass
    #Convert series pandas values to list
    list_cidfails = cidfails2.values.tolist()
    #Convert all integer itens in list to strings without float point decimals
    k = 0
    for id in list_cidfails:
        list_cidfails[k] = str(id)[:-2]
        k+=1
    #Remove "[]" and converts list to joint str 
    str_cidfails = ''.join(str(list_cidfails))[1:-1]

    #Analyze transactions liquidated --------------- Anticipated or Debit Fails in D+2
    
    # -------------------------------- CREDIT Analysis ID LIST
    #Get all stoneids from RAV
    try:
        ravdf = lookupfiles('../Files/RAV/', '.csv')
        #Convert it into a list without duplicates
        ravlist = ravdf[ravdf.columns[1]].drop_duplicates().values.tolist()

        #Map all Strings and convert them into integers
        list_cidfails2 = [int(x) for x in list_cidfails]
        #Intersect fails with RAV list to get fails without anticipations   
        for i in ravlist:
            if i in list_cidfails2:
                list_cidfails2.remove(i)

        list_cidfails3 = [str(x) for x in list_cidfails2]
        str_cidfailrepr = ''.join(str(list_cidfails3))[1:-1]
    except:
        str_cidfailrepr = ''
        ravlist = []

    # -------------------------------- CREDIT Analysis ID Report

    #failcredit.to_excel('../Files/failcred.xlsx')

    try:
        cstonecodes = failcredit[failcredit.columns[2]].reset_index(drop=True)
    except:
        pass
    
    ravcheck = []
    testelista = []

    for index, row in cstonecodes.items():
        #print('STONEID IS =', row)
        if row in ravlist:
            ravcheck.append('Liquidou')
        else:
            ravcheck.append('N Liquidou')
    
    ravliquids = pd.DataFrame(ravcheck)

    #print(liquids)
    failcredit = failcredit.reset_index(drop=True)

    failcredit = pd.concat([failcredit,ravliquids], axis=1)
  
    try:
        failcredit.columns.values[14] = 'Liquidou?'
    except:
        failcredit['Liquidou?'] = pd.Series([])

    # -------------------------------- DEBIT Analysis ID Report

    #Get business rules info about client (Debit split and Visa Split)
    aux = pd.read_csv('../Business-Rules/Regras-de-negocio_MID.csv', delimiter=';')
    aux = aux[[aux.columns[3],aux.columns[10]]]

    #Set the index as Merchant ID column to iterate on it
    debitpmt = aux.set_index(['Stonecode-EC'], drop=True)
    
    pmttype = []
    
    try:
        dstonecodes = faildebit[faildebit.columns[12]].reset_index(drop=True)
        for index, row in dstonecodes.items():
            sc = row
            testdebit = debitpmt.loc[sc][0]
            if testdebit == 0:
                pmttype.append('Liquidou')
            else:
                pmttype.append('N Liquidou')
    except:
        pass
    
    


    
    liquids = pd.DataFrame(pmttype)

    faildebit = faildebit.reset_index(drop=True)
    
    faildebit = pd.concat([faildebit,liquids], axis=1)
    
    try:
        faildebit.columns.values[14] = 'Liquidou?'
    except:
        faildebit['Liquidou?'] = pd.Series([])
    
    
    # ----------------------------------  DEBIT Analysis ID List

    #Convert df to list without duplicates
    try:
        reprdebit = aggdfs(faildebit, 14, 'N Liquidou')
        debitd2list = reprdebit[reprdebit.columns[2]].values.tolist()

        debitd2list2 = [str(int(x)) for x in debitd2list]
        str_didfailrepr = ''.join(str(debitd2list2))[1:-1]
    except:
        str_didfailrepr = ''

    # -------------------------------------------------------------------------------------------- #

    #Concat Debit Failsv2 wih Credit Failsv2 and then add hours

    frames4 = [faildebit, failcredit]

    fails_report = pd.concat(frames4,axis=0)

    #Create aux frames to concat hours series into fails

    #Function to compare a column df with a list and return ocurrencies

    #Load new All Sales to get fail sales only
    aux_df_sales = pd.read_csv(sales_filepath, delimiter=';')

    fail_list2 = fails_report[fails_report.columns[2]].tolist()
    #print('faillist2', fail_list2)
    
    aux_df_fails = create_fail_sales(aux_df_sales,fail_list2, 'Stone ID')
    #print('auxdffails', aux_df_fails)
    
    dfaux = gethours(fail_list2, aux_df_fails, 'Stone ID')

    #Get only hours from datetime string
    fail_hours = dfaux[[dfaux.columns[0],dfaux.columns[1]]]
    fail_hours[fail_hours.columns[1]] = fail_hours[fail_hours.columns[1]].apply(lambda x: str(x)[-15:])
    fail_hours.drop_duplicates(subset=[fail_hours.columns[0]], inplace=True)

    #Create hours dictionary
    hours_dict = {}
    for index, row in fail_hours.iterrows():
        stoneid = row[0]
        time = row[1]
        hours_dict[stoneid] = time
    
    #Create column with stoneids failed
    df_stoneids = fails_report[fails_report.columns[2]]
    #Create column with hours mapped by hours dict
    df_hours = df_stoneids.apply(maphours, args=(hours_dict,))
    
    frames5 = [fails_report, df_hours]
    #Join hours colum to the left of the dataframe fails report
    fails_report = pd.concat(frames5, axis=1)
    fails_report.columns.values[15] = 'Hora da Venda'
    #Drop columns and duplicate rows
    fails_report.drop(fails_report.columns[[3,7,8,11,13,]], axis=1, inplace=True)
    fails_report.drop_duplicates(subset=[fails_report.columns[2]], inplace=True)


    # Create reports for reprocessing, with and without VAN

    #Save file names
    failsreportname = folnamefails + '/fails_report_' + sufix + '.csv'
    failsreportvname = folnamefails + '/fails_report_van_' + sufix + '.csv'
    repreportname = folnamefails + '/reprocess_report_' + sufix + '.csv'

    #Modify fails_report to apply VAN aquirer trx mode 

    bool_van = baux.set_index(['Stonecode-EC'], drop=False)
    
    bool_van.drop(bool_van.columns[[0,1,3,4,5,6,7,8,9]], axis=1, inplace=True)

    van_dict = {}
    
    #print(bool_van[0:5])

    for index, row in bool_van.iterrows():
        stonecode = row[1]
        aqmode = row[0]
        van_dict[stonecode] = aqmode

    #print(van_dict) 

    reportsc = fails_report[fails_report.columns[8]]

    reportbrand = fails_report[fails_report.columns[4]]

    merge3 = [reportsc,reportbrand]

    brandnsc = pd.concat(merge3, axis=1)

    brandnsc = brandnsc.reset_index(drop=True)
    
    fails_report = fails_report.reset_index(drop=True)

    aquirercol = brandnsc.apply(aquirmode, args=(van_dict,), axis=1)

    frames6 = [fails_report, aquirercol]
    
    fails_report_full = pd.concat(frames6, axis=1)

    fails_report_full.columns.values[11] = 'Adq. Elo Van?'

    #Split and save different reports by aq. mode
    try:
        fails_report_ok = aggdfs(fails_report_full, 11, 'STONE')
        fails_report_ok.to_csv(failsreportname,index=False, sep=';')
    except:
        print('No fails.')

    try:
        fails_report_van = aggdfs(fails_report_full, 11, 'VAN') 
        fails_report_van.to_csv(failsreportvname,index=False, sep=';')
    except:
        print('No VAN fails.')  
    #Group trx by paid and not paid to reprocessing routine
    try:
        reprocess = aggdfs(fails_report, 9, 'N Liquidou')
        reprocess.to_csv(repreportname,index=False, sep=';')
    except:
        print(' * No transactions to reprocess.')


    #Get information about lost transactions (Diff between all fails and non liquidated)
    try:
        fails_lostr = aggdfs(fails_report_ok, 9, 'Liquidou')
        fail_lostr_d = aggdfs(fails_lostr, 7, 'Credito')['Valor Bruto da Transacao']
        fail_lostr_dsum = fail_lostr_d.sum()
        fail_lostr_dnum = fail_lostr_d.shape[0]
    except:
        print('None of the Debit fails has been liquidated yet.')
        fail_lostr_dsum = 0
        fail_lostr_dnum = 0

    try:
        fails_lostr = aggdfs(fails_report_ok, 9, 'Liquidou')
        fail_lostr_c = aggdfs(fails_lostr, 7, 'Debito')['Valor Bruto da Transacao']
        fail_lostr_csum = fail_lostr_c.sum()
        fail_lostr_cnum = fail_lostr_c.shape[0]
    except:
        print('None of the Credit fails has been liquidated yet.')
        fail_lostr_csum = 0
        fail_lostr_cnum = 0


    #Add stoneids to dictionaries
    kpi_dict[dict_ind]['ID_Fail_List'] = {}
    kpi_dict[dict_ind]['ID_Fail_List']['All'] = {}
    kpi_dict[dict_ind]['ID_Fail_List']['All']['Debit'] = str_didfails
    kpi_dict[dict_ind]['ID_Fail_List']['All']['Credit'] = str_cidfails

    #List without anticipated or paid StoneIDs
    kpi_dict[dict_ind]['ID_Fail_List']['For_Reprocessing'] = {}
    kpi_dict[dict_ind]['ID_Fail_List']['For_Reprocessing']['Credit'] = str_cidfailrepr
    kpi_dict[dict_ind]['ID_Fail_List']['For_Reprocessing']['Debit'] = str_didfailrepr

    #Calculate Fail % by value and number of fails
    kpi_dict[dict_ind]['Fail_Statistics']['Debit'] = {}
    kpi_dict[dict_ind]['Fail_Statistics']['Credit'] = {}
    kpi_dict[dict_ind]['Fail_Statistics']['Total'] = {}

    try:
        kpi_dict[dict_ind]['Fail_Statistics']['Debit']['Percentage_of_value'] = str(round( (float(fdsum)/float(adsum)*100) , 2)) + '%'
    except:
        kpi_dict[dict_ind]['Fail_Statistics']['Debit']['Percentage_of_value'] = 0

    try:
        kpi_dict[dict_ind]['Fail_Statistics']['Credit']['Percentage_of_value'] = str(round( (float(fcsum)/float(acsum)*100), 2)) + '%'
    except:
        kpi_dict[dict_ind]['Fail_Statistics']['Credit']['Percentage_of_value'] = 0

    try:
        kpi_dict[dict_ind]['Fail_Statistics']['Debit']['Percentage_of_transactions'] = str(round( (float(fdnum)/float(adnum)*100), 2)) + '%'
    except:
        kpi_dict[dict_ind]['Fail_Statistics']['Debit']['Percentage_of_transactions'] = 0

    try:
        kpi_dict[dict_ind]['Fail_Statistics']['Credit']['Percentage_of_transactions'] = str(round( (float(fcnum) / float(acnum)*100) , 2)) + '%'
    except:
        kpi_dict[dict_ind]['Fail_Statistics']['Credit']['Percentage_of_transactions'] = 0

               
    kpi_dict[dict_ind]['Fail_Statistics']['Total']['Percentage_of_value'] = str(round((((fcsum + fdsum) / (adsum + acsum)) * 100),2)) + '%'
    kpi_dict[dict_ind]['Fail_Statistics']['Total']['Percentage_of_transactions'] = str(round(((fcnum + fdnum) / (adnum + acnum) * 100),2)) + '%'

    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Credit'] = {}
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Credit']['Percentage_of_value'] = str(round((float(fail_lostr_csum)/float(acsum)*100), 2)) + '%'
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Credit']['Percentage_of_transactions'] = str(round((float(fail_lostr_cnum)/float(acnum)*100), 2)) + '%'

    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Debit'] = {}
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Debit']['Percentage_of_value'] = str(round((float(fail_lostr_dsum)/float(adsum)*100), 2)) + '%'
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Debit']['Percentage_of_transactions'] = str(round((float(fail_lostr_dnum)/float(adnum)*100), 2)) + '%'

    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Total'] = {}
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Total']['Percentage_of_value'] = str(round((float(fail_lostr_csum)/float(acsum)*100), 2)) + '%'
    kpi_dict[dict_ind]['Fail_Statistics_Lost']['Total']['Percentage_of_transactions'] = str(round((float(fail_lostr_dnum+fail_lostr_cnum)/float(acnum+adnum)*100), 2)) + '%'

    #Compare Fail Statistics with lost transactions to reprocess those ain't paid

    strfile = json.dumps(kpi_dict,sort_keys=True,indent=2,separators=(',',':'))

    stroutput = kpi_dict

    print('     100% Finished.', '\n', '\n', sufix, ' split Fail Analysis Finished Sucessful!')

    analysis_filepath = folnameresult + '/Analysis_Result_' + sufix + '.txt'

    with open(analysis_filepath, 'w') as file:
        file.write(strfile)

    return

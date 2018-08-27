def frulesdict(df):

    fees_dict = {}

    for index, row in df.iterrows():

        fees_dict[index] = {}
        fees_dict[index]['suplier'] = row[0]
        fees_dict[index]['ecgroup'] = row[2]
        fees_dict[index]['supgroup'] = row[3]
        fees_dict[index]['nature'] = row[4]
        fees_dict[index]['whopay'] = row[5]
        fees_dict[index]['updates'] = row[6]
    
    return fees_dict 


def maprules(row, dict, par):
    
    return dict[row][par]

def mapfees1(row, dict):
    
    return dict[row]


def mapfees2(row, df):

    suplisc = row['StoneCode Fornecedor']
    splitdate = row['Data da Venda']

    #Get the suplier stonecode from column and filter groupped df
    fee_forn = df.get_group(suplisc)
    fee_forn = fee_forn.sort_values(by=['Update'])

    k = 0
    x = 0

    while x < 1:
        if  fee_forn.iloc[k,2] > splitdate:
            feeratio = float(fee_forn.iloc[k,1])
            x=2
        else:
            k+=1

    return feeratio


def feesdict(df):

    feesdict = {}

    for index, row in df.iterrows():

        feesdict[index] = row[1]
    
    return feesdict 


def mapstr(row):
    return round(float((str(row).replace('.',','))),2)
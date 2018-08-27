import pandas as pd

#Create transaction object by index (dtype = unicode removed)
class TrxBuild:
  
    def __init__(self, df):

        self.df = df

    def nrow(self, row):

        stoneid = self.df[self.df.columns[0]][row]
        date = self.df[self.df.columns[1]][row]
        merchant_ID = self.df[self.df.columns[2]][row]
        gross_value = self.df[self.df.columns[3]][row]
        type = self.df[self.df.columns[4]][row]
        brand = self.df[self.df.columns[5]][row]
        nparc = self.df[self.df.columns[6]][row]

        return SaleTrx(stoneid, date, merchant_ID, gross_value, type, brand, nparc)

class SaleTrx:
    
    def __init__(self, stoneid, date, merchant_ID, gross_value, type, brand, nparc):
        
        self.stoneid = stoneid
        self.date = date
        self.merchant_ID = merchant_ID
        self.gross_value = gross_value
        self.type = type
        self.brand = brand
        self.nparc = nparc



#Create multisplit object by index  (BETA)
class SplitBuild:

    def __init__(self, df):

        self.df = df

    def nrow(self, row):

        pmtdate = report[report.columns[16]][row]
        splitvalue = report[report.columns[12]][row]
        ec = report[report.columns[14]][row]
        cnpjec = report[report.columns[15]][row]
        scec = report[report.columns[20]][row]
        supname = report[report.columns[2]][row]
        supsc = report[report.columns[1]][row]
        splitdate = report[report.columns[0]][row]

        return SplitTrx(pmtdate, splitvalue, ec, cnpjec, scec, supname, supsc, splitdate)

class SplitTrx():

    def __init__(init, pmtdate, splitvalue, ec, cnpjec, scec, supname, supsc, splitdate):
        
        self.pmtdate = pmtdate
        self.splitvalue = splitvalue
        self.ec = ec
        self.cnpjec = cnpjec
        self.scec = scec
        self.supname = supname
        self.supsc = supsc
        self.splitdate = splitdate



#Create transaction object by index (dtype = unicode removed)
class FeeBuild:
  
    def __init__(self, df):

        self.df = df

    def nrow(self, row):

        lastdate = self.df[self.df.columns[0]][row]
        suplier = self.df[self.df.columns[1]][row]
        supliersc = self.df[self.df.columns[2]][row]
        ecgroup = self.df[self.df.columns[3]][row]
        supgroup = self.df[self.df.columns[4]][row]
        nature = self.df[self.df.columns[5]][row]
        whopay = self.df[self.df.columns[6]][row]
        fee = self.df[self.df.columns[7]][row]

        return ClientFee(lastdate, suplier, supliersc, ecgroup, supgroup, nature, whopay, fee)


class ClientFee:
    
    def __init__(self, lastdate, suplier, supliersc, ecgroup, supgroup, nature, whopay, fee):
        
        self.lastdate = lastdate
        self.suplier = suplier
        self.supliersc = supliersc
        self.ecgroup = ecgroup
        self.supgroup = supgroup
        self.nature = nature
        self.whopay = whopay
        self.fee = fee





#Create busines rules object by index
class BusinessBuild:

    def __init__(self, path):
        
        self.path = path
        self.df = pd.read_csv(self.path, delimiter=';')

    def nrow(self, row):    

        stonecode = self.df[self.df.columns[0]][row]
        split_ratio = self.df[self.df.columns[1]][row]
        elo_mode = self.df[self.df.columns[2]][row]
        liq_days = self.df[self.df.columns[3]][row]
        split_deb = self.df[self.df.columns[4]][row]
        split_cred = self.df[self.df.columns[5]][row]
        split_visa = self.df[self.df.columns[6]][row]
        RS_EC = self.df[self.df.columns[7]][row]
        suplier = self.df[self.df.columns[8]][row]
        first_date = self.df[self.df.columns[9]][row]
        merchant_ID = self.df[self.df.columns[10]][row]

        return ClientInfo(stonecode, split_ratio, elo_mode, liq_days, split_deb, split_cred, split_visa, RS_EC, suplier, first_date, merchant_ID)


class ClientInfo:

    def __init__(self, stonecode, split_ratio, elo_mode, liq_days, split_deb, split_cred, split_visa, RS_EC, suplier, first_date, merchant_ID):
        
        self.stonecode = stonecode
        self.split_ratio = split_ratio
        self.elo_mode = elo_mode
        self.liq_days = liq_days
        self.split_deb = split_deb
        self.split_cred = split_cred
        self.split_visa = split_visa
        self.RS_EC = RS_EC
        self.suplier = suplier
        self.first_date = first_date
        self.merchant_ID = merchant_ID

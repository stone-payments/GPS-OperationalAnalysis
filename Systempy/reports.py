from analysis import split_analysis
from failtools import errormsg, file_download, folders
from feesreport import feesreportgen
import datetime

def main():

    print(' * Downloading Split and All Sales Reports', '\n')
    weekday = datetime.date.today().weekday()
    #weekday = 0

    if weekday != 0:
        deltadi = 0
        deltadf = 2

        try:
            outputpath = '../Files/Queries/'
            split_url = 'https://banking-report-gps.stone.com.br:3443/report.csv'
            split_filepath = outputpath + 'report.csv'
            file_download(split_url,split_filepath)

            sales_url = 'https://banking-report-gps.stone.com.br:3443/all-sales-report'
            sales_filepath = outputpath + 'allsales.csv'
            file_download(sales_url,sales_filepath)

            stroutput = split_analysis(0, deltadi, deltadf)
        except:
            print('Error opening Report and All Sales files. Verify them')
            errormsg()

    else:
        j=0
        outputpath = '../Files/Queries/'
        split_url = 'https://banking-report-gps.stone.com.br:3443/report.csv'
        split_filepath = outputpath + 'report.csv'
        file_download(split_url,split_filepath)
        sales_url = 'https://banking-report-gps.stone.com.br:3443/all-sales-report'
        sales_filepath = outputpath + 'allsales.csv'
        file_download(sales_url,sales_filepath)

        for days in range(1,4,1):

            deltadi = 0 + j
            deltadf = 2 + j

            try:
                stroutput = split_analysis(0, deltadi, deltadf)

            except:
                print('Error with Report or/and All Sales file(s), verify them and queries.')
                errormsg()
            j+=1

    return

if __name__ == "__main__":
    main()


def init():
    return folders()

if __name__ == "__init__":
    initializer()


def full(daterange, deltadi):

    deltadf = 0

    outputpath = '../Files/Queries/'
    split_url = 'https://banking-report-gps.stone.com.br:3443/report.csv'
    split_filepath = outputpath + 'report.csv'
    file_download(split_url,split_filepath)

    sales_url = 'https://banking-report-gps.stone.com.br:3443/all-sales-report'
    sales_filepath = outputpath + 'allsales.csv'
    file_download(sales_url,sales_filepath)

    stroutput = split_analysis(daterange, deltadi, deltadf)

    return stroutput

if __name__ == "__full__":
    full(daterange)


def frontfees():
    feesreportgen()
    return

if __name__ == "__frontfees__":
    frontfees()

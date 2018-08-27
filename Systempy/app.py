from flask import Flask, render_template, send_file, jsonify
from failtools import foldersufix
import reports
import json
import datetime
from datetime import datetime as dt
import datetime
#import pythoncom

# ---------------------------------  START SYSTEM MODULES NEEDED TO RUN FUNCTIONS AND GETS ---------------------

app = Flask(__name__)
print(' * Creating System Folders')
reports.init()


# --------------------------------- FRONT DASHBOARD AND SPLIT ANALYSIS SITE -----------------------------------

@app.route('/split-dashboard/')
def dashboard():

    return render_template('home.html')


@app.route('/split-analysis/')
def index():

    return render_template('fails.html')


# ------------------------------- RUN MODULE ENDPOINTS - POST FUNCTIONS            --------------------

@app.route('/fails-statistics/')
def fails_statistics():

    reports.main()

    reports.frontfees()

    return index()


@app.route('/fails-statistics-full/')
def fails_statistics_full():

    daterange = int(input(' * A) Number of days before today to START analysis : '))

    deltadi = int(input(' * B) Number of days before today to END analysis (min. 1 and bigger than START): '))

    stroutput = reports.full(daterange, deltadi)

    reports.frontfees()

    return index()


# -------------------------------      SEND FILE ENDPOINTS - GET REPORTS            ---------------------------


@app.route('/reprocess-report/') #OK
def reprocess():

    analysis_date = datetime.date.today().weekday()
    if analysis_date != 0 :
        sufix = foldersufix(1)
        filepath = '../Files/Reports/' + sufix + '/Fails/reprocess_report_' + sufix + '.csv'
        filename = 'reprocess_report_' + sufix + '.csv'

    return send_file(filepath, attachment_filename=filename, as_attachment=True)


@app.route('/all-trx-report/') #OK
def alltrx():

    analysis_date = datetime.date.today().weekday()
    if analysis_date != 0 :
        sufix = foldersufix(1)
        filepath = '../Files/Reports/' + sufix + '/All/All_trx_' + sufix + '.xlsx'
        filename = 'All_trx_' + sufix + '.xlsx'

    return send_file(filepath,attachment_filename=filename, as_attachment=True)


@app.route('/fails-report/')
def failsreport():

    analysis_date = datetime.date.today().weekday()
    if analysis_date != 0 :
        sufix = foldersufix(1)
        filepath = '../Files/Reports/' + sufix + '/Fails/fails_report_' + sufix + '.csv'
        filename = 'fails_report_' + sufix + '.csv'

    return send_file(filepath,attachment_filename=filename, as_attachment=True)


@app.route('/response-json/')
def responsejson():

    analysis_date = datetime.date.today().weekday()
    if analysis_date != 0 :
        sufix = foldersufix(1)
        filepath = '../Files/Reports/' + sufix + '/Result/Analysis_Result_' + sufix + '.txt'
        filename = 'Analysis_Result_' + sufix + '.txt'

    return send_file(filepath,attachment_filename=filename, as_attachment=True)


@app.route('/van-trx-report/') #OK
def vantrx():

    analysis_date = datetime.date.today().weekday()
    if analysis_date != 0 :
        sufix = foldersufix(1)
        filepath = '../Files/Reports/' + sufix + '/Fail/fails_report_van_' + sufix + '.csv'
        filename = 'fails_report_van_' + sufix + '.xlsx'

    return send_file(filepath,attachment_filename=filename, as_attachment=True)


@app.route('/fees-report/')
def feesreport():

    sufix = foldersufix(1)
    filepath = '../Files/Fees/input-cobranca-split.csv'
    filename = 'input-cobranca-split.csv'

    return send_file(filepath,attachment_filename=filename, as_attachment=True)

'''
@app.route('/e-mail-send/')
def mailfunc():

    #recipients = 'lucas.rocha@stone.com.br'
    #body = 'Teste message body'
    #path = '..Files/all_trx.xlsx'
    #Attach file to e-mail

    pythoncom.CoInitialize()
    reports.email()

    return 'OK again'
'''




if __name__ == '__main__':
    app.run(debug=True)

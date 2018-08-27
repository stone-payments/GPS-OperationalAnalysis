import os

try:
    os.remove('../Files/Fees')
except:
    print('Cant delete Fees Folder')
try:
    print('delete Queries folder')
except:
    print('Cant delete Queries Folder')
try:
    os.remove('../Files/RAV/')
except:
    print('Cant delete RAV Folder')
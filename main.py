import sys
import requests
import json
import traceback, sys
from datetime import datetime
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSlot, QRunnable, QThreadPool, QObject,pyqtSignal
from gui import Ui_Dialog
import pandas as pd
import xlsxwriter


#for tracking progress of data download, not currently implemented
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing

    progress
        `int` indicating % progress 

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()       

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()


class MainWindow(QtWidgets.QMainWindow, Ui_Dialog, QMessageBox):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.threadpool = QThreadPool()#start thread pool
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        super(MainWindow, self).__init__(*args, **kwargs)
        #setup ui layout
        self.setupUi(self)
        #set window title
        self.setWindowTitle("SSG Scouting App")
        #event listener for button
        self.startButton.clicked.connect(self.start_button_click)
        self.clearButton.clicked.connect(self.clear_button_click)
        
        
    def print_output(self, s):
        print(s)

    #display script progress
    def progress_fn(self, n):
        print("%d%% done" % n)

    #function that is called when generate button is clicked
    def start_button_click(self):
        
        worker = Worker(self.fetchData)
        worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

        #resets input fields
    def clear_button_click(self):
        self.zipCodeInput.clear()
        self.cityInput.clear()
        self.radiusInput.clear()
        self.keywordsInput.clear()

    #display error message, not implemented yet
    def display_error_message(self):
        QMessageBox.about(self, "Title", "Message")

    #validate input, not implemented yet
    def validate_input(self):
        city_state = self.cityInput.text().strip().split(",") #get city input, strip white space
        zip = self.zipCodeInput.text().strip()#get zip, strip white space
    
        #returns "zip" if zip is selected, "city" if city is selected, -1 if both are selected
        def determineCityOrZipSearch():
            if(city_state != '' and zip == ''):
                return 0
            elif(city_state[0] == '' and zip != ''):
                return 1
            else:
                return -1
            

        #validate search limit, returns
        def validateLimit():
            limitInput = self.limitInput.text()
            if(limitInput.isdigit() == True and limitInput != None):
                limit = int(self.limitInput.text())
                if(limit > 200 or limit < 1):
                    return -1
                else:
                    return limit

        def validateZipCode():
            if(len(zip) != 5 or zip.isalpha() == True):
                return -1
            else:
                return zip

        
        def validatecity_state():
            if isinstance(city_state, list):
                if(len(city_state) == 2):
                    if(city_state[0].isalpha() == True and city_state[1].isalpha() == True):
                        return city_state
                else:
                    return -1
            else:
                return -1


        return determineCityOrZipSearch(), validateLimit(), validateZipCode(), validatecity_state()


    #not implemented yet, todo
    def determineError(self,checkedInput):
        if(checkedInput[0] != -1):
            if(checkedInput[1] != -1):
                if(checkedInput[2] != -1 and checkedInput[0] == 'zip'):
                    if(checkedInput[3] != -1):
                        return 0
                    else:
                        return 4
                else:
                    return 3
            else:
                return 2
        else:
            return 1


    def fetchData(self):
        #getting keywords from input
        keywordsArray = self.keywordsInput.text().split(',')

        #call validate input, returns list in order zipOrCity, zipCode, city, limit
        #if zip is selected, zipOrCity will return 'zip', if city is selected, will return 'city', if both are selected, will return '0'.
        validatedInput = self.validate_input()

        #assigning variables for returned functions
        city_state = validatedInput[2]
        resultLimit = 200

        city = '' #city variable to be passed to get request
        state = '' #state varaible to be passed to get request
        zipcode = self.zipCodeInput.text().strip()
        responseJsonDict = [] #where json responses will be appended

        for keyword in keywordsArray:
            self.statusOutput.setText("Retreiving data for keyword " + keyword)
            r = requests.get(url = "https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=&taxonomy_description=" + keyword + "&first_name=&use_first_name_alias=&last_name=&organization_name=&address_purpose=&city=&state=&postal_code=" + str(zipcode) + "&country_code=&limit=" + str(resultLimit) + "&skip=&version=2.1")
            data = r.json()
            responseJsonDict.append(data)

        self.wire_xlsx(responseJsonDict) 
    
    def write_xlsx(self, data):
        now = datetime.now()  # current time and date
        date_time = now.strftime("%m-%d-%Y")  # month-day-year format
        print(date_time)
        df = pd.DataFrame.from_dict(data)
        df2 = df["results"]

        practitioners = []  # List which contains the sub-lists of each potential practitioner
        for i in df2:
            if not isinstance(i, float):  # Gets around chunks of json that are not relevant
                for j in range(len(i)):
                    practitioner = []
                    practitioner.append(i[j]['basic']['name'])
                    if hasattr(df2, 'authorized_official_telephone_number'):  # Phone number is either located with 'authorized_official_telephone_number
                                                                      # or with 'telephone_number'
                        practitioner.append(i[j]['basic']['authorized_official_telephone_number'])  # Phone number
                    else:
                        practitioner.append(i[j]['addresses'][0]['telephone_number'])  # Phone number
                        practitioner.append(i[j]['addresses'][0]['address_1'])  # Address
                        practitioner.append(i[j]['addresses'][0]['city'])  # City
                        practitioner.append(i[j]['addresses'][0]['state'])  # State
                        practitioners.append(practitioner)  # Append practitioner to list of practitioners

# Creates and writes to the excel file
        with xlsxwriter.Workbook(date_time + '.xlsx') as workbook:
            worksheet = workbook.add_worksheet()

            for row, data in enumerate(practitioners):
                worksheet.write_row(row, 0, data)
        self.statusOutput.setText("Excel written")


app = QtWidgets.QApplication(sys.argv)#starting app
window = MainWindow()#open window
window.show()#show window
app.exec()#execute app

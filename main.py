import sys
import requests
import json
import traceback, sys
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSlot, QRunnable, QThreadPool, QObject,pyqtSignal
from gui import Ui_Dialog
import pandas as pd
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
        `object` data returned from processing, anything

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
class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        error_dialog = QtWidgets.QErrorMessage()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        super(MainWindow, self).__init__(*args, **kwargs)
        #setup ui layout
        self.setupUi(self)
        #set window title
        self.setWindowTitle("SSG Scouting App")
        #event listener for button
        self.startButton.clicked.connect(self.startButtonClick)
        self.clearButton.clicked.connect(self.clearButtonClick)

    def print_output(self, s):
        print(s)
        
    def thread_complete(self):
        self.statusOutput.setText("Thread Complete")
        #button click functions
    def progress_fn(self, n):
        print("%d%% done" % n)
    #function that is called when generate button is clicked
    def startButtonClick(self):
        worker = Worker(self.fetchData)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)
        #resets input fields
    def clearButtonClick(self):
        self.zipCodeInput.clear()
        self.cityInput.clear()
        self.radiusInput.clear()
        self.keywordsInput.clear()

    def fetchData(self):
        print("inside")
         #base url for requests
        keyword = ""
        zipCode = ""
            #get keywords from input
        keywordsArray = self.keywordsInput.text().split(',')
            #get zipcode from input, strip white space
        zipCode = self.zipCodeInput.text().strip()
            #get limit from input, validate
        def validateLimit():
            limit = int(self.limitInput.text())
            if(limit != None):
                if(limit > 200 or limit < 1):
                    QtWidgets.QErrorMessage.showMessage("Limit must be more than 1 and less than 200")
                else:
                    return limit
        resultLimit = validateLimit()

        responseJsonDict = []

        for keyword in keywordsArray:
            self.statusOutput.setText("Retreiving data for keyword " + keyword)
            r = requests.get(url = "https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=&taxonomy_description=" + keyword + "&first_name=&use_first_name_alias=&last_name=&organization_name=&address_purpose=&city=&state=&postal_code=" + str(zipCode) + "&country_code=&limit=" + str(resultLimit) + "&skip=&version=2.1")
            data = r.json()
            responseJsonDict.append(data)

        with open('results.json', 'w', encoding='utf-8') as f:
                json.dump(responseJsonDict, f, ensure_ascii=False, indent=4)
        df = pd.read_json('results.json')
        df.to_excel('exported_json_data.xlsx')


                   



           
        



app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()

import PyQt5
import sys
import pandas as pd
import xlsxwriter
import requests
import traceback
from pyzipcode import ZipCodeDatabase
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QObject,pyqtSignal
from ui import Ui_Dialog


'''
This class defines the available from a running worker thread
    *finished = no data
    *error = tuple
    *result = object
    *progress = int
'''
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


'''
The worker thread.
Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
'''
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()    
    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        
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
            self.signals.finished.emit()  # Done
            
            
'''
This class sets up the GUI, and contains all the methods that are available
inside of the gui.  
'''
class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        threadpool = QThreadPool() #start threadpool
        threadpool.setMaxThreadCount(20)
        self.setupUi(self)#setup GUI
        response_dict = []#where all the responses are stored


        #calls the function to write the excel file once all the threads have completed 
        def all_threads_finished():
            if self.write_excel_check.isChecked():
                write_xlsx(response_dict)
            

        #get current progress, once progress is 100%, return true
        def get_progress():
            while True:
                if self.progress_bar.value() == self.progress_bar.maximum():
                    return True


        #Moniter status of the threads
        def thread_moniter():
            worker = Worker(get_progress)
            worker.signals.finished.connect(all_threads_finished)
            threadpool.start(worker)


        #update progress bar when each thread finishes
        def update_progress_bar():
            current_value = self.progress_bar.value()
            self.progress_bar.setValue(current_value + 1)
            

        #get keywords from text file, return list
        def get_keywords_from_text():
            with open("keywords.txt","r") as keyword_text_file:
                keywords = keyword_text_file.read().splitlines()
            return keywords


        #populates keyword list, no return
        def populate_keyword_scrollarea():
            keywords = get_keywords_from_text()
            self.keyword_list_widget.addItems(keywords)


        #add keyword to text file, no return
        def add_keyword():
            with open("keywords.txt","a") as keyword_text_file:
                keyword_text_file.write("test" + "\n")
                self.keyword_list_widget.addItem("test")
                keyword_text_file.close()
                

        #remove keyword from text file, remove keyword from listbox, no return
        def remove_keyword():
            selected_keywords = self.keyword_list_widget.selectedItems()
            if not selected_keywords: return
            for key in selected_keywords:
                self.keyword_list_widget.takeItem(self.keyword_list_widget.row(key))

            lines = get_keywords_from_text()
            with open("keywords.txt", "w") as keyword_text_file:
                for line in lines:
                    for key in selected_keywords:
                        if(key.text() != line):
                            keyword_text_file.write(line + "\n")
        

        #returns string, zipcode from zipcode input field
        def get_zipcode_input():
            return self.starting_zip_input.text()
        populate_keyword_scrollarea()


        #returns int, search radius from input slider
        def get_search_radius():
            return self.radius_slider.value()


        def get_selected_search_keywords():
            selected_keywords_text = [] #return dict
            keywords = self.keyword_list_widget.selectedItems() #pull keywords from selecton
            for key in keywords:  #loop through keyword list, convert to plain text
                selected_keywords_text.append(key.text()) #use .text() to get raw text
            return selected_keywords_text #return list of raw text


        #returns list, zipcodes in radius of inputted zipcode and inputted radius
        def get_zipcodes_in_radius():
            zipcode_input = get_zipcode_input()
            radius = get_search_radius()
            zcdb = ZipCodeDatabase()
            in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius(zipcode_input, radius)] #('ZIP', radius in miles)
            return in_radius


        #takes in list of all zipcodes in radius, returns list of zipcodes with only unique first 2 digits
        def generalize_zip_codes():
            zipcodes = get_zipcodes_in_radius()
            general_zip_list = [] #initalize empty list
            general_zip_list =  [zip[0:3] + "**" for zip in zipcodes] #list comprehension
            general_zip_list = set(general_zip_list) #make a set of the data, removing duplicates
            return list(general_zip_list)


        #start threads, get data and append to response_dict.  Response is converted to json and added to an array
        def make_request(**kwargs):
            keyword = kwargs['kwargs']["keyword"]
            zipcode = kwargs['kwargs']["zip"]
            current_progress = self.progress_bar.value()
            request_url = ("https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=&taxonomy_description=" +
                 keyword + "&first_name=&use_first_name_alias=&last_name=&organization_name=&address_purpose=&city=&state=&postal_code=" +
                 str(zipcode) + "&country_code=&limit=200&skip=&version=2.1")

            r = requests.get(url = request_url)
            data = r.json()
            response_dict.append(data)
            

        #write to excel
        def write_xlsx(data):
            df = pd.DataFrame.from_dict(data)
            df2 = df["results"]
            complete_zip_list = get_zipcodes_in_radius()
            file_name = self.filename_input.text()

            customers = []  # List which contains the sub-lists of each potential customer
            for i in df2:
                if not isinstance(i, float):  # Gets around chunks of json that are not relevant
                    for j in range(len(i)):
                        customer = []
                        customer.append(i[j]['basic']['name'])
                        zipcode = i[j]['addresses'][0]['postal_code'][0:5]
                        if zipcode in complete_zip_list :
                            if hasattr(df2, 'authorized_official_telephone_number'):  # Phone number is either located with 'authorized_official_telephone_number
                                                                      # or with 'telephone_number'
                                customer.append(i[j]['basic']['authorized_official_telephone_number'])  # Phone number
                            else:
                                customer.append(i[j]['addresses'][0]['telephone_number'])  # Phone number
                            customer.append(i[j]['addresses'][0]['address_1'])  # Address
                            customer.append(i[j]['addresses'][0]['postal_code'][0:5])#zip code
                            customer.append(i[j]['addresses'][0]['city'])  # City
                            customer.append(i[j]['addresses'][0]['state'])  # State
                            customers.append(customer)  # Append customer to list of customers

            with xlsxwriter.Workbook(file_name + '.xlsx') as workbook:
                worksheet = workbook.add_worksheet()

                for row, data in enumerate(customers):
                    worksheet.write_row(row, 0, data)


        #main function, called when the generate button is pushed
        def generate_button_push():
            keywords = get_selected_search_keywords() #get search keywords
            zips = generalize_zip_codes() #get generalized zipcodes
            self.progress_bar.setMaximum(len(keywords)*len(zips))
            
            threads_total = len(keywords) * len(zips)
            thread_moniter()
            
            for keyword in keywords:
               for zipcode in zips:
                    worker = Worker(make_request, kwargs = {"keyword":keyword, "zip":zipcode})
                    worker.signals.finished.connect(update_progress_bar)
                    threadpool.start(worker)


        #updates slider value when slider is moved
        def update_slider_value():
            self.slider_radius_output.setText(str(self.radius_slider.value()) + " Miles")

            
        #signals to call fuctions from
        self.radius_slider.valueChanged.connect(update_slider_value) #call function to update slider value when slider is moved
        self.remove_item_button.clicked.connect(remove_keyword)
        self.add_item_button.clicked.connect(add_keyword)
        self.generate_button.clicked.connect(generate_button_push)


app = QtWidgets.QApplication(sys.argv)#setting up app
window = MainWindow()#load window
window.show()#show window
app.exec()#execute app

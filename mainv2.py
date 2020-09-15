import PyQt5
import sys
import pandas as pd
import xlsxwriter
import requests
import traceback
from pyzipcode import ZipCodeDatabase
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QObject,pyqtSignal
from v2 import Ui_Dialog
from second import Ui_Form
import openpyxl
from openpyxl import Workbook
from datetime import datetime
import time

'''
This class defines 
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

class TaxonomyWindow(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self, *args, obj=None, **kwargs):
        super(TaxonomyWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)#setup second window
        

        #Adds taxonomy data to taxonomy_list_widget
        def populate_listview(data):
            for code_desc in data:
                self.taxonomy_list_widget.addItem(str(code_desc))
        

        #Reads taxonomy data from taxonomy.csv
        def read_taxonomy_csv():
            df = pd.read_csv("taxonomy.csv")#read csv of taxonomy data using pandas
            #list comprehension 
            data = [[short_name,grouping,code] for short_name,grouping,code in zip(df['HPTC__ShortName'],df['HPTC__Grouping'], df['HPTC__Taxonomy'])]
            return data


        #Adds item to keyword box and keywords.txt.
        def add_item(item):
            with open("keywords.txt","a") as keyword_text_file:
                item_desc_text = item.text() #get str from item
                keyword_text_file.write(item_desc_text + '\n') #write whole line to file
                window.keyword_list_widget.addItem(item_desc_text) #write just desc to box
                keyword_text_file.close()
        
        
        #Search function called when text changed in search_box.
        def on_search_text_changed():
            text = self.search_box.text()
            for row in range(self.taxonomy_list_widget.count()):
                item = self.taxonomy_list_widget.item(row)
                if text.lower() in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
        
        #def get_shortened_name():
            
   
        #Listeners for item click, search box
        self.taxonomy_list_widget.itemActivated.connect(add_item)
        self.search_box.textChanged.connect(on_search_text_changed)

        #call the function to read the csv
        csv_data = read_taxonomy_csv()
        #populate listview with csv data
        populate_listview(csv_data)

        
            
class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        threadpool = QThreadPool() #start threadpool
        threadpool.setMaxThreadCount(20) #set max threads to 20
        self.setupUi(self)#setup main window
        response_dict = []#where all the responses are stored
        self.filename_input.setText("asdfasdf")
        


        def show_error_message(self, error):
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.setWindowTitle("Error")
            self.error_dialog.showMessage(error)


        #calls the function to write the excel file once all the threads have completed 
        def all_threads_finished():
            time.sleep(1)
            if self.write_excel_check.isChecked():
                write_xlsx(response_dict)
            

        #get current progress, once progress is 100%, return true
        def get_progress():
            while True:
                if self.progress_bar.value() == self.progress_bar.maximum():
                    self.progress_label.setText("Done")
                    return True
        
        
        #show confirmation message,
        def show_starting_message(zipcode, radius, keywords):
            answer = QtWidgets.QMessageBox.question(self, "Confirm Search", 
            "Selected paramaters for search\n" + "Zip Code: " + zipcode
            + "\nSearch Radius: " + radius
            + "\nKeywords" + keywords + "\n Is This Correct?"
            , QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

            if answer == QtWidgets.QMessageBox.Yes:
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


        #displays a text field for keyword input, returns keyword string
        def show_keyword_input_popup():
            keyword, ok = QtWidgets.QInputDialog.getText(self, 'Add a Keyword',
             'Enter a Keyword to add: ')
            if ok:
                return keyword


        #add keyword to text file, no return
        def add_keyword():
            tax_window.show()

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
            zipcode = self.starting_zip_input.text()
            if len(zipcode) != 5:
                show_error_message(self, "Please enter a valid zipcode")
                return None
            return zipcode
        

        #returns int, search radius from input slider
        def get_search_radius():
            return self.radius_slider.value()


        def get_selected_search_keywords():
            selected_keywords_text = [] #return dict
            keywords = self.keyword_list_widget.selectedItems() #pull keywords from selecton
            for key in keywords:  #loop through keyword list, convert to plain text
                current_key = key.text() #use .text() to get raw text
                split_keyword = current_key.split(",")
                split_keyword = split_keyword[0]
                selected_keywords_text.append(split_keyword[2:-1])
            if keywords == []:
                show_error_message(self, "At least one keyword needs to be selected.")
                return None
            return selected_keywords_text #return list of raw text
            

        #returns list, zipcodes in radius of inputted zipcode and inputted radius
        def get_zipcodes_in_radius():
            zipcode_input = get_zipcode_input() #getting zipcode from input
            if not zipcode_input:
                return None
            radius = get_search_radius() #getting radius from input
            zcdb = ZipCodeDatabase() #using zipCodeDatabase
            try:
                in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius(zipcode_input, radius)] #('ZIP', radius in miles)
                return in_radius
            except Exception: #catch when zipcode is not found in database
                show_error_message(self, "Inputted zipcode was not found")


        #takes in list of all zipcodes in radius, returns list of zipcodes with only unique first 2 digits
        def generalize_zip_codes():
            zipcodes = get_zipcodes_in_radius()
            if not zipcodes:
                return None
            general_zip_list = [] #initalize empty list
            general_zip_list =  [zip[0:3] + "**" for zip in zipcodes] #list comprehension
            general_zip_list = set(general_zip_list) #make a set of the data, removing duplicates
            return list(general_zip_list)



        #start threads, get data and append to response_dict.  Response is converted to json and added to an array
        def make_request(**kwargs):
            keyword = kwargs['kwargs']["keyword"]
            zipcode = kwargs['kwargs']["zip"]
            self.progress_label.setText("Keyword: " + keyword)
            
            current_progress = self.progress_bar.value()
            request_url = ("https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=&taxonomy_description=" +
                 keyword + "&first_name=&use_first_name_alias=&last_name=" +
                 "&organization_name=&address_purpose=&city=&state=&postal_code=" +
                 str(zipcode) + "&country_code=&limit=200&skip=&version=2.1")
            r = requests.get(url = request_url)
            data = r.json()
            response_dict.append(data)


        #write to excel
        def write_xlsx(data):
            df = pd.DataFrame.from_dict(data)
            complete_zip_list = get_zipcodes_in_radius()

            file_name = self.filename_input.text()
            if hasattr(df, "results"):
                df2 = df["results"]
                
            practitioners = []  # List which contains the sub-lists of each potential customer
            for i in df2:
                if not isinstance(i, float):  # Gets around chunks of json that are not relevant
                    for j in range(len(i)):
                        practitioner = []
                        practitioner.append(i[j]['basic']['name'])
                        # practitioner.append(i[j]['basic']['name'])
                        if hasattr(df2, 'authorized_official_telephone_number'):  # Phone number is either located with 'authorized_official_telephone_number
                                                                                # or with 'telephone_number'
                            practitioner.append(i[j]['basic']['authorized_official_telephone_number'])  # Phone number
                        else:
                            practitioner.append(i[j]['addresses'][0]['telephone_number'])  # Phone number
                        location = i[j]['addresses'][0]['address_1'] + ", " + i[j]['addresses'][0]['city'] + ", " + i[j]['addresses'][0]['state']
                        zipcode = i[j]['addresses'][0]['postal_code']
                        zipcode = zipcode[0:5]
                        location += (" " + zipcode)
                        practitioner.append(location)
                        taxonomie = len(i[j]['taxonomies'])
                        descs = ''
                        codes = ''
                        for k in range(taxonomie):
                            code = (i[j]['taxonomies'][0]['code'])
                            desc = (i[j]['taxonomies'][0]['desc'])
                            if code not in codes:
                                codes += code

                            if desc not in descs:
                                descs += desc
             
                        practitioner.append(descs)
                        practitioner.append(codes)
                        in_list = False

                        for m in range(len(practitioners)):
                            if practitioner[1] in practitioners[m] and practitioner[2] in practitioners[m]:
                                in_list = True

                        if not in_list and zipcode in complete_zip_list:
                            practitioners.append(practitioner)  # Append customer to list of customers

            with xlsxwriter.Workbook(file_name + '.xlsx') as workbook:
                worksheet = workbook.add_worksheet()
                for row, data in enumerate(practitioners):
                    worksheet.write_row(row, 0, data)
        

        def create_map():
            file_name = self.filename_input.text()






        #main function, called when the generate button is pushed
        def generate_button_push():
            zipcode_input = get_zipcode_input()#get zipcode input for verifiction popup
            range_input = get_search_radius()#get search radius for popup
            keywords = get_selected_search_keywords() #get search keywords for requests
            zips = generalize_zip_codes() #get generalized zipcodes for requests, returns none if empty or invalid
            
            
            if keywords and zips:
                confirm_input = show_starting_message(zipcode_input , str(range_input), str(keywords)) #show popup, return true if confirmed
                if confirm_input:
                    threads_total = len(keywords) * len(zips) #number of total threads to be ran
                    self.progress_bar.setMaximum(threads_total)#set progress bar maximum to total threads to be ran
                    thread_moniter() #start thread moniter, when threads are done, excel will be written

                    for keyword in keywords:#iterate through keywords
                        for zipcode in zips:#iterate through generalized zips
                            worker = Worker(make_request, kwargs = {"keyword":keyword, "zip":zipcode})#new thread for each zip, keyword
                            worker.signals.finished.connect(update_progress_bar)#update progress bar when thread is complete
                            threadpool.start(worker)#start thread


        #called when the reset button is pushed
        def reset_button_push():
            self.starting_zip_input.clear()
            self.radius_slider.setValue(1)
            self.keyword_list_widget.clearSelection()
            self.progress_bar.setValue(0)
            self.progress_label.clear()
            set_filename_and_slider()
        
        #updates slider value when slider is moved
        def update_slider_value():
            self.slider_radius_output.setText(str(self.radius_slider.value()) + " Miles")#update label with slider value

        #set the filename input field to the current datetime
        def set_filename_and_slider():
            now = datetime.now()
            self.filename_input.setText(now.strftime(("%d-%m-%Y-%H-%M-%S")))
            self.radius_slider.setValue(50)
            update_slider_value()
        
       
        #set initial filename
        set_filename_and_slider()

        populate_keyword_scrollarea()#call function to populate keyword area
        #signals to call fuctions from

        #call function to update slider value when slider is moved
        self.radius_slider.valueChanged.connect(update_slider_value) 

        #call function to remove keyword on button press
        self.remove_item_button.clicked.connect(remove_keyword)

        #call function to add keyword on button press
        self.add_item_button.clicked.connect(add_keyword)

        #call function to start main operations on generate button press
        self.generate_button.clicked.connect(generate_button_push)

        #call reset function on button click
        self.reset_button.clicked.connect(reset_button_push)


app = QtWidgets.QApplication(sys.argv)#starting app
window = MainWindow()#open window
window.show()#show window
tax_window = TaxonomyWindow()
app.exec()#execute app

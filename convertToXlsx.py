from datetime import datetime
import pandas as pd
import xlsxwriter

now = datetime.now()  # current time and date
date_time = now.strftime("%m-%d-%Y")  # month-day-year format
print(date_time)
df = pd.read_json("results.json")
df2 = df["results"]

customers = []  # List which contains the sub-lists of each potential customer
for i in df2:
    if not isinstance(i, float):  # Gets around chunks of json that are not relevant
        for j in range(len(i)):
            customer = []
            customer.append(i[j]['basic']['name'])
            if hasattr(df2, 'authorized_official_telephone_number'):  # Phone number is either located with 'authorized_official_telephone_number
                                                                      # or with 'telephone_number'
                customer.append(i[j]['basic']['authorized_official_telephone_number'])  # Phone number
            else:
                customer.append(i[j]['addresses'][0]['telephone_number'])  # Phone number
            customer.append(i[j]['addresses'][0]['address_1'])  # Address
            customer.append(i[j]['addresses'][0]['city'])  # City
            customer.append(i[j]['addresses'][0]['state'])  # State
            customers.append(customer)  # Append customer to list of customers

# Creates and writes to the excel file
with xlsxwriter.Workbook(date_time + '.xlsx') as workbook:
    worksheet = workbook.add_worksheet()

    for row, data in enumerate(customers):
        worksheet.write_row(row, 0, data)

import numpy as n
from datetime import datetime
from datetime import timedelta
import csv

# RETURN DATA GREATER THEN PAST N DAYS
def get_data_at_len(data, days):
    # GET CURRENT DATE
    tod = datetime.now()
    # MINUS DAYS INPUTTED
    d = timedelta(days=days)
    to_compare = tod - d
    # FORMAT
    format = '%Y-%m-%d'
    # SET RETURN DATA
    to_return = []
    # ITERATE DATA
    for row in data[1:]:
        # GET DATE OF DATA
        cur_date = datetime.strptime(row[0], format)
        # IF IN OUR DATE RANGE
        if cur_date > to_compare:
            # IF THE OPEN DATA IS MISSING
            if row[1] == str(0):
                # APPEND HIGH PRICE
                to_return.append(float(row[2]))
            else:
                # APPEND OPEN PRICE
                to_return.append(float(row[1]))
    return to_return


# GET DATA FROM CSV FILE
def stock_open_data(stock_file_name):
    # SET LIST
    open_data = [stock_file_name]
    # SET PATH
    stock_file = 'staging/' + stock_file_name
    # OPEN FILE
    with open(stock_file, 'r') as file:
        reader = csv.reader(file)
        all_rows = list(reader)
        # ITERATE THROUGH DATA
        for line in all_rows[1:]:
            # APPEND OPEN DATA
            open_data.append(line)
    # RETURN OPEN DATA
    return open_data


# SETS THE DATA LENGTH TO BE THE SAME FOR ALL CSV FILES
def corr_max_data(data1, data2):
    if len(data1) < len(data2):
        data2 = data2[:len(data1)]
    else:
        data1 = data1[:len(data2)]

    corr = n.corrcoef(data1,data2)

    return corr[0][1]


# calculate the risk of a portfolio with two stocks
def two_stock_portfolio_risk(w1, w2, sd1, sd2, cor):

    sd = n.square(w1) * n.square(sd1) + n.square(w2) * n.square(sd2) + (2.0 * w1 * w2 * cor * sd1 * sd2)

    print('SD^2 = ', n.abs(sd))

    return n.sqrt(sd)


# calculates risk of 3 stock portfolio
def three_stock_portfolio_risk(w1, w2, w3, sd1, sd2, sd3, cor1_2, cor2_3, cor1_3):

    sd = (n.square(w1) * n.square(sd1)) + (n.square(w2) * n.square(sd2)) + (n.square(w3) * n.square(sd3)) + \
         (2 * w1 * w2 * cor1_2 * sd1 * sd2) + (2 * w2 * w3 * cor2_3 * sd2 * sd3) + (2 * sd1 * sd3 * cor1_3 * sd1 * sd3)

    print('SD^2 = ', n.abs(sd))

    return n.sqrt(n.abs(sd))

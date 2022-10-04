import os
import csv
import time
import math
from os.path import exists
import more_itertools as it
from collections import Counter
import folders_processing as fp
import yahoo_finance_scraper as yfs
from functions import get_data_at_len, stock_open_data

########################################################################################################################


# TICKERS TO USE WITH THE CALCULATOR
Tickers = ['NVDA', 'BIP', 'LCFS.TO', 'DKS', 'HCA', 'GNRC', 'AVNW']

# IF YOU BOUGHT STOCKS ALREADY AND THEY'RE IN YOUR PORTFOLIO THEN YOU CAN ADD THEM HERE:
Current_Stock_Amount = [['NVDA', 2],
                        ['BIP', 4],
                        ['LCFS.TO', 14]]

# YOUR CURRENT PORTFOLIO BALANCE (CASH + STOCK VALUE)
Total_Portfolio_Balance = 1871.75

# RANGE TO COVER IN STAGING DATA (PREVIOUS 'N' DAYS)
Day_Range = 100

# SET SCRAPE TO TRUE TO SCRAPE DATA FROM YAHOO
scrape = True


########################################################################################################################

start_time = time.process_time()


# CLEARS ALL DOWNLOADED DATA
def clear_cwd():
    directory = os.path.dirname(__file__)
    data = directory + r'\data'
    staging = directory + r'\staging'

    for file_name in os.listdir(data):
        os.remove(data + '/' + file_name)

    for file_name in os.listdir(staging):
        os.remove(staging + '/' + file_name)


# GET CURRENT PRICES
def get_current_prices():
    cur_prices = []
    # IF WEIGHTS IS LEFT EMPTY THEN WE CALCULATE POSSIBLE WEIGHTS

    # GET CURRENT STOCK PRICE FOR EACH TICKER
    for csv_name in os.listdir('C:/Users/fcroasdale/PycharmProjects/Portfolio Risk Calculator/staging'):
        with open('C:/Users/fcroasdale/PycharmProjects/Portfolio Risk Calculator/staging/{}'.format(csv_name),
                  'r') as csv_open:
            reader = csv.reader(csv_open)
            all_rows = list(reader)

            cur_price_to_append = ''.join(all_rows[-1][1])
            ticker_to_append = ''.join(csv_name.split('.csv')[0])

            cur_prices.append([ticker_to_append, round(float(cur_price_to_append), 2)])
    return cur_prices


# SET CWD
directory = os.path.dirname(__file__)
datadir = directory + r'\data'
staging = directory + r'\staging'

# IF USER WANTS TO SCRAPE DATA AGAIN THEN
if scrape:
    # CLEAR DATA
    clear_cwd()
    # SCRAPE
    yfs.download_csv(Tickers)
    print('Done.')
else:
    yfs.close()

# GET UNALTERED BALANCE
total_port_balance_unaltered = Total_Portfolio_Balance

# GET CURRENT STOCK PRICES
cur_prices = get_current_prices()

# NOW HERE WE ARE ASSUMING THAT WE WANT AT LEAST ONE OF EACH STOCK AND WE NEED TO CHECK FOR STOCK ALREADY IN OUR
# PORTFOLIO INPUTTED BY THE USER IN (CURRENT STOCK AMOUNT)
in_both = []
for stock_value in cur_prices:
    # BUT WE ALSO KNOW THAT WE MIGHT ALREADY HAVE ONE TICKER
    # SO WE MUST SUBTRACT THAT FROM OUR TOTAL BALANCE
    for bought_in_stock in Current_Stock_Amount:
        if stock_value[0] == bought_in_stock[0]:
            Total_Portfolio_Balance -= bought_in_stock[1] * stock_value[1]
            stock_value.append(bought_in_stock[1])
            in_both.append(stock_value[0])

    if stock_value[0] not in in_both:
        stock_value.append(1)
        Total_Portfolio_Balance -= stock_value[1]

# DIVIDE THE TOTAL BALANCE BY EACH STOCK PRICE TO GET THE MAXIMUM AMOUNT OF STOCK WE COULD POSSIBLY BUY FOR THAT STOCK
# AND ROUND OFF TO AN INTEGER
for stock_value in cur_prices:
    maximum_stock_buy = math.trunc(Total_Portfolio_Balance / stock_value[1])
    stock_value.append(int(maximum_stock_buy))

# FOR EACH TICKER (WE WILL ADD EACH STOCK BY TICKER IN ORDER UNTIL WE REACH OUR MAX AMOUNT) AND THEN ADD THE
# STOCK AND TICKER TO A LIST TIMES THAT INTEGER THAT WILL GIVE US THE MAXIMUM AMOUNT OF STOCK BUYS FOR THAT STOCK
stock_price_combinations_list = []
for stock_data in cur_prices:
    for copy_cur in range(0, int(math.trunc(stock_data[3]))):
        stock_price_combinations_list.append(stock_data)

c = int(len(stock_price_combinations_list))

# IF WE HAVEN'T ALREADY CALCULATED POSSIBLE COMBINATIONS
if not exists(datadir + r'\possible_combinations.csv'):
    # NOW WE ACTUALLY CALCULATE ALL THE POSSIBLE COMBINATIONS
    possible_weights = []
    print('Calculating weights...')
    # WHILE WE DO NOT CHOOSE 0
    while c != 0:
        # START A TIMER TO MEASURE CALC TIME
        tic = time.process_time()
        # GET ALL COMBINATIONS OF THOSE PRICES THAT ARE CLOSE TO EQUAL OUR BALANCE AMOUNT
        all_combinations = it.distinct_combinations(stock_price_combinations_list, c)
        # ITERATE THROUGH EACH COMBINATION AND GET THE SUM OF IT
        for cur_combination in all_combinations:
            # SET SUM
            sum = 0
            # SET TO_APPEND
            stock_to_append = []
            # FOR EACH STOCK IN OUR POSSIBLE COMBINATION
            for cur_stock in cur_combination:
                # ADD THE SUM
                sum += round(cur_stock[1], 2)
                # IF THE SUM IS GREATER THEN OUR AVAILABLE PORTFOLIO BALANCE
                if sum > Total_Portfolio_Balance:
                    # ADD THE STOCKS BEFORE THAT SUM
                    # possible_weights.append(stock_to_append)
                    # BREAK OUT OF THE LOOP AND GO TO NEXT COMBINATION
                    break
                if cur_combination.index(cur_stock) == len(cur_combination) - 1:
                    possible_weights.append(stock_to_append)

                # APPEND THE STOCK TO KEEP TRACK OF OUR SUM
                stock_to_append.append(cur_stock[0])

        # PRINT PROCESSING TIME
        toc = time.process_time()
        print('TIME OF PROCESS:', toc - tic)
        # ITERATE C
        c = c - 1

    possible_weights_clean = []
    # CLEAN THE DATA
    for row in possible_weights:
        counts = Counter(row)
        to_append_counts = ()

        # ITERATE THE DICTIONARY
        for key in counts:
            # APPEND THE KEY AND THE VALUE
            to_append_counts += (key, counts[key])
        # APPEND THE DATA TO POSSIBLE WEIGHTS
        possible_weights_clean.append(to_append_counts)

    possible_weights_clean = list(set(possible_weights_clean))

    # OPEN THE FILE AND WRITE CLEAN DATA
    with open(datadir + r'\possible_combinations.csv',
              'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        headers = []
        for cur_stock_data in cur_prices:
            headers.append(cur_stock_data[0])

        # WRITE HEADERS
        writer.writerow(headers)

        # ITERATE EACH ROW OF OUR DATA
        for row in possible_weights_clean:
            to_write = list(len(Tickers) * ('',))
            # FIND THE POSITION OF THE NUMBER OF STOCKS FOR THAT COMBINATION
            c = 0
            for ticker in cur_prices:
                if ticker[0] in row:
                    # SET INDEX FOR READABILITY
                    index_of_number_from_csv = c
                    # GET INDEX OF VALUE FROM ROW
                    index_of_data = row.index(ticker[0]) + 1
                    # SET THE POSITION OF THE NUMBER TO THE DATA
                    to_write[index_of_number_from_csv] = row[index_of_data] + ticker[2]
                else:
                    # ELSE BECAUSE WERE ASSUMING THAT WERE HAVING AT LEAST ONE OF EACH STOCK WE MUST REFLECT THAT IN
                    # OUR DATA
                    to_write[c] = 1
                c += 1
            writer.writerow(to_write)

    # OPEN THE FILE AND GET THE DATA
    with open(datadir + r'\possible_combinations.csv',
              'r') as csv_file:
        reader = csv.reader(csv_file)
        # READ INTO LIST
        possible_weights = list(reader)

# ELSE IF POSSIBLE COMBINATIONS WAS ALREADY CALCULATED
else:
    # OPEN THE FILE
    with open(datadir + r'\possible_combinations.csv',
              'r') as csv_file:
        reader = csv.reader(csv_file)
        # READ INTO LIST
        possible_weights = list(reader)

# NOW WE MUST CALCULATE THE RISK FOR EACH COMBINATION KEEPING IN MIND THAT WE MIGHT HAVE MADE THE ASSUMPTION
# THAT WE ARE AT LEAST BUYING ONE STOCK OF EACH TICKER GIVEN
if not exists(
        datadir + r'\possible_combinations_combined.csv'):
    # OPEN THE FILE AND WRITE PERCENTAGE OF THE WEIGHTS
    with open(
            datadir + r'\possible_combinations_combined.csv',
            'w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)

        # WRITE HEADERS
        headers = possible_weights[0].copy()
        for ticker_header in possible_weights[0]:
            headers.append(ticker_header + '_weights')
        headers.append('CASH')
        writer.writerow(headers)

        # ITERATE THROUGH DATA
        for row in possible_weights[1:]:
            c = 0
            sum = 0
            to_append = row.copy()
            for volume in row:
                # AND THEN CONVERT TO WEIGHTS
                weight = (int(volume) * cur_prices[c][1]) / total_port_balance_unaltered * 100
                to_append.append(weight)
                sum += weight
                c += 1

            to_append.append(100 - sum)
            writer.writerow(to_append)

# OPEN THE FILE AND WRITE PERCENTAGE OF THE WEIGHTS
with open(
        datadir + r'\possible_combinations_combined.csv',
        'r', newline='', encoding='UTF-8') as csv_file:
    reader = csv.reader(csv_file)
    data = list(reader)
# SET TIC FOR START OF PROCESSING TIME
tic = time.process_time()
# GET THE CSV FILES FROM OUR PORTFOLIO FOLDER
csv_list = []
for csv_name in os.listdir(staging):
    # APPEND THE DATA THAT IS IN OUR TICKERS
    if csv_name.split('.csv')[0] in Tickers:
        to_append = get_data_at_len(stock_open_data(csv_name), Day_Range)
        csv_list.append(to_append)

# CALCULATE RISK
data_final = []
# FOR EACH CALCULATED WEIGHT IN OUR CSV FILE

print('Calculating Risk...')
for row in data[1:]:
    # GET THE RISK IN OUR DATE RANGE
    risk = fp.total_risk(row[len(Tickers):2 * len(Tickers)], csv_list)
    # COPY THE ROW
    row_copy = row.copy()
    # APPEND THE RISK VALUE FOR THOSE POSSIBLE WEIGHTS
    row_copy.append(risk)
    # APPEND THE ROW TO OUR DATA
    data_final.append(row_copy)
# PRINT THE PROCESSING TIME
toc = time.process_time()
print('TIME OF PROCESS:', toc - tic)

# OPEN FINAL DATA CSV
with open(datadir + r'/final_data.csv',
          'w', newline='', encoding='UTF-8') as csv_file:
    writer = csv.writer(csv_file)
    # WRITE HEADER
    header = data[0].copy()
    header.append('RISK')
    writer.writerow(header)
    # ITERATE THROUGH DATA AND WRITE TO CSV
    for row in data_final:
        writer.writerow(row)
end_time = time.process_time()

print('TOTAL CALCULATOR PROCESS TIME: ', end_time - start_time)

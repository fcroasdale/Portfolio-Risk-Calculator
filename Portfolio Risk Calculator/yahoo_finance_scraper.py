import csv
import selenium
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import time as t
from csv import writer
import shutil
import os
import datetime
from datetime import date
import shutil

#######################################################################################################################


chrome_options = Options()
chrome_options.add_argument("--disable-extensions")


#######################################################################################################################

# chrome path
driver = webdriver.Chrome(executable_path=r"C:\Users\fcroasdale\PycharmProjects\Portfolio Risk Calculator\chromedriver",
                          options=chrome_options)


#######################################################################################################################

# action = ActionChains(driver)

# select max on dropdown
def get_recent():
    t.sleep(3)
    # click dropdown
    driver.find_element(By.XPATH,
                        '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div[1]').click()
    t.sleep(1)
    # select max
    driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/ul[2]/li[4]/button').click()
    t.sleep(2)
    # hit apply
    driver.find_element(By.XPATH,
                        '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()


# scrape most recent data entry
def scrape_text_one():
    data = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]')))
    data = data.text
    # clean data
    data = data.replace(',', '')
    data = data.split(' ')
    # get time
    time = str(date.today())
    data[1] = time
    if data[8] == '-':
        data[8] = ''
    return data


# return bool if element is on screen
def element_completely_viewable(driver, elem):
    elem_left_bound = elem.location.get('x')
    elem_top_bound = elem.location.get('y')
    elem_width = elem.size.get('width')
    elem_height = elem.size.get('height')
    elem_right_bound = elem_left_bound + elem_width
    elem_lower_bound = elem_top_bound + elem_height

    win_upper_bound = driver.execute_script('return window.pageYOffset')
    win_left_bound = driver.execute_script('return window.pageXOffset')
    win_width = driver.execute_script('return document.documentElement.clientWidth')
    win_height = driver.execute_script('return document.documentElement.clientHeight')
    win_right_bound = win_left_bound + win_width
    win_lower_bound = win_upper_bound + win_height

    return all((win_left_bound <= elem_left_bound,
                win_right_bound >= elem_right_bound,
                win_upper_bound <= elem_top_bound,
                win_lower_bound >= elem_lower_bound)
               )


# scroll the page down
def scroll_down():
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    print('last_height', last_height)
    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        WebDriverWait(driver, 30).until(lambda d: d.execute_script(
            'return (document.readyState == "complete" || document.readyState == "interactive")'))
        t.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        print('new_height', new_height)

        if new_height == last_height:

            break

        last_height = new_height


# scrape most recent data entry
def scrape_text():
    # element = driver.find_elements(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody')
    # element = element[-1]
    ele = driver.find_element('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tfoot/tr/td/span[2]')

    # not element_completely_viewable(driver, element)
    while not element_completely_viewable(driver, ele):
        # scroll_down()
        # action.send_keys(Keys.PAGE_DOWN).perform()
        print('ran')

        """    
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

        element = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions) \
            .until(EC.visibility_of_element_located((By.XPATH, ele_path)))

        element = driver.find_elements(By.XPATH,
                                       ele_path)
        element = element[-1]"""


    print('stopped')
    t.sleep(10000)

    data = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]')))

    print('-----STOP-----')
    t.sleep(100000)
    data = data.text
    # clean data
    data = data.replace(',', '')
    data = data.split(' ')

    # get time
    time = str(date.today())
    data[1] = time
    if data[8] == '-':
        data[8] = ''
    return data


"""
# not element_completely_viewable(driver, element)
while True:
    coordinates = element.location_once_scrolled_into_view  # returns dict of X, Y coordinates
    driver.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    t.sleep(2)
"""


# steps to download csv HAS TO BE ON THE HISTORIC DATA PAGE
def yahoo_download():
    get_recent()
    t.sleep(5)
    # hit downlaod
    driver.find_element(By.XPATH,
                        '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a/span').click()


# closes webdriver
def close():
    driver.quit()


# get address for ticker
def get_data(ticker):
    # search ticker symbol
    driver.get('https://ca.finance.yahoo.com/quote/{}/history'.format(ticker))

    # if there are no results
    return driver.find_element(By.XPATH, '//*[@id="atomic"]/head/title').text != "Requested symbol wasn't found"


# get data from yahoo csv download links
def download_csv(symbols):
    for ticker in symbols:
        print('Scraping...', ticker)

        if get_data(ticker):
            get_recent()
            driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a').click()
        t.sleep(2)
        shutil.move('C:/Users/fcroasdale/Downloads/{}.csv'.format(ticker),
                    'C:/Users/fcroasdale/PycharmProjects/Portfolio Risk Calculator/staging')

    driver.quit()


# get data by element scraping
def element_scrape(all_rows, symbols):
    # get data
    for ticker in symbols:
        if '^' in ticker:
            ticker = ticker.replace('^', '%5E')
        if '=' in ticker:
            ticker = ticker.replace('=', '%3D')

        # if ticker found
        if get_data(ticker):
            # select most recent data
            get_recent()
            # get data
            data = scrape_text()
            data_day = data[1][8:10]
            cur_day = str(datetime.datetime.now().day)

            if data_day == cur_day:
                if '%5E' in ticker:
                    ticker = ticker.replace('%5E', '^')
                if '%3D' in ticker:
                    ticker = ticker.replace('%3D', '=')
                data[2] = ticker
                # append
                all_rows.append(data)
        else:
            print(ticker, ': NOT FOUND CHECK TICKER SYMBOL')
    driver.quit()


# transform csv
def transform_csv(source, target, ticker):
    with open(source, 'r') as infile, \
            open(target, 'w', newline='', encoding='UTF-8') as outfile:
        # get data
        all_rows = list(infile)
        lines = len(all_rows)

        print(lines)

        infile = csv.reader(infile)
        # set writer
        outfile = writer(outfile)
        # for each row
        header = 1
        c = 0
        for row in all_rows:
            c += 1
            if 'null' not in row and header == 0 and c == lines:
                to_write = row.strip('\n')
                to_write = to_write.split(',')
                to_write.insert(1, ticker)
                outfile.writerow(to_write)
                print('i ran')
            if header == 1:
                to_write = row.strip('\n')
                # write the header
                to_write = to_write.split(',')
                to_write.insert(1, 'Ticker')
                # row.insert(6, 'Volume')
                outfile.writerow(to_write)
                header -= 1
                print(to_write)


# send data to csv file
def data_to_csv(all_rows):
    with open(r'C:\Users\fcroasdale\PycharmProjects\Portfolio Risk Calculator\staging\ticker_data.csv', 'w', newline='',
              encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        headers = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close*', 'Adj Close**', 'Volume']
        writer.writerow(headers)

        for row in all_rows:
            writer.writerow(row[1:])


"""# set data
data = []
# scrape data
element_scrape(data, tickers)
# put into csv
data_to_csv(data)"""

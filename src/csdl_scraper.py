from pathlib import Path
from time import sleep
import pandas as pd
import datetime

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# defining directory
dir_path = Path(__file__).resolve().parents[1]
raw_data_path = dir_path.joinpath("data", "raw", "csdl")
if not raw_data_path.exists():
    raw_data_path.mkdir(parents=True)

cash_mkt_folder = raw_data_path.joinpath("cash_mkts")
if not cash_mkt_folder.exists():
    cash_mkt_folder.mkdir(parents=True)

otc_folder = raw_data_path.joinpath("in_otc")
if not otc_folder.exists():
    otc_folder.mkdir(parents=True)


# an empty placeholder dataset to store dates whwere html parsing fails and another file to remember all scraped dates and no data cases
missing_dates_df = raw_data_path.joinpath("missing_dates.csv")

scraped_dates_df = raw_data_path.joinpath("scraped_dates.csv")

no_data_dates_df = raw_data_path.joinpath("no_data_dates.csv")


def driver_generate():
    """A function to initiate the driver"""
    driver = webdriver.Edge()
    return driver


def otc_mkt_selector(driver):
    """A function which clicks the necessary radio button to isolate results from OTC markets"""
    sleep(2)

    cash_radio = driver.find_element(By.XPATH, '//input[@id="customRadioInline2"]')
    driver.execute_script(f"arguments[0].click()", cash_radio)
    sleep(2)


def cash_mkt_selector(driver):
    """A function which clicks the necessary radio button to isolate results from cash markets"""
    sleep(2)

    cash_radio = driver.find_element(By.XPATH, "//input[@id='customRadioInline1']")
    driver.execute_script(f"arguments[0].click()", cash_radio)
    sleep(2)


def calendar_selector(driver, date: str):
    """A function which selects the required dates and provides the form inputs"""
    sleep(2)

    cal_image = driver.find_element(By.XPATH, "//div[@class='ui input left icon']")
    driver.execute_script(f"arguments[0].click()", cal_image)
    sleep(1)

    cal_input = driver.find_element(By.XPATH, "//input[@id='idtradedate']")
    driver.execute_script(f"arguments[0].value = '{date}'", cal_input)

    sleep(2)


def second_mkt_selector(driver, activate: bool):
    if activate:
        mkt_selection = Select(
            driver.find_element(By.XPATH, "//select[@id='markettype_select']")
        )

        driver.find_element(By.XPATH, "//select[@id='markettype_select']").click()

        sleep(1)
        mkt_selection.select_by_value("S")
        sleep(2)


def submit_form(driver):
    """A function which accepts the input date and submits the form"""
    search_button = driver.find_element(By.XPATH, "//input[@id='btnsearch']")
    driver.execute_script(f"arguments[0].click()", search_button)

    sleep(2)


def extract_table(driver):
    """A function whicg identifies the necessary rables and outputs its outerHTML"""
    data_tables = driver.find_elements(By.XPATH, "//table[@id='tbl']")
    sleep(2)
    data_list = [
        pd.read_html(frame.get_attribute("outerHTML")) for frame in data_tables
    ]

    return data_list


def data_exporter(data: list, market: str, date: str):
    """A function which is inspects each dataset and places it accordingly in the respective directories within the raw data folder"""

    try:
        df = pd.DataFrame(data[0][0])

        if market == "cash":
            df_path = cash_mkt_folder.joinpath(f"{date}.csv")

        elif market == "otc":
            df_path = otc_folder.joinpath(f"{date}.csv")

        print(df_path)
        if not df_path.exists():
            df.to_csv(df_path, index=False)

        else:
            print(f"File exists for {date}. Aborting export!!!")

    except UnboundLocalError:
        try:
            miss_df = pd.read_csv(missing_dates_df)
            df2 = pd.DataFrame({"missing_dates": [date]})
            miss_df = pd.concat([miss_df, df2], axis=0)
            miss_df.to_csv(missing_dates_df, index=False)
        except FileNotFoundError:
            miss_df = pd.DataFrame({"missing_dates": [date]})
            miss_df.to_csv(missing_dates_df, index=False)

    except IndexError:
        try:
            no_data_df = pd.read_csv(no_data_dates_df)
            df2 = pd.DataFrame({"missing_dates": [date]})
            no_data_df = pd.concat([no_data_df, df2], axis=0)
            no_data_df.to_csv(no_data_dates_df, index=False)
        except FileNotFoundError:
            no_data_df = pd.DataFrame({"missing_dates": [date]})
            no_data_df.to_csv(no_data_dates_df, index=False)


def date_builder():
    """A function which creates a list week days between the spoecified start and end dates."""
    # initializing date
    start_date = datetime.datetime.strptime("01-07-2016", "%d-%m-%Y")
    end_date = datetime.datetime.strptime("27-10-2023", "%d-%m-%Y")

    date_generated = pd.date_range(start_date, end_date, freq="B")
    date_list = date_generated.strftime("%B %d, %Y")
    date_list = [str(date.replace(" 0", " ")) for date in date_list]

    try:
        scraped_dates = pd.read_csv(scraped_dates_df)

        date_list = [
            date
            for date in date_list
            if date not in scraped_dates["scraped_dates"].unique()
        ]

        return date_list

    except FileNotFoundError:
        print("No dates have been scraped. So, date filter need not be implemented")

        return date_list


def date_ignorer(date: str):
    try:
        df = pd.read_csv(scraped_dates_df)
        df2 = pd.DataFrame({"scraped_dates": [date]})
        df = pd.concat([df, df2], axis=0)
        df.to_csv(scraped_dates_df, index=False)

    except FileNotFoundError:
        df = pd.DataFrame({"scraped_dates": [date]})
        df.to_csv(scraped_dates_df, index=False)


def run_scraper(driver, market: str, activate_secondary: bool):
    dates = date_builder()

    for date in dates:
        # adding the date
        calendar_selector(driver, date)

        # selecting only secondary market
        second_mkt_selector(driver, activate=activate_secondary)

        # submitting form with date
        submit_form(driver)

        # capturing output table
        dfs = extract_table(driver)

        # cleaning the extrcated datasets
        data_exporter(data=dfs, market=market, date=date)

        # marking scraped dates
        date_ignorer(date)


def scrape():
    """A function that compiles and initiates all the pre-defined functions to scrape, parse and export secondary bond market information from the CSDL aspx dashboard."""

    driver = driver_generate()

    url = "https://www.cdslindia.com/CorporateBond/CorporateBondReports.aspx"

    driver.get(url)

    # selecting markets
    # for scraping otc market, uncomment the following and run
    # otc_mkt_selector(driver)
    # run_scraper(driver=driver, market="otc", activate_secondary=False)

    # for scraping cash market, uncomment the following and run
    cash_mkt_selector(driver)
    run_scraper(driver=driver, market="cash", activate_secondary=True)


scrape()

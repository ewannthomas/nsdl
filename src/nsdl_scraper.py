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
raw_data_path = dir_path.joinpath("data", "raw")
if not raw_data_path.exists():
    raw_data_path.mkdir(parents=True)

cap_mkt_folder = raw_data_path.joinpath("in_cap_mkts")
if not cap_mkt_folder.exists():
    cap_mkt_folder.mkdir(parents=True)

otc_folder = raw_data_path.joinpath("in_otc")
if not otc_folder.exists():
    otc_folder.mkdir(parents=True)

primary_folder = raw_data_path.joinpath("primary_issuance")
if not primary_folder.exists():
    primary_folder.mkdir(parents=True)

# an empty placeholder dataset to store dates whwere html parsing fails
missing_dates_df = raw_data_path.joinpath("missing_dates.csv")


def driver_generate():
    """A function to initiate the driver"""
    driver = webdriver.Edge()
    return driver


def drp_view_selector(driver):
    """A fucntion which selects the necessary drop down option to isolate results from secondary markets"""
    sleep(2)

    drp = Select(driver.find_element(By.XPATH, '//select[@id="drp_view"]'))
    drp.select_by_value("Only Secondary Market")


def calendar_selector(driver, date: str):
    """A function which selects the required dates and provides the form inputs"""
    sleep(2)

    cal_image = driver.find_element(By.XPATH, "//img[@id='imgtxtFromDate']")
    cal_image.click()
    sleep(1)

    cal_input = driver.find_element(By.XPATH, "//input[@id='hdnFromDate']")
    driver.execute_script(f"arguments[0].value = '{date}'", cal_input)

    sleep(2)


def submit_form(driver):
    """A function which accepts the input date and submits the form"""
    go_button = driver.find_element(By.XPATH, '//a[@id="btnSubmit"]')
    go_button.click()

    sleep(2)


def extract_table(driver):
    """A function whicg identifies the necessary rables and outputs its outerHTML"""
    data_tables = driver.find_elements(By.XPATH, '//table[@class="tbls01"]')
    sleep(2)
    data_list = [
        pd.read_html(frame.get_attribute("outerHTML")) for frame in data_tables
    ]

    return data_list


def data_exporter(df_name: str, df: pd.DataFrame, date: str):
    """A function which is inspects each dataset and places it accordingly in the respective directories within the raw data folder"""
    try:
        print(df_name)
        if "_in_capital" in df_name:
            df_path = cap_mkt_folder.joinpath(f"{df_name}.csv")

        elif "_in_otc" in df_name:
            df_path = otc_folder.joinpath(f"{df_name}.csv")

        elif "primary" in df_name:
            df_path = primary_folder.joinpath(f"{df_name}.csv")

        print(df_path)
        if not df_path.exists():
            df.to_csv(df_path, index=False)

        else:
            print("File exists. Aborting export!!!")

    except UnboundLocalError:
        print("error in path, hard assigning path")
        miss_df = pd.read_csv(missing_dates_df)
        df2 = pd.DataFrame({"missing_dates": [date]})
        miss_df = pd.concat([miss_df, df2], axis=0)
        miss_df.to_csv(missing_dates_df, index=False)


def data_grabber(data: list, date: str):
    """A function which takes in the outerHTML of tables and parses it into Pandas dataframes"""
    data_list = data
    current_date = date

    for data_frame in data_list:
        df = pd.DataFrame(data_frame[0])

        data_columns = df.columns

        actual_cols = [col[1] for col in data_columns]

        df_name = str(data_columns[0][0]).lower().replace(" ", "_")
        print(df_name)

        df.columns = actual_cols

        data_exporter(df_name, df, current_date)


def date_builder():
    """A function which creates a list week days between the spoecified start and end dates."""
    # initializing date
    start_date = datetime.datetime.strptime("30-05-2022", "%d-%m-%Y")
    end_date = datetime.datetime.strptime("13-10-2023", "%d-%m-%Y")

    date_generated = pd.date_range(start_date, end_date, freq="B")
    date_list = date_generated.strftime("%d-%b-%Y")

    return date_list


def scrape():
    """A function that compiles and initiates all the pre-defined functions to scrape, aprse and export secondary bond market information from the NSDL aspx dashboard."""
    dates = date_builder()

    driver = driver_generate()

    url = "https://www.fpi.nsdl.co.in/web/Reports/traderepositoryreport.aspx"

    driver.get(url)

    # selecting secondary markets
    drp_view_selector(driver)

    for date in dates:
        # adding the date
        calendar_selector(driver, date)

        # submitting form with date
        submit_form(driver)

        # capturing output table
        dfs = extract_table(driver)

        # cleaning the extrcated datasets
        data_grabber(dfs, date)


scrape()

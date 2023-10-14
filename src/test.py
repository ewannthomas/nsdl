# import re

# df_name = "secondary_market_repository_for_bonds_traded_in_otc_including_rfq_market_segment_for_13-sep-2023"

# print(re.search(re.compile("_in_otc"), df_name).group())


# import datetime
import pandas as pd
from pathlib import Path

# # initializing date
# start_date = datetime.datetime.strptime("01-7-2022", "%d-%m-%Y")
# end_date = datetime.datetime.strptime("01-8-2022", "%d-%m-%Y")

# date_generated = pd.date_range(start_date, end_date, freq="B")
# date_list = date_generated.strftime("%d-%b-%Y")
# print(type(date_list[0]))


# defining directory
dir_path = Path(__file__).resolve().parents[1]
raw_data_path = dir_path.joinpath("data", "raw")
if not raw_data_path.exists():
    raw_data_path.mkdir(parents=True)

missing_dates_df = raw_data_path.joinpath("missing_dates.csv")
miss_df = pd.read_csv(missing_dates_df)
df2 = pd.DataFrame({"missing_dates": ["09-Aug-2023"]})
miss_df = pd.concat([miss_df, df2], axis=0)
print(miss_df)

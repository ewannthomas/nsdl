import pandas as pd
from pathlib import Path

# defining directories
dir_path = Path(__file__).resolve().parents[1]
cap_data_path = dir_path.joinpath("data", "raw/in_cap_mkts")
otc_data_path = dir_path.joinpath("data", "raw/in_otc")
interim_data_path = dir_path.joinpath("data", "interim")
if not interim_data_path.exists():
    interim_data_path.mkdir(parents=True)

# reading in raw files and exporting appended otc data
otc_files = otc_data_path.glob("*.csv")
otc_dfs = [pd.read_csv(file) for file in otc_files]
otc_data_appended = pd.concat(otc_dfs, axis=0)
otc_data_appended.to_csv(interim_data_path.joinpath("otc_data.csv"), index=False)


# reading in raw files and exporting appended cap data
cap_files = cap_data_path.glob("*.csv")
cap_dfs = [pd.read_csv(file) for file in cap_files]
cap_data_appended = pd.concat(cap_dfs, axis=0)
cap_data_appended.to_csv(interim_data_path.joinpath("cap_data.csv"), index=False)

print(otc_data_appended)

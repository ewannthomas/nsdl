import requests as r
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# defining directory
dir_path = Path(__file__).resolve().parents[1]
header_path = Path(__file__).resolve().parents[0].joinpath("headers.json")


url = "https://www.fpi.nsdl.co.in/web/Reports/traderepositoryreport.aspx"

# importing headers
with open(str(header_path), "r") as in_file:
    headers = dict(json.load(in_file))

payload = {
    "drp_EntityType": "For All",
    "hdndrpEntity": "0",
    "txtDescription": "",
    "drp_view": "Only Secondary Market",
    "hdndrpview": "0",
    "hdnFromDate": "02-Jan-2017",
    "HdnValexceldata": "",
    "hdnFlag": "",
    "drp_EntityType_Month": "For All",
    "hdndrpEntityMonth": "0",
    "txtDescription_Monthly": "",
    "drp_view_month": "2",
    "hdndrpviewMonth": "2",
    "ddlYear": "2023",
    "ddlMonth": "6",
    "HiddenField1": "",
    "HiddenField2": "",
    "hdnSelectedTab": "0",
}


page = r.post(url=url, headers=headers, data=payload)

soup = BeautifulSoup(page.content, "html5lib")

table = soup.find("div", attrs={"id": "dvTradeData"})

df = pd.read_html(table.decode_contents())

for d, name in zip(df, ["a", "b", "c"]):
    d.to_csv(f"{name}.csv", index=False)

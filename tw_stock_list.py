import os
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime


def get_list(url):

    # get stock list
    res = requests.get(url)
    df_full = pd.read_html(res.text, header=0)[0]
    df = df_full[df_full["CFICode"]=="ESVUFR"].reset_index(drop=True)
    df["備註"] = df["備註"].replace(np.nan, "", regex=True)

    # split ticker and name
    df.loc[:, "ticker"] = df.iloc[:, 0].str.split("\s", expand=True)[0].replace("\s","")
    df.loc[:, "name"] = df.iloc[:, 0].str.split("\s", expand=True)[1].replace("\s","")
    df.__delitem__("有價證券代號及名稱")

    # reorder the columns
    cols = list(df)
    cols.insert(0, cols.pop(cols.index("ticker")))
    cols.insert(1, cols.pop(cols.index("name")))
    df = df.loc[:, cols]
    return df


def save_csv(market, df):

    # build output folder
    output_folder = "./tw_stock_list/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, mode=0o777)

    # output dataframe as csv
    output_file = "{}_list_update_{}.csv".format(market, datetime.now().strftime("%Y-%m-%d"))
    output = "{}{}".format(output_folder, output_file)
    df.to_csv(path_or_buf=output, index=False, encoding="utf-8-sig")

    print("{} done!".format(output_file))


def concat():

    df_twse = get_list(twse_url)
    df_otc = get_list(otc_url)
    save_csv("twse", df_twse)
    save_csv("otc", df_otc)

    # concat and drop index
    df_stock = pd.concat([df_twse, df_otc]).sort_values("ticker", ascending=True).reset_index(drop=True)
    df_stock["ticker"] = df_stock["ticker"] + ".TW"
    save_csv("stock", df_stock)


url_part = "http://isin.twse.com.tw/isin/C_public.jsp?strMode="
twse_url = "{}2".format(url_part)
otc_url = "{}4".format(url_part)

start_time = time.time()
concat()
print("--- {:.2f} sec spent ---".format(time.time() - start_time))
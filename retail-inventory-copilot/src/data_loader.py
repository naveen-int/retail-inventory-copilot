import pandas as pd


def load_data():
    products = pd.read_csv("data/products.csv")
    stores = pd.read_csv("data/stores.csv")
    sales = pd.read_csv("data/sales.csv")
    stock = pd.read_csv("data/stock.csv")

    sales["date"] = pd.to_datetime(sales["date"])

    return products, stores, sales, stock
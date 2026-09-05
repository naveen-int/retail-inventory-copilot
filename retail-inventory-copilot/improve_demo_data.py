import pandas as pd
import random
from datetime import date, timedelta

random.seed(42)

# -----------------------------------------
# LOAD EXISTING DATA
# -----------------------------------------

products = pd.read_csv("data/products.csv")
stores = pd.read_csv("data/stores.csv")
stock = pd.read_csv("data/stock.csv")


# -----------------------------------------
# CREATE 30 DAYS OF SALES
# -----------------------------------------

sales_data = []

start_date = date(2026, 8, 1)

for day_number in range(30):

    current_date = start_date + timedelta(days=day_number)

    for _, store in stores.iterrows():

        selected_products = random.sample(
            list(products.index),
            random.randint(8, 15)
        )

        for product_index in selected_products:

            product = products.iloc[product_index]

            product_id = product["product_id"]
            price = product["price"]

            quantity = random.randint(1, 8)

            # High-demand products
            if product_id in ["P001", "P004", "P010", "P015"]:
                quantity = random.randint(4, 12)

            # Lower-demand products
            if product_id in ["P005", "P014", "P011"]:
                quantity = random.randint(1, 5)

            revenue = quantity * price

            sales_data.append([
                current_date.isoformat(),
                store["store_id"],
                product_id,
                quantity,
                revenue
            ])


sales = pd.DataFrame(
    sales_data,
    columns=[
        "date",
        "store_id",
        "product_id",
        "quantity_sold",
        "revenue"
    ]
)


# -----------------------------------------
# NON-MOVING PRODUCT
# P019 gets no sales
# -----------------------------------------

sales = sales[
    sales["product_id"] != "P019"
].copy()


# -----------------------------------------
# SALES SPIKE
# August 20
# -----------------------------------------

spike_date = "2026-08-20"

for store_id in stores["store_id"]:

    for product_id in ["P010", "P015"]:

        product = products[
            products["product_id"] == product_id
        ].iloc[0]

        quantity = 30

        sales.loc[len(sales)] = [
            spike_date,
            store_id,
            product_id,
            quantity,
            quantity * product["price"]
        ]


# -----------------------------------------
# SALES DROP
# August 21
# -----------------------------------------

drop_date = "2026-08-21"

sales = sales[
    sales["date"] != drop_date
].copy()


# -----------------------------------------
# MAKE STOCK-OUT RISKS
# -----------------------------------------

risk_products = ["P001", "P004", "P010", "P015"]

for store_id in stores["store_id"]:

    for product_id in risk_products:

        condition = (
            (stock["store_id"] == store_id)
            & (stock["product_id"] == product_id)
        )

        stock.loc[condition, "current_stock"] = random.randint(3, 6)


# -----------------------------------------
# MAKE OVERSTOCK ITEMS
# -----------------------------------------

overstock_products = ["P006", "P008", "P018", "P020", "P013"]

for product_id in overstock_products:

    condition = (
        stock["product_id"] == product_id
    )

    stock.loc[
        condition,
        "current_stock"
    ] = 150


# -----------------------------------------
# MAKE P019 NON-MOVING WITH STOCK
# -----------------------------------------

condition = stock["product_id"] == "P019"

stock.loc[
    condition,
    "current_stock"
] = 80


# -----------------------------------------
# SAVE DATA
# -----------------------------------------

sales.to_csv(
    "data/sales.csv",
    index=False
)

stock.to_csv(
    "data/stock.csv",
    index=False
)


# -----------------------------------------
# CONFIRMATION
# -----------------------------------------

print("Demo data updated successfully!")
print()
print("Sales rows:", len(sales))
print("Stock rows:", len(stock))
print("Sales period:", sales["date"].min(), "to", sales["date"].max())
print("Sales spike created for:", spike_date)
print("Sales drop created for:", drop_date)
print("Overstock products:", ", ".join(overstock_products))
print("Non-moving product: P019")
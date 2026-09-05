import pandas as pd


def calculate_summary(products, stores, sales, stock):

    # -----------------------------
    # PREPARE DATE COLUMN
    # -----------------------------
    sales["date"] = pd.to_datetime(sales["date"])

    # -----------------------------
    # BASIC SALES SUMMARY
    # -----------------------------
    total_revenue = sales["revenue"].sum()
    total_units = sales["quantity_sold"].sum()
    total_stock = stock["current_stock"].sum()

    # -----------------------------
    # SALES PERIOD
    # -----------------------------
    number_of_days = (
        sales["date"].max() - sales["date"].min()
    ).days + 1

    # -----------------------------
    # PRODUCT SALES
    # -----------------------------
    product_sales = (
        sales.groupby("product_id")
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
    )

    product_sales = product_sales.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
                "price"
            ]
        ],
        on="product_id",
        how="left"
    )

    # -----------------------------
    # AVERAGE DAILY SALES
    # -----------------------------
    product_sales["avg_daily_sales"] = (
        product_sales["quantity_sold"] / number_of_days
    )

    # -----------------------------
    # TOP PRODUCTS
    # -----------------------------
    top_products = (
        product_sales
        .sort_values("revenue", ascending=False)
        .head(5)
    )

    # -----------------------------
    # BOTTOM PRODUCTS
    # -----------------------------
    bottom_products = (
        product_sales
        .sort_values("revenue", ascending=True)
        .head(5)
    )

    # -----------------------------
    # STOCK + PRODUCT INFORMATION
    # -----------------------------
    inventory = stock.merge(
        products[
            [
                "product_id",
                "product_name",
                "category"
            ]
        ],
        on="product_id",
        how="left"
    )

    # Add sales information
    inventory = inventory.merge(
        product_sales[
            [
                "product_id",
                "quantity_sold",
                "avg_daily_sales"
            ]
        ],
        on="product_id",
        how="left"
    )

    # Products with no sales
    inventory["quantity_sold"] = (
        inventory["quantity_sold"].fillna(0)
    )

    inventory["avg_daily_sales"] = (
        inventory["avg_daily_sales"].fillna(0)
    )

    # -----------------------------
    # ESTIMATED DAYS OF STOCK
    # -----------------------------
    inventory["days_of_stock"] = inventory.apply(
        lambda row:
        row["current_stock"] / row["avg_daily_sales"]
        if row["avg_daily_sales"] > 0
        else 999,
        axis=1
    )

    # -----------------------------
    # LIKELY STOCK-OUTS
    # -----------------------------
    stock_out_risk = inventory[
        (inventory["avg_daily_sales"] > 0)
        & (inventory["days_of_stock"] <= 7)
    ].copy()

    stock_out_risk = stock_out_risk.sort_values(
        "days_of_stock"
    )

       # -----------------------------
    # OVERSTOCK
    # -----------------------------
    overstock = inventory[
        (
            (inventory["avg_daily_sales"] > 0)
            & (inventory["days_of_stock"] >= 15)
        )
        |
        (inventory["current_stock"] >= 150)
    ].copy()

    overstock = overstock.sort_values(
        "days_of_stock",
        ascending=False
    )

    # -----------------------------
    # NON-MOVING STOCK
    # -----------------------------
    non_moving = inventory[
        (inventory["quantity_sold"] == 0)
        & (inventory["current_stock"] > 0)
    ].copy()

    # -----------------------------
    # STORE PERFORMANCE
    # -----------------------------
    store_sales = (
        sales.groupby("store_id")
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
    )

    store_sales = store_sales.merge(
        stores[
            [
                "store_id",
                "store_name",
                "location"
            ]
        ],
        on="store_id",
        how="left"
    )

    store_sales = store_sales.sort_values(
        "revenue",
        ascending=False
    )

    # -----------------------------
    # DAILY SALES TREND
    # -----------------------------
    all_dates = pd.date_range(
        sales["date"].min(),
        sales["date"].max(),
        freq="D"
    )

    daily_sales = (
        sales.groupby("date")
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reindex(all_dates, fill_value=0)
        .rename_axis("date")
        .reset_index()
    )

    # -----------------------------
    # SALES SPIKES / DROPS
    # -----------------------------
    average_daily_revenue = (
        daily_sales["revenue"].mean()
    )

    daily_sales["difference_from_average"] = (
        daily_sales["revenue"]
        - average_daily_revenue
    )

    sales_spikes = daily_sales[
        daily_sales["revenue"]
        >= average_daily_revenue * 1.25
    ].copy()

    sales_drops = daily_sales[
        daily_sales["revenue"]
        <= average_daily_revenue * 0.75
    ].copy()

    # -----------------------------
    # JSON-FRIENDLY DATE FORMAT
    # -----------------------------
    daily_sales["date"] = (
        daily_sales["date"]
        .dt.strftime("%Y-%m-%d")
    )

    sales_spikes["date"] = (
        sales_spikes["date"]
        .dt.strftime("%Y-%m-%d")
    )

    sales_drops["date"] = (
        sales_drops["date"]
        .dt.strftime("%Y-%m-%d")
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "total_revenue": float(total_revenue),

        "total_units": int(total_units),

        "total_stock": int(total_stock),

        "number_of_days": int(number_of_days),

        "top_products":
            top_products.to_dict("records"),

        "bottom_products":
            bottom_products.to_dict("records"),

        "stock_out_risk":
            stock_out_risk.to_dict("records"),

        "overstock":
            overstock.to_dict("records"),

        "non_moving":
            non_moving.to_dict("records"),

        "store_sales":
            store_sales.to_dict("records"),

        "daily_sales":
            daily_sales.to_dict("records"),

        "sales_spikes":
            sales_spikes.to_dict("records"),

        "sales_drops":
            sales_drops.to_dict("records"),
    }
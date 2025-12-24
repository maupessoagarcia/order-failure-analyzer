import pandas as pd
import re


def process_file(df: pd.DataFrame) -> dict:
    """
    Core processing function.
    Returns:
        orders (dict)
    """

    df = df.copy()

    df.columns = [
        'Id', 'Order Number', 'Country', 'State', 'City', 'Line1',
        'Line2', 'Postal Code', 'Customer Name', 'Order Date',
        'Sku', 'Quantity', 'Barcode', 'Fail Code', 'Fail Detail', 'Unused'
    ]

    df = df[['Order Number', 'Country', 'Sku', 'Quantity', 'Fail Code', 'Fail Detail']]

    # Keep only NO_STOCK_AVAILABLE
    df = df[
        df['Fail Code'].astype(str).str.strip() == 'NO_STOCK_AVAILABLE'
    ].reset_index(drop=True)

    orders = {}

    for _, row in df.iterrows():
        order_id = row['Order Number']
        country = row['Country']
        sku = str(row['Sku']).strip()
        quantity = int(row['Quantity'])
        fail_detail = str(row['Fail Detail'])

        if order_id not in orders:
            orders[order_id] = {"country": country}

        orders[order_id][sku] = {
            "quantity": quantity,
            "available": True
        }

        # Extract unavailable SKUs from FIRST sentence only
        first_sentence = fail_detail.split('.')[0]
        match = re.search(r'\[\[(.+?)\]\]|\[(.+?)\]', first_sentence)

        if match:
            unavailable_str = match.group(1) or match.group(2)
            unavailable_skus = [s.strip() for s in unavailable_str.split()]

            for unavail_sku in unavailable_skus:
                if unavail_sku in orders[order_id]:
                    orders[order_id][unavail_sku]["available"] = False

    return orders


def all_available(orders: dict) -> dict:
    return {
        order_id: data
        for order_id, data in orders.items()
        if all(
            sku_data["available"]
            for key, sku_data in data.items()
            if key != "country"
        )
    }


def failed_orders(orders: dict) -> dict:
    return {
        order_id: data
        for order_id, data in orders.items()
        if any(
            sku_data["available"] is False
            for key, sku_data in data.items()
            if key != "country"
        )
    }


def us_x_nonus_fails(orders: dict):
    us_agg = {}
    nonus_agg = {}

    for data in orders.values():
        country = str(data.get("country", "")).strip()

        for sku, info in data.items():
            if sku == "country":
                continue

            if not info.get("available", True):
                qty = int(info.get("quantity", 0))

                if country == "US":
                    us_agg[sku] = us_agg.get(sku, 0) + qty
                else:
                    nonus_agg[sku] = nonus_agg.get(sku, 0) + qty

    df_us = (
        pd.DataFrame(us_agg.items(), columns=["Sku", "TotalQuantity"])
        .sort_values("TotalQuantity", ascending=False)
        .reset_index(drop=True)
    )

    df_nonus = (
        pd.DataFrame(nonus_agg.items(), columns=["Sku", "TotalQuantity"])
        .sort_values("TotalQuantity", ascending=False)
        .reset_index(drop=True)
    )

    return df_us, df_nonus


def convert_orders_to_df(orders: dict) -> pd.DataFrame:
    rows = []

    for order_id, data in orders.items():
        rows.append({
            "OrderID": order_id,
            "Country": data["country"],
            "Skus": ",".join([k for k in data.keys() if k != "country"])
        })

    return pd.DataFrame(rows)

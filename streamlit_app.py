import streamlit as st
import pandas as pd

from logic import (
    process_file,
    all_available,
    failed_orders,
    us_x_nonus_fails,
    convert_orders_to_df
)

st.set_page_config(page_title="Order Failure Analyzer", layout="centered")

st.title("Order Failure Analyzer")

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(
    uploaded_file,
    engine="python",
    on_bad_lines="skip",
    encoding="utf-8"
    )

    st.success("File uploaded successfully")
    st.dataframe(df.head())

    option = st.radio(
        "Select output",
        (
            "Orders with all items available",
            "Failed order list",
            "SKU fails – US",
            "SKU fails – Non-US"
        )
    )

    with st.spinner("Processing file..."):
        orders = process_file(df)

    if option == "Orders with all items available":
        result = all_available(orders)
        df_out = convert_orders_to_df(result)

        st.subheader("Orders with all items available")
        st.dataframe(df_out)

        st.download_button(
            "Download CSV",
            df_out.to_csv(index=False),
            "orders_all_available.csv",
            "text/csv"
        )

    elif option == "Failed order list":
        result = failed_orders(orders)
        df_out = convert_orders_to_df(result)

        st.subheader("Failed orders")
        st.dataframe(df_out)

        st.download_button(
            "Download CSV",
            df_out.to_csv(index=False),
            "failed_orders.csv",
            "text/csv"
        )

    elif option == "SKU fails – US":
        df_us, _ = us_x_nonus_fails(orders)

        st.subheader("US SKU Failures")
        st.dataframe(df_us)

        st.download_button(
            "Download CSV",
            df_us.to_csv(index=False),
            "sku_fails_us.csv",
            "text/csv"
        )

    elif option == "SKU fails – Non-US":
        _, df_nonus = us_x_nonus_fails(orders)

        st.subheader("Non-US SKU Failures")
        st.dataframe(df_nonus)

        st.download_button(
            "Download CSV",
            df_nonus.to_csv(index=False),
            "sku_fails_non_us.csv",
            "text/csv"
        )

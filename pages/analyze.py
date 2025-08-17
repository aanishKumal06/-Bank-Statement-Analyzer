import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# --- Hide Sidebar ---
st.markdown("""
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
title_html = """
    <style>
        .title-container {
            margin-top: 50px;
            padding: 10px 0;
            font-size: 32px;
            font-weight: bold;
        }
    </style>
    <div class="title-container">📊 Statement Analyzer</div>
"""
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.markdown(title_html, unsafe_allow_html=True)
with col2:
    if st.button("🔙 Back"):
        st.switch_page("app.py")

st.markdown("---")

# --- Categorization Function ---
def categorize(description):
    description = str(description).lower()
    if any(k in description for k in ["atm", "cash", "withdrawal"]):
        return "Cash Withdrawal"
    elif any(k in description for k in ["ncell", "ntc", "recharge", "topup"]):
        return "Mobile Recharge"
    elif any(k in description for k in ["shopping", "daraz", "store", "mall", "pos"]):
        return "Shopping"
    elif any(k in description for k in ["utility", "electricity", "water", "bill", "nepal electricity"]):
        return "Utilities"
    elif any(k in description for k in ["food", "restaurant", "cafe", "hotel"]):
        return "Food & Dining"
    elif any(k in description for k in ["loan", "emi", "interest"]):
        return "Loan Payment"
    elif any(k in description for k in ["insurance", "premium"]):
        return "Insurance"
    elif any(k in description for k in ["transfer", "fund", "send", "receive", "trf", "mos:", "fps:", "ibft"]):
        return "Transfers"
    else:
        return "Others"

# --- Main Logic ---
if "df" in st.session_state:
    df = st.session_state.df.copy()
    holder = st.session_state.get("holder", "Unknown")

    # --- Convert Columns ---
    df['Withdraw'] = pd.to_numeric(df['Withdraw'], errors='coerce')
    df['Deposit'] = pd.to_numeric(df['Deposit'], errors='coerce')
    df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
    df['Txn Date'] = pd.to_datetime(df['Txn Date'], errors='coerce')

    # --- Date Filter UI ---
    min_date = df["Txn Date"].min()
    max_date = df["Txn Date"].max()

    with st.form("date_filter"):
        col1, col2, col3 = st.columns([1, 1, 0.5])
        with col1:
            start_date = st.date_input("📅 Start Date", min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
        with col2:
            end_date = st.date_input("📅 End Date", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())
        with col3:
            submitted = st.form_submit_button("Apply")

    # --- Filter Data by Date ---
    mask = (df["Txn Date"] >= pd.to_datetime(start_date)) & (df["Txn Date"] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    if not filtered_df.empty:
        # --- Calculate Summary Metrics ---
        total_deposit = filtered_df["Deposit"].sum()
        total_withdraw = filtered_df["Withdraw"].sum()
        net_balance = total_deposit - total_withdraw

        # --- Summary Header ---
        st.subheader("📄 Transaction Details")
        st.markdown("""
            <style>
            .metric-container {
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .metric-title {
                font-size: 16px;
                color: #555;
            }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-container'><div class='metric-title'>👤 Account Holder</div><h4>{holder}</h4></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-container'><div class='metric-title'>📅 From</div><h4>{start_date.strftime('%d-%b-%Y')}</h4></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-container'><div class='metric-title'>📅 To</div><h4>{end_date.strftime('%d-%b-%Y')}</h4></div>", unsafe_allow_html=True)

        # --- Summary Metrics ---
        st.subheader("💰 Account Summary")
        with st.container():
            a1, a2, a3 = st.columns(3)
            a1.markdown(f"<div class='metric-container'><div class='metric-title'>💵 Total Deposits</div><h4>Rs. {total_deposit:,.2f}</h4></div>", unsafe_allow_html=True)
            a2.markdown(f"<div class='metric-container'><div class='metric-title'>💸 Total Withdrawals</div><h4>Rs. {total_withdraw:,.2f}</h4></div>", unsafe_allow_html=True)
            a3.markdown(f"<div class='metric-container'><div class='metric-title'>📊 Remaining Balance</div><h4>Rs. {net_balance:,.2f}</h4></div>", unsafe_allow_html=True)

        # --- Monthly Bar Chart: Deposit vs Withdrawal ---
        filtered_df["Month"] = filtered_df["Txn Date"].dt.to_period("M").astype(str)
        summary_df = filtered_df.groupby("Month")[["Deposit", "Withdraw"]].sum().reset_index()

        bar_fig = px.bar(
            summary_df,
            x="Month",
            y=["Deposit", "Withdraw"],
            barmode="group",
            title="Monthly Deposit vs Withdrawal",
            labels={"value": "Amount", "Month": "Month"}
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        # --- Category-wise Expense Breakdown ---
        filtered_df["Description"] = filtered_df["Description"].astype(str)
        filtered_df["Category"] = filtered_df["Description"].apply(categorize)

        df_exp = filtered_df[filtered_df["Withdraw"] > 0].copy()
        df_exp["Month"] = df_exp["Txn Date"].dt.to_period("M").astype(str)
        summary = df_exp.groupby(["Month", "Category"])["Withdraw"].sum().reset_index()

        fig = px.bar(
            summary,
            x="Month",
            y="Withdraw",
            color="Category",
            barmode="stack",
            title="Monthly Expense Breakdown by Category",
            labels={"Withdraw": "Amount (Rs.)", "Month": "Month", "Category": "Expense Type"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Balance Line Chart ---
        line_fig = px.line(
            filtered_df.sort_values("Txn Date"),
            x="Txn Date",
            y="Balance",
            title="Balance Over Time"
        )
        st.plotly_chart(line_fig, use_container_width=True)

        # --- Donut Pie Chart ---
        pie_data = pd.DataFrame({
            "Type": ["Deposit", "Withdrawal"],
            "Amount": [total_deposit, total_withdraw]
        })
        pie_fig = px.pie(
            pie_data,
            names="Type",
            values="Amount",
            hole=0.4,
            title="Transaction Breakdown"
        )
        st.plotly_chart(pie_fig, use_container_width=True)


        # --- Preview Filtered Data ---
        st.subheader("🔍 Filtered Transaction Data")
        st.dataframe(filtered_df, use_container_width=True)

        # --- Download Filtered Data ---
        st.subheader("⬇️ Download Filtered Transactions")

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name="filtered_transactions.csv",
            mime="text/csv"
        )


    else:
        st.warning("⚠️ No transactions found in the selected date range.")
else:
    st.warning("⚠️ No data found. Please upload your statement on the Home page.")

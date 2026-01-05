import streamlit as st
import pandas as pd

# 1. Page Setup
st.set_page_config(page_title="ClearQty", layout="wide")
st.title("📦 ClearQty Inventory Portal")

# 2. The Logic Function
def calculate_order(row):
    try:
        lt = int(row['LeadTimeMonths'])
        cover = float(row['DesiredCoverMonths'])
        stock = float(row['CurrentStock'])
        
        # Monthly sales (M1-M12)
        sales_cols = [f'Month{i}' for i in range(1, 13)]
        sales = [float(row[m]) for m in sales_cols if m in row]
        
        lt_demand = sum(sales[:lt])
        avg_sales = sum(sales) / len(sales) if sales else 0
        target_stock = lt_demand + (cover * avg_sales)
        rec_qty = max(0, round(target_stock - stock))
        
        status = "✅ Healthy"
        if stock < lt_demand:
            status = "🔴 Stockout Risk"
            
        return pd.Series([lt_demand, rec_qty, status])
    except Exception as e:
        return pd.Series([0, 0, f"Error: {str(e)}"])

# 3. Simple File Upload
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if st.button("Calculate Replenishment"):
        df[['LeadTimeDemand', 'RecommendedOrder', 'Status']] = df.apply(calculate_order, axis=1)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report", csv, "clearqty_results.csv")
else:
    st.info("Awaiting CSV upload...")

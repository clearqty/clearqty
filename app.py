import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ClearQty | Inventory Planner", layout="wide", page_icon="📦")

# --- CUSTOM BRANDING ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .instruction-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 ClearQty Replenishment Portal")

# --- SIDEBAR INSTRUCTIONS ---
with st.sidebar:
    st.header("Help & Instructions")
    st.info("""
    **How to use:**
    1. Download the Template CSV.
    2. Fill in your SKU data and 12-month sales forecast.
    3. Upload the file to see 'Quantity to Order' and 'Risk Flags'.
    """)
    
    # Create a template for the user to download
    template_data = pd.DataFrame(columns=['SKU', 'LeadTimeMonths', 'DesiredCoverMonths', 'CurrentStock'] + [f'Month{i}' for i in range(1, 13)])
    template_data.loc[0] = ['EXAMPLE-SKU-01', 4, 3, 50] + [40]*12
    
    csv_template = template_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV Template", csv_template, "clearqty_template.csv", "text/csv")

# --- MAIN INTERFACE ---
st.markdown("""
<div class="instruction-card">
    <h4>Welcome to ClearQty</h4>
    <p>This tool calculates <b>What</b> to order, <b>When</b> to order, and <b>Why</b> based on your lead-time demand and target coverage.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Step 2: Upload your filled-out template", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    def calculate_replenishment(row):
        try:
            lt = int(row['LeadTimeMonths'])
            cover = float(row['DesiredCoverMonths'])
            stock = float(row['CurrentStock'])
            sales_cols = [f'Month{i}' for i in range(1, 13)]
            sales = [float(row[m]) for m in sales_cols if m in row]
            
            lt_demand = sum(sales[:lt])
            avg_sales = sum(sales) / 12
            target_stock = lt_demand + (cover * avg_sales)
            order_qty = max(0, round(target_stock - stock))
            
            if stock < lt_demand:
                status = "🔴 STOCKOUT RISK"
            elif stock < (lt_demand + avg_sales):
                status = "🟡 LOW STOCK"
            else:
                status = "✅ HEALTHY"
                
            return pd.Series([lt_demand, round(target_stock), order_qty, status])
        except:
            return pd.Series([0, 0, 0, "⚠️ Check Data"])

    # Calculations
    df[['LT_Demand', 'Target_Level', 'Order_QTY', 'Status']] = df.apply(calculate_replenishment, axis=1)
    
    # Display results with highlighting
    st.subheader("Replenishment Plan")
    st.dataframe(df.style.apply(lambda x: ["background-color: #ffcccc" if v == "🔴 STOCKOUT RISK" else "" for v in x], axis=1, subset=['Status']))
    
    # Download results
    final_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Download Results", final_csv, "replenishment_plan.csv")
else:
    st.warning("Awaiting file upload. Please download the template from the sidebar if you don't have one.")

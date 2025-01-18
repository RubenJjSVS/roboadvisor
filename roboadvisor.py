import yfinance as yf
import pandas as pd
import streamlit as st

# Define stock tickers for the water and waste treatment industry
WATER_WASTE_TICKERS = ["AQUA", "WTRG", "XYL", "AWK", "CWT"]

# Fetch stock data with key financial metrics
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            # Extract key metrics
            pe_ratio = stock.info.get("trailingPE", None)
            debt_to_equity = stock.info.get("debtToEquity", None)
            revenue_growth = stock.info.get("revenueGrowth", None)
            eps_growth = stock.info.get("earningsGrowth", None)

            data[ticker] = {
                "Name": stock.info.get("shortName", "N/A"),
                "P/E Ratio": pe_ratio,
                "Debt-to-Equity": debt_to_equity,
                "Revenue Growth (%)": revenue_growth * 100 if revenue_growth else None,
                "EPS Growth (%)": eps_growth * 100 if eps_growth else None,
            }
        except Exception:
            data[ticker] = {
                "Name": "Data not available",
                "P/E Ratio": None,
                "Debt-to-Equity": None,
                "Revenue Growth (%)": None,
                "EPS Growth (%)": None,
            }
    return pd.DataFrame.from_dict(data, orient="index")

# Generate investment recommendations based on financial metrics
def generate_recommendations(data):
    # Filter out any missing data
    filtered_data = data.dropna()

    # Normalize metrics for ranking (lower is better for P/E and Debt-to-Equity, higher is better for growth metrics)
    filtered_data["P/E Rank"] = filtered_data["P/E Ratio"].rank(ascending=True)
    filtered_data["Debt-to-Equity Rank"] = filtered_data["Debt-to-Equity"].rank(ascending=True)
    filtered_data["Revenue Growth Rank"] = filtered_data["Revenue Growth (%)"].rank(ascending=False)
    filtered_data["EPS Growth Rank"] = filtered_data["EPS Growth (%)"].rank(ascending=False)

    # Compute an overall score (equal weighting)
    filtered_data["Total Score"] = (
        filtered_data["P/E Rank"] +
        filtered_data["Debt-to-Equity Rank"] +
        filtered_data["Revenue Growth Rank"] +
        filtered_data["EPS Growth Rank"]
    )

    # Sort by the total score (lower score = better)
    recommendations = filtered_data.sort_values(by="Total Score").head(2)
    return recommendations

# Streamlit Dashboard
def dashboard():
    st.title("Water & Waste Treatment Investment Advisor")
    
    # Fetch financial data
    financial_data = fetch_stock_data(WATER_WASTE_TICKERS)
    st.write("### Financial Metrics", financial_data)

    # Generate and display recommendations
    recommendations = generate_recommendations(financial_data)
    st.write("### Recommended Stocks to Buy", recommendations[["Name", "P/E Ratio", "Debt-to-Equity", "Revenue Growth (%)", "EPS Growth (%)"]])

    # Visualize key metrics
    st.write("### P/E Ratio Comparison")
    st.bar_chart(financial_data["P/E Ratio"])

    st.write("### Debt-to-Equity Ratio Comparison")
    st.bar_chart(financial_data["Debt-to-Equity"])

    st.write("### Revenue Growth Comparison")
    st.bar_chart(financial_data["Revenue Growth (%)"])

    st.write("### EPS Growth Comparison")
    st.bar_chart(financial_data["EPS Growth (%)"])

if __name__ == "__main__":
    dashboard()

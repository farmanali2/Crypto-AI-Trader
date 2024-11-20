import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Crypto Backtesting Engine")

# Sidebar - Upload CSV or Select Example Data
st.sidebar.header("Upload or Select Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

# Example data
example_data = "data/BTCUSDT_minute_data.csv"
use_example = st.sidebar.checkbox("Use Example Data")

# Load Data
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.success("Uploaded data loaded successfully!")
elif use_example:
    data = pd.read_csv(example_data)
    st.success("Using example data!")
else:
    st.warning("Upload a CSV file or select the example data to proceed.")
    st.stop()

# Preprocess Data
data["open_time"] = pd.to_datetime(data["open_time"])
data.set_index("open_time", inplace=True)

# Show data preview
st.write("### Data Preview", data.head())

# Sidebar - Strategy Parameters
st.sidebar.header("Strategy Parameters")
short_window = st.sidebar.slider("Short Moving Average Window", 5, 50, 10)
long_window = st.sidebar.slider("Long Moving Average Window", 50, 200, 100)

# Calculate Moving Averages
data["MA_short"] = data["close"].rolling(window=short_window).mean()
data["MA_long"] = data["close"].rolling(window=long_window).mean()

# Generate Buy/Sell Signals
data["signal"] = 0
data.loc[data["MA_short"] > data["MA_long"], "signal"] = 1  # Buy
data.loc[data["MA_short"] <= data["MA_long"], "signal"] = -1  # Sell

# Display Updated Data
st.write("### Updated Data with Strategy Signals", data[["close", "MA_short", "MA_long", "signal"]].tail())

# Plot Close Price and Moving Averages
st.write("### Price Chart with Moving Averages")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data["close"], label="Close Price", color="blue")
ax.plot(data.index, data["MA_short"], label=f"MA {short_window}", color="orange")
ax.plot(data.index, data["MA_long"], label=f"MA {long_window}", color="green")
ax.legend()
st.pyplot(fig)

# Backtesting Logic
initial_balance = 10000
balance = initial_balance
position = 0
portfolio = []

for i, row in data.iterrows():
    if row["signal"] == 1 and balance > 0:  # Buy
        position = balance / row["close"]
        balance = 0
    elif row["signal"] == -1 and position > 0:  # Sell
        balance = position * row["close"]
        position = 0
    portfolio.append(balance + (position * row["close"]))

data["portfolio"] = portfolio

# Plot Portfolio Value
st.write("### Portfolio Value Over Time")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data["portfolio"], label="Portfolio Value", color="purple")
ax.legend()
st.pyplot(fig)

# Show Final Portfolio Value
final_value = portfolio[-1]
total_return = (final_value - initial_balance) / initial_balance * 100
st.write(f"### Final Portfolio Value: ${final_value:.2f}")
st.write(f"### Total Return: {total_return:.2f}%")
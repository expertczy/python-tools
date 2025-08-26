import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# Configuration
STOCK_CODE = 'IITU.L'  # Change this to any stock code you want to analyze
DAYS_TO_PLOT = 200   # Number of days to look back

# Get end date (today) and start date
end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_TO_PLOT)

# Download stock data
stock_data = yf.download(STOCK_CODE, start=start_date, end=end_date)

# Calculate percentage change for price
initial_price = stock_data['Close'].iloc[0]
price_pct_change = ((stock_data['Close'] - initial_price) / initial_price) * 100

# Define the date to highlight
highlight_date = datetime(2025, 1, 17)

# Create the figure and axis with two y-axes
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis

# Plot volume data on the first y-axis
ax1.plot(stock_data.index, stock_data['Volume'], linewidth=2, color='blue', label='Volume')
ax1.set_ylabel('Volume', fontsize=12, color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Plot price percentage change on the second y-axis
ax2.plot(stock_data.index, price_pct_change, linewidth=2, color='red', label='Price Change %')
ax2.set_ylabel('Price Change (%)', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Highlight the specific date if it exists in the data
if highlight_date in stock_data.index:
    highlight_idx = stock_data.index.get_loc(highlight_date)
    # Highlight volume
    ax1.scatter(highlight_date, stock_data['Volume'].iloc[highlight_idx], 
                color='darkblue', s=100, zorder=5, label=f'Volume on {highlight_date.strftime("%Y-%m-%d")}')
    # Highlight price change
    ax2.scatter(highlight_date, price_pct_change.iloc[highlight_idx], 
                color='darkred', s=100, zorder=5, label=f'Price Change % on {highlight_date.strftime("%Y-%m-%d")}')
    # Add vertical line
    plt.axvline(x=highlight_date, color='green', linestyle='--', alpha=0.7, 
                label=f'Highlight: {highlight_date.strftime("%Y-%m-%d")}')

# Customize the chart
plt.title(f'{STOCK_CODE} Daily Trading Volume and Price Change % (Last {DAYS_TO_PLOT} Days)', fontsize=14)
ax1.set_xlabel('Date', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Format volume y-axis labels to show millions
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6)}M'))

# Add legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()
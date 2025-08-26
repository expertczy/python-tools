# Python Tools

A collection of simple Python utilities for common tasks.

## Tools

### 📄 PDF Splitter (`pdf_splitter.py`)
- Split PDF files by page range
- Simple GUI interface
- Requires: `PyPDF2`, `tkinter`

### 📊 Stock Price Tracker (`stock_price.py`)
- Track multiple stock indices and ETFs
- Compare price changes over time
- Generate charts with matplotlib
- Requires: `yfinance`, `matplotlib`

### 📈 Stock Volume Analyzer (`stock_volumn.py`)
- Analyze trading volume and price changes
- Dual-axis charts for volume and price
- Highlight specific dates
- Requires: `yfinance`, `matplotlib`, `numpy`

### ✂️ Video Cutter (`video_cutter.py`)
- Cut video files by time range
- GUI interface for easy use
- Fast cutting with ffmpeg (if available)
- Fallback to moviepy for processing
- Requires: `moviepy`, `tkinter`

## Installation

```bash
pip install PyPDF2 yfinance matplotlib moviepy numpy
```

## Usage

Run any tool directly with Python:

```bash
python pdf_splitter.py
python stock_price.py
python stock_volumn.py
python video_cutter.py
```

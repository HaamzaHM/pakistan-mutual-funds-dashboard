# 📊 Pakistan Mutual Funds Dashboard

An interactive, open-source Streamlit dashboard for exploring and analyzing mutual funds data from Pakistan. Featuring dynamic filtering, pagination, comprehensive analytics, and real-time data visualization based on official MUFAP data.

**🔗 Data Source:** [MUFAP - Mutual Funds Association of Pakistan](https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=1) (Publicly Available)

**📧 Contact & Questions:** 
- Email: [m.hamzamaliik@gmail.com](mailto:m.hamzamaliik@gmail.com)
- LinkedIn: [linkedin.com/in/hamzamaliik](https://www.linkedin.com/in/hamzamaliik/)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HaamzaHM/pakistan-mutual-funds-dashboard.git
   cd pakistan-mutual-funds-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare your data**
   - Place your CSV file in the `data/` folder
   - Or use `funds_clean.csv` if available

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`

---

## 📋 CSV Format

Your CSV needs these columns (case-insensitive):

| Column | Required? | Example |
|--------|-----------|---------|
| Fund Name | ✅ Yes | ABL Cash Fund |
| Company / Company Name | ⭐ Optional | ABL Asset Management |
| NAV | ✅ Yes | 10.78 |
| Category | ⭐ Optional | Money Market |
| Risk Rating / Risk | ⭐ Optional | Low Risk |
| Offer Price | ⭐ Optional | 10.87 |

**Minimum:** Just need Fund Name + NAV columns to start!

---

## ✨ Features

- **� Paginated Data Table** - Browse 50 funds per page with sorting capabilities
- **� Dynamic Filters** - Filter by fund name, category, company, risk level, and NAV range
- **📊 Analytics Dashboard** - Visualize distributions and top-performing funds
- **⚠️ Risk Analysis** - Detailed analysis by risk rating with statistics
- **📥 Data Export** - Download filtered results as CSV
- **🎨 Professional UI** - Clean, responsive design with modern styling

---

## 📊 About This Project

This is an open-source interactive dashboard built with **Streamlit** to make mutual funds data more accessible to Pakistan's investors. The data is sourced directly from the **Mutual Funds Association of Pakistan (MUFAP)** website and presented in an easy-to-use interface with powerful filtering and analytical tools.

### Why This Dashboard?
- 📈 **Real Data**: Uses official MUFAP data (publicly available)
- 🚀 **Fast & Interactive**: Instant filtering and analysis
- 💻 **Open Source**: Free to use, modify, and deploy
- 🎯 **Investor Focused**: Designed for Pakistani fund investors
- 🔄 **Regularly Updated**: Easy to refresh with latest data from MUFAP

### Data Attribution
All mutual funds data is sourced from:
- **[MUFAP Official Website](https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=1)**
- Public data available for research and educational purposes

---

## 🎛️ Usage Guide

### Filters
1. **Search Fund Name** - Type to search for specific funds
2. **Category Filter** - Select fund categories
3. **Risk Level Filter** - Choose risk ratings (Very Low, Low, Medium, High)
4. **NAV Range** - Adjust the slider for desired NAV range
5. **Company Filter** - Filter by fund company/AMC

### Tabs
- **Data Table** - View paginated fund data with sorting and export
- **Analytics** - Charts and visualizations of fund distributions
- **By Risk** - Risk-based analysis and statistics

### Tips
- **Smart Filtering** - Category and risk filters dynamically update based on selections
- **Pagination** - Jump to any page or use previous/next buttons
- **Export Data** - Download filtered results for further analysis

---

## 📁 Project Structure

```
Sarmaya.pk web scrapping/
│
├── app.py                 # Main dashboard application
├── config.py              # Configuration constants
├── requirements.txt       # Python packages
├── README.md             # This guide
│
├── styles/               # CSS styling
│   └── style.css         # Dashboard styling
│
└── data/                 # Your data folder
    └── funds_clean.csv   # Cleaned mutual funds data
```

---

## 🚀 How to Use

### 1. Load Your Data
- Save CSV in `data/` folder
- App auto-detects it
- Refresh page if needed

### 2. Explore with Filters
- Click on sidebar filters
- Select multiple options
- Click "Apply Filters"
- See results update instantly

### 3. View Data
- **Data Table Tab**: See all funds, sort, download
- **Analytics Tab**: Charts and statistics
- **By Risk Tab**: Risk-based analysis

### 4. Download Results
- Use "Download Filtered Data as CSV" button
- Gets your current filtered data
- File saves as `filtered_funds.csv`

---

## 📊 Example CSV Format

Save this as `data/funds.csv`:

```csv
Fund Name,Company,NAV,Category,Risk Rating,Offer Price
ABL Cash Fund,ABL Asset Management,10.78,Money Market,Low Risk,10.87
ABL Stock Fund,ABL Asset Management,39.63,Equity,High Risk,40.55
AKD Cash Fund,AKD Investment Management,54.65,Money Market,Low Risk,54.65
HBL Growth Fund,HBL Asset Management,251.15,Equity,High Risk,256.92
Meezan Islamic Fund,Al Meezan Investment,168.16,Equity,High Risk,172.03
JS Growth Fund,JS Investments,567.65,Equity,High Risk,587.24
```

---

## �� What Columns Get Auto-Detected?

Dashboard looks for these (case-insensitive):
- **Fund Name:** fund_name, name, fund
- **Company:** company, company_name, amc, asset_manager
- **NAV:** nav, price, nav_value
- **Category:** category, fund_type, type
- **Risk:** risk, risk_rating, risk_level

If your columns don't match, the app asks you to select them! 👍

---

## 💾 Export & Share

### Download Filtered Data
1. Apply your filters
2. Go to "Data Table" tab
3. Click "📥 Download Filtered Data as CSV"
4. Share the CSV file

### Deploy to Web (Free!)

**Streamlit Cloud:**
```bash
# 1. Push to GitHub
git add .
git commit -m "Add dashboard"
git push origin main

# 2. Go to https://streamlit.io/cloud
# 3. Connect your GitHub repo
# 4. Select app.py
# Deploy & share link!
```

---

## ⚙️ Customize Your Dashboard

Edit `app.py` to change:

### Page Title
```python
page_title="My Fund Dashboard"
```

### Colors
Look for this in the CSS section:
```python
#667eea 0%, #764ba2 100%  # Change these colors
```

### Filter Names
In the sidebar, change filter labels to match your data

---

## 🐛 Troubleshooting

### "No CSV file found"
- Make sure file is in `data/` folder
- Check file extension is `.csv`
- Restart: `streamlit run app.py`

### "Could not auto-detect columns"
- App will ask you to select columns
- Match to: fund_name, nav, category, company, risk
- Select the right columns for your CSV

### App is slow
- Your CSV is very large? Try filtering first
- Refresh browser: Ctrl+F5
- Check internet connection if deployed

### Filters not working
- Click "Apply Filters" button
- Make sure selections are visible in sidebar
- Try "Clear All" then reselect

---

## 📱 Mobile & Responsive

✅ Works great on:
- 💻 Desktop browsers
- 📱 Phones
- 📱 Tablets

Dashboard automatically adjusts to screen size!

---

## 🔐 Privacy & Security

✅ Safe features:
- All processing happens on YOUR computer
- No data sent to external servers
- CSV stays locally
- No login required

---

## 📞 Quick Tips

💡 **Tip 1:** Use meaningful CSV column names (fund_name, nav, etc.)

💡 **Tip 2:** Clean your CSV before uploading (remove special characters)

💡 **Tip 3:** Test with sample data first

💡 **Tip 4:** Filters are multi-select (pick multiple options!)

💡 **Tip 5:** Use "Clear All" to reset and start fresh

---

## ✅ You're All Set!

1. ✅ Place CSV in `data/` folder
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Run `streamlit run app.py`
4. ✅ Start exploring! 🎉

**Questions?** Check that your CSV has at least:
- A column with fund names
- A column with NAV values

That's all you need to get started!

---

## 📞 Contact & Support

**Have questions or suggestions?**

- **Email:** [m.hamzamaliik@gmail.com](mailto:m.hamzamaliik@gmail.com)
- **LinkedIn:** [linkedin.com/in/hamzamaliik](https://www.linkedin.com/in/hamzamaliik/)
- **GitHub Issues:** [Report bugs or request features](https://github.com/HaamzaHM/pakistan-mutual-funds-dashboard/issues)

---

## 📜 License & Attribution

- **Data Source:** [MUFAP - Mutual Funds Association of Pakistan](https://www.mufap.com.pk/)
- **Data Usage:** Public data for educational and analytical purposes
- **Project License:** MIT (Feel free to use, modify, and share)

---

## 🌟 Contributing

Found a bug? Have a feature idea? Want to improve the dashboard?

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

Contributions are welcome! 🚀

---

## 🔍 SEO Keywords

This project helps investors search for and analyze:
- Pakistan mutual funds
- MUFAP data visualization
- Fund performance analysis
- NAV tracking dashboard
- Risk-based fund selection
- Interactive mutual funds dashboard

---

**Happy Analyzing! 📊✨**

*Last Updated: January 2026*

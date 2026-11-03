# SA859CMS Cost Report - Standalone Analytics Dashboard

A zero-installation, modular commercial analytics dashboard and Excel repair toolkit for **SA859CMS & SA859JUK (50MW Humain Campus Data Center CS)**.

---

## 🚀 Quick Start (On Any PC or Office Laptop)

1. **Open the Dashboard**:
   - Double-click **`index.html`** to open directly in **Microsoft Edge** or **Google Chrome**.
   - No web server, Python, or admin permissions required.

2. **When an Updated Weekly Excel File Arrives**:
   - Open `index.html` in your browser.
   - **Drag and drop** the new `SA859CMS_Cost Report_WE_*.xlsx` file onto the drop-zone banner at the top of the dashboard.
   - All KPIs, weekly burn rates, gross margins, and transactions will update instantly in browser memory.
   - Click **"Cleaned Excel (Fast Open)"** to download the repaired `.xlsx` that opens in Excel in 1–2 seconds.

3. **1-Click Native Windows Excel Fix (Without opening the browser)**:
   - Drag and drop your `.xlsx` report directly onto **`Clean-Excel.bat`** (or double-click it).
   - In 3 seconds, it produces `[Filename]_Cleaned.xlsx` ready to open natively in Microsoft Excel.

---

## 📂 Project Structure

```
scratch/
│
├── index.html                           # Main modular dashboard application
├── README.md                            # 1-page quick start guide
│
├── css/
│   └── styles.css                       # Dashboard theme, transitions, scrollbars
│
├── js/
│   ├── app.js                           # Core controller, currency toggle (SAR/USD), tab routing
│   ├── data.js                          # Embedded baseline project dataset (works offline / file://)
│   ├── charts.js                        # Chart.js graphs (GM trend, regional mix, scope bars, weekly spend)
│   ├── excel-parser.js                  # In-browser .xlsx drag-and-drop parser & defined-names cleaner
│   └── table-explorer.js                # 4,095-row Oracle transaction grid with search, filters & CSV export
│
├── data/
│   ├── transactions.csv                 # Clean CSV of all 4,095 Oracle ERP transactions
│   └── dashboard_data.json              # Clean JSON dataset
│
├── SA859CMS_Cost_Report_Cleaned.xlsx     # Repaired Excel file (opens in ~2s in Microsoft Excel)
├── Clean-Excel.bat                      # 1-click native Windows batch file (No Python needed)
├── Clean-Excel.ps1                      # Windows PowerShell engine powering the batch file
│
└── python_tools/                        # [Development Archive] Python exploration scripts (not needed on office laptop)
```

---

## 💼 Commercial Highlights (Week 13)

- **Revenue**: PJTD SAR 963,798 / Baseline SAR 20,405,191 (4.7%)
- **Burdened Cost**: PJTD SAR 692,231 / Baseline SAR 14,103,573 (4.9%)
- **Gross Margin**: **28.18%** vs. **30.88%** budget target (2.7% margin erosion)
- **Weekly Burn**: 240.65 hrs / SAR 53,248.52 per week
- **Working Capital**: Unbilled WIP SAR 697,713 | AR: SAR 0
- **WWOA Facility**: 73.8% consumed (SAR 692,231 of SAR 937,500 approved)


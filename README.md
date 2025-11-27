# ⚡ Forecasting UK Battery Electric Vehicle (BEV) Adoption to 2035  
*A Time-Series & Machine Learning Analysis for a Master's Dissertation*  

<img width="2752" height="1536" alt="unnamed (2)" src="https://github.com/user-attachments/assets/e2fb0405-f62c-4961-bc6e-d0c474d69791" />


---

## 📖 Project Overview
This repository contains the **code, datasets, and analytical workflow** for my MSc Business Analytics dissertation project.  
The study forecasts **Battery Electric Vehicle (BEV) adoption in the United Kingdom** up to **2035**, combining **statistical time-series models** and **machine learning** within the **CRISP-DM framework**.

### 🔑 Key Findings
- ✅ **SARIMAX** model delivers the most statistically accurate **short-term forecasts**, outperforming Prophet, LightGBM, and baseline regression.  
- 📈 **Google Trends (public interest)** is the most significant **leading indicator** of BEV demand.  
- ⚡ Charging infrastructure and household income effects **diminish** as the market matures.  
- 🚦 UK is projected to **miss the 2030 Zero Emission Vehicle (ZEV) mandate** of 80% BEV market share, achieving it in **late 2031** under optimistic scenarios.  

   *An accompanying interactive Dash dashboard translates these findings into decision-ready visuals for executives (interactive dashboard: https://ev-adoption-analysis-dashboard.onrender.com/)*.
---

## 📂 Project Directory Structure
*All the code files are run in the particular order as shown below for the best results.*

*Modelling_Scenario_RQ_Analysis.ipynb file contains all the modelling, scenario analysis and research question analysis.*
```text
Masters_Dissertation/
│
├── 📁 Datasets/  
│   └── Raw & processed datasets  
│
├── 📁 Code Files/  
│   │
│   ├── 📁 Analysis and Modelling Code Files/  
│   │   ├── 1_final_merged.ipynb                Data Consolidation  
│   │   ├── 2_EDA.ipynb                         Initial Exploration & Visualisation  
│   │   ├── 3_Feature_selection_Feature_Engg.ipynb   Feature Selection & PCA  
│   │   ├── 4_Data_Engineering.ipynb            Lag & Rolling Feature Creation  
│   │   ├── 5_EDA_Final.ipynb                   Advanced EDA & Driver Analysis  
│   │   ├── 6_Modelling_Scenario_RQ_Analysis.ipynb   Forecasting Models & Scenarios and Hypothesis Testing (ITS, Granger)    
│   │
│   └── 📁 Independent variables data cleaning code files/  
│       └── Cleaning scripts for raw datasets  
│
└── 📄 README.md

```

---

## ⚙️ Methodology
The workflow follows a **structured five-phase pipeline**:

1. **Data Collection & Merging** 📊  
   Aggregated monthly BEV registrations + economic, infrastructure, and behavioral indicators.  

2. **Exploratory Analysis & Feature Engineering** 🔍  
   - Time-series decomposition, ADF tests, correlations.  
   - PCA, lag/rolling features to capture temporal dependencies.  

3. **Model Development & Comparison** 🤖  
   - Benchmarked **Linear Regression, SARIMAX, Prophet, LightGBM**.  
   - Out-of-sample evaluation → **SARIMAX champion model**.  

4. **Research Question Analysis** 📑  
   - **Interrupted Time Series (ITS)**, **Granger Causality**, and **LOESS smoothing**.  

5. **Hybrid Forecasting & Scenario Analysis** 🔮  
   - **Short-Term (2024–2027):** SARIMAX baseline + economic stress.  
   - **Long-Term (to 2035):** Logistic Growth (S-curve) with four strategic adoption paths.  

![Workflow Diagram](assets/methodology_workflow.png) <!-- Example workflow graphic -->

---


## 🚀 How to Run the Code
To replicate the analysis, follow these steps:

1. Clone the repository:

git clone [https://github.com/AshishSiwach/Masters_Dissertation.git](https://github.com/AshishSiwach/Masters_Dissertation.git)
cd Masters_Dissertation

2. Set up a Python environment:
It is recommended to use a virtual environment.

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install dependencies:

pip install pandas numpy matplotlib seaborn statsmodels pmdarima prophet lightgbm scikit-learn jupyter

---

📚 Data Sources

All data is public, aggregated, and anonymized, from authoritative sources:

🚗 BEV Registrations: UK Department for Transport (DfT), Table VEH1153.

📉 Economic Indicators: ONS (Real Household Disposable Income, CPI).

⛽ Fuel Prices: Department for Energy Security and Net Zero (DESNZ).

🌐 Public Interest: Google Trends ("electric car").

⚡ Charging Infrastructure: DfT statistical releases.

🏛 Policy Data: Historical Plug-in Car Grant (PiCG) values from UK Government announcements.

*Note: To deploy the Dash Python dashboard on Render, a separate repository (https://github.com/AshishSiwach/EV_Adoption_Dashboard.git) was created.*

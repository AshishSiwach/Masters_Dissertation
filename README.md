Forecasting UK Battery Electric Vehicle (BEV) Adoption to 2035
A Time-Series Analysis for a Master's Dissertation
<p align="center">
<img src="image_c892b5.png" alt="BEV Forecast" width="800"/>
</p>

Project Overview
This repository contains the code and analytical workflow for a Master's dissertation project focused on forecasting the adoption of Battery Electric Vehicles (BEVs) in the United Kingdom through 2035. The study employs a hybrid forecasting model, combining statistical time-series analysis with machine learning, grounded in the CRISP-DM framework.

The key findings indicate that:

A SARIMAX model provides the most statistically accurate short-term forecasts, outperforming Prophet, LightGBM, and a baseline regression model.

Public interest (measured via Google Trends) is the most significant leading indicator of BEV demand, while the direct impact of charging infrastructure and household income shows diminishing returns in the market's mature phase.

Under current trajectories, the UK is projected to miss its 2030 Zero Emission Vehicle (ZEV) mandate of 80% market share, achieving this milestone in late 2031 even under the most optimistic scenarios.

Project Directory Structure
The repository is organized into two main folders: Datasets and Code Files. The notebooks for the core analysis are located in Code Files/Analysis and Modelling Code Files and are designed to be run sequentially.

Masters_Dissertation/
│
├── Datasets/
│   └── (All raw and processed dataset files)
│
├── Code Files/
│   │
│   ├── Analysis and Modelling Code Files/
│   │   ├── 1_final_merged.ipynb       # Data Consolidation
│   │   ├── 2_EDA.ipynb                # Initial Exploration & Visualization
│   │   ├── 3_Feature_selection_Feature_Engg.ipynb # Feature Selection & PCA
│   │   ├── 4_Data_Engineering.ipynb   # Lag/Rolling Feature Creation
│   │   ├── 5_EDA_Final.ipynb          # Advanced EDA & Driver Analysis
│   │   ├── 6_Modelling_Scenario_Analysis_Copy.ipynb # Forecasting Models & Scenarios
│   │   └── 7_Research_Questions_Analysis.ipynb # Hypothesis Testing (ITS, Granger)
│   │
│   └── Independent variables data cleaning code files/
│       └── (Notebooks for cleaning individual raw datasets)
│
└── README.md

Methodology
The project follows a structured five-phase analytical workflow:

Data Collection and Merging: Aggregated monthly data from public sources.

Exploratory Analysis & Feature Engineering: Used decomposition, ADF tests, and correlation analysis to understand data properties. Engineered features using PCA, lagging, and rolling statistics.

Model Development and Comparison: Performed a rigorous out-of-sample evaluation of four distinct models (Linear Regression, SARIMAX, Prophet, LightGBM) to identify the champion model for short-term forecasting.

Research Question Analysis: Employed quasi-experimental (ITS) and advanced statistical methods (Granger Causality, LOESS) to quantify the impact of specific drivers.

Hybrid Forecasting and Scenario Analysis:

Short-Term (2024-2027): Used the champion SARIMAX model to forecast registrations under baseline and economic stress scenarios.

Long-Term (to 2035): Used a Logistic Growth (S-curve) model to forecast market share under four strategic scenarios.

How to Run the Code
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

4. Run the notebooks:
Execute the Jupyter notebooks in the Code Files/Analysis and Modelling Code Files/ directory in their numbered order to ensure dependencies from data creation and feature engineering are met.

Data Sources
This study uses exclusively public, anonymized, and aggregated data from the following authoritative sources.

BEV Registrations: UK Department for Transport (DfT), table VEH1153.

Economic Indicators: Office for National statistics (ONS) for Real Household Disposable Income (RHDI) and Consumer Price Index (CPI).

Fuel Prices: Department for Energy Security and Net Zero (DESNZ).

Public Interest: Google Trends for search terms related to "electric car".

Charging Infrastructure: DfT statistical releases on public charging points.

Policy Data: Historical Plug-in Car Grant (PiCG) values compiled from government announcements.

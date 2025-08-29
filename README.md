# Gauss-Markov-BTC-Analysis

This project explores the econometric and machine learning modeling of **Bitcoin (BTC/USD)** using key macro-financial variables.  
We test the **Gauss-Markov assumptions** (linearity, homoskedasticity, no autocorrelation, no perfect multicollinearity, and normality of residuals) to verify when OLS estimators satisfy the **BLUE (Best Linear Unbiased Estimator)** properties.  
Additionally, we apply **Random Forest regression** and **Partial Dependence Plots (PDP/ICE)** to capture non-linear relationships and compare the results with classical OLS.

---

## Variables and Data Sources

- **Bitcoin (BTC/USD)**  
- **XAU/USD** – Gold Spot Price in US Dollars  
- **S&P500 (SPX)** – US stock market index  
- **Federal Funds Effective Rate (FEDFUNDS)** – US interest rate (FRED)  
- **US Dollar Index (DXY)** – strength of USD relative to a basket of currencies  
- **CPI-U (All Urban Consumers, All Items)** – US Consumer Price Index (FRED)  

---

## Model Notation

- $B_t$ : Bitcoin price  
- $G_t$ : Gold price  
- $S_t$ : S&P500 index  
- $D_t$ : US Dollar Index (DXY)  
- $\pi_t$ : CPI (inflation measure)  
- $r_t$ : Federal Funds Rate  

---

## Data Coverage

- Period: **01.01.2015 – 01.07.2025**  
- Frequency: **Monthly observations**  
- Sources: **Investing.com** (BTC, Gold, S&P500, DXY) and **FRED** (FEDFUNDS, CPI-U)  

---

## Main Findings

- **OLS Analysis**:  
  - ΔSPX has a strong, statistically significant effect on ΔBTC/USD.  
  - Other variables (Gold, CPI, DXY, FEDFUNDS) have weaker or heterogeneous effects.  
  - Homoskedasticity and autocorrelation issues were detected, corrected with **White and Newey–West robust errors**.  

- **Machine Learning (Random Forest)**:  
  - Feature importance confirms SPX as the strongest driver of Bitcoin returns.  
  - PDP/ICE plots show positive non-linear response to SPX, while effects of CPI, Gold, DXY, and FEDFUNDS remain weaker.  

---

## License
This project is licensed under the **MIT License** – free to use, modify, and distribute with attribution.

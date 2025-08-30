# Gauss-Markov-BTC-Analysis

This project combines **econometric methods** and **machine learning approaches** to analyze the relationship between **Bitcoin (BTC/USD)** and key macro-financial variables.  

We begin by testing the **Gauss-Markov assumptions** to assess whether Ordinary Least Squares (OLS) estimators can be considered **BLUE (Best Linear Unbiased Estimators)**. When these conditions fail, we extend the analysis with **Random Forest regression**, **Partial Dependence Plots (PDP/ICE)**, and additional time-series correlation methods.  

---

## Variables and Data Sources

- **Bitcoin (BTC/USD)** – [Investing.com](https://www.investing.com)  
- **XAU/USD (Gold)** – [Investing.com](https://www.investing.com)  
- **S&P500 (SPX)** – [Investing.com](https://www.investing.com)  
- **US Dollar Index (DXY)** – [Investing.com](https://www.investing.com)  
- **Federal Funds Effective Rate (FEDFUNDS)** – [FRED](https://fred.stlouisfed.org/series/FEDFUNDS)  
- **CPI-U (All Urban Consumers, All Items)** – [U.S. Bureau of Labor Statistics (BLS)](https://www.bls.gov/cpi/)    

**Data coverage:**  
- Period: **2015M01 – 2025M07**  
- Frequency: **Monthly observations**  
- Sources: [Investing.com](https://www.investing.com) (BTC, Gold, S&P500, DXY) and [FRED](https://fred.stlouisfed.org) (CPI-U, Fed Funds Rate)  
- Number of observations: **127 monthly entries**  

---

## Methodology

1. **Descriptive Statistics & Visualization**  
   - Summary statistics, variance, skewness, kurtosis.  
   - Time-series plots with trend inspection.  

2. **OLS Regression**  
   - Estimation of ΔBTC/USD on macro variables.  
   - Tests of Gauss-Markov assumptions:  
     - Linearity ($y = X\beta + \varepsilon$)  
     - No perfect multicollinearity ($X'X$ invertible)  
     - Exogeneity ($E[\varepsilon|X] = 0$)  
     - Homoskedasticity ($Var(\varepsilon|X) = \sigma^2 I$)  
     - No autocorrelation ($Cov(\varepsilon_t, \varepsilon_s)=0, \; t \neq s$)  
   - Robust standard errors (White HC1, Newey–West HAC) applied when needed.  

3. **Correlation Analysis**  
   - BTC vs SPX levels: extremely high correlation ($\rho \approx 0.94$).  
   - BTC vs SPX log-returns: moderate correlation ($\rho \approx 0.24 – 0.36$).  
   - Rolling correlation plots show time-varying dependence.  

4. **Granger Causality**  
   - Tested whether SPX returns predict BTC returns.  
   - Across 1–6 lags, **no statistical evidence of causality** (p-values > 0.05).  
   - Interpretation: BTC and SPX co-move due to common risk sentiment rather than direct causal link.  

5. **Machine Learning (Random Forest)**  
   - Feature importance: ΔSPX strongest driver of ΔBTC/USD.  
   - PDP/ICE plots:  
     - ΔSPX shows strong monotonic positive effect.  
     - ΔCPI-U, ΔDXY, ΔXAU/USD, ΔFEDFUNDS show weak or unstable patterns.  

6. **Error & Robustness Checks**  
   - Residual distribution histograms (fat-tailed, non-normal).  
   - Rolling correlations confirm regime shifts in BTC–SPX relationship.  

---

## Key Findings

- **BTC behaves more like a “risk-on” asset**, strongly tied to equity markets rather than inflation, interest rates, or gold.  
- **SPX returns (ΔSPX) are the only robust driver** of Bitcoin returns across both econometric and machine learning frameworks.  
- The co-movement in levels is trend-driven; short-term dynamics reveal only moderate dependence.  
- Granger causality confirms **no predictive causal effect** from SPX to BTC.  
- Machine learning methods (Random Forest, PDP/ICE) complement OLS by capturing **non-linear effects** and enhancing interpretability.  

---

## License
This project is licensed under the **MIT License** – free to use, modify, and distribute with attribution.  

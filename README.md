# Gauss-Markov-BTC-Analysis  
[![View Project](https://img.shields.io/badge/View_Project-517FF7)](https://github.com/mikbalyilmaz/Gauss-Markov-BTC-Analysis)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  

This project integrates **econometric techniques** and **machine learning approaches** to analyze the relationship between **Bitcoin (BTC/USD)** and major macro-financial variables.  

We begin by testing the **Gauss–Markov assumptions** to assess whether OLS estimators can be considered **BLUE (Best Linear Unbiased Estimators)**. When these assumptions fail, the analysis is extended with **Random Forest regression**, **Partial Dependence Plots (PDP/ICE)**, and additional time-series methods.  

---

## Variables and Data Sources

- **Bitcoin (BTC/USD)** – [Investing.com](https://www.investing.com)  
- **XAU/USD (Gold)** – [Investing.com](https://www.investing.com)  
- **S&P500 (SPX)** – [Investing.com](https://www.investing.com)  
- **US Dollar Index (DXY)** – [Investing.com](https://www.investing.com)  
- **Federal Funds Effective Rate (FEDFUNDS)** – [FRED](https://fred.stlouisfed.org/series/FEDFUNDS)  
- **CPI-U (All Urban Consumers, All Items)** – [BLS](https://www.bls.gov/cpi/)    

**Data coverage:**  
- Period: **2015M01 – 2025M07**  
- Frequency: **Monthly**  
- Sources: [Investing.com](https://www.investing.com), [FRED](https://fred.stlouisfed.org)  
- Observations: **127 monthly entries**  

---

## Methodology

1. **Descriptive Statistics & Visualization**  
   - Summary stats, variance, skewness, kurtosis.  
   - Time-series plots with trend inspection.  

2. **OLS Regression**  
   - Regression of ΔBTC/USD on macro variables.  
   - Gauss–Markov tests: linearity, multicollinearity, exogeneity, homoskedasticity, autocorrelation.  
   - Robust errors (White HC1, Newey–West HAC) applied when needed.  

3. **Correlation Analysis**  
   - BTC vs SPX levels: strong correlation (\(\rho \approx 0.94\)).  
   - BTC vs SPX returns: moderate correlation (\(\rho \approx 0.24 – 0.36\)).  
   - Rolling correlation plots show time-varying dependence.  

4. **Granger Causality**  
   - Tested predictive power of SPX returns on BTC returns.  
   - No significant causality (p > 0.05).  
   - Interpretation: co-movement driven by risk sentiment, not causality.  

5. **Machine Learning (Random Forest)**  
   - Feature importance: ΔSPX is the dominant driver.  
   - PDP/ICE plots reveal strong monotonic effects for ΔSPX, weaker patterns for others.  

6. **Robustness Checks**  
   - Residual histograms: fat tails, non-normality.  
   - Rolling correlations confirm regime shifts.  

---

## Key Findings

- **BTC acts as a “risk-on” asset**, highly tied to equity markets rather than inflation, interest rates, or gold.  
- **SPX returns are the only consistent driver** of BTC returns across both OLS and ML models.  
- Co-movement in levels is trend-driven, while short-term dynamics show moderate dependence.  
- No evidence of Granger causality from SPX to BTC.  
- ML methods enhance OLS by capturing **non-linearities** and improving interpretability.  

---

## License
 © Licensed under the **MIT License** – free to use, modify, and distribute with attribution.  

---

## Future Improvements

- **Time Series Cross-Validation** (rolling/expanding windows).  
- **Lag Structures** (1–3 months).  
- **Cointegration & VECM** (Johansen/Engle–Granger).  
- **Structural Break Tests** (Bai–Perron, Markov-switching).  
- **Robust Inference** (bootstrap, quantile regression).  
- **Feature Engineering** (volatility, macro regimes, crypto metrics).  
- **Model Comparison** (Diebold–Mariano tests).  
- **Explainability** (permutation importance, SHAP values).  

---

## How to Cite  

> Yılmaz, M. İ. (2025). *Gauss-Markov-BTC-Analysis*. GitHub. https://github.com/mikbalyilmaz/Gauss-Markov-BTC-Analysis  

**APA citation:**  
Yılmaz, M. İ. (2025). *Gauss-Markov-BTC-Analysis*. GitHub. Retrieved September 3, 2025, from https://github.com/mikbalyilmaz/Gauss-Markov-BTC-Analysis  

**BibTeX:**  

```bibtex
@misc{gauss_markov_btc_2025,
  author       = {Muhammed İkbal Yılmaz},
  title        = {Gauss-Markov-BTC-Analysis},
  year         = {2025},
  howpublished = {\url{https://github.com/mikbalyilmaz/Gauss-Markov-BTC-Analysis}},
  note         = {Accessed: 2025-09-03}
}

# 🦆 DuckIO — A/B Testing a Call-to-Action Button

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An end-to-end A/B testing project demonstrating experiment design, data collection, statistical analysis, and business recommendation for a landing page call-to-action button.

<p align="center">
  <img src="https://github.com/YVandana/A-B-Testing-a-Call-To-Action-Button/blob/main/outputs/conversion_rates.png" alt="Conversion Rates">
  
  <img src="https://github.com/YVandana/A-B-Testing-a-Call-To-Action-Button/blob/main/outputs/bayesian_posterior.png" alt="Bayesian Posterior">
</p>

---

## Table of Contents

- [Project Overview](#project-overview)
- [Experiment Design](#experiment-design)
- [Results Summary](#results-summary)
- [Methodology](#methodology)
- [Key Findings](#key-findings)
- [Technologies Used](#technologies-used)

---

## Project Overview

DuckIO is a fictional crafting newsletter platform. This project tests whether changing the landing page's call-to-action (CTA) button text and color affects user sign-up conversion rates.

**Business Question:** *Will changing the CTA button from "Start First Free Month" (Light Sea Green) to "Join The Community!" (Plum) increase newsletter sign-ups?*

### What This Project Demonstrates

- **Experiment Design** — Hypothesis formulation, metrics selection, sample size planning
- **Live A/B Testing App** — Bare-bones Streamlit web application with randomized variant assignment
- **Data Collection** — SQLite event logging with session management
- **Statistical Analysis** — Frequentist hypothesis testing + Bayesian inference
- **Data Visualization** — Conversion rate comparisons, cumulative trends, posterior distributions
- **Business Recommendation** — Actionable insights from statistical results

---

## Experiment Design

| Component | Detail |
|-----------|--------|
| **Hypothesis (H₁)** | The treatment button will increase conversion rate compared to control |
| **Null Hypothesis (H₀)** | There is no difference in conversion rates between variants |
| **Primary Metric** | Conversion Rate = Unique Clicks / Unique Page Views |
| **Randomization Unit** | User session (deterministic hash-based assignment) |
| **Significance Level (α)** | 0.05 |
| **Statistical Power** | 0.80 |
| **Test Duration** | 7 days (simulated) |

### Variants

| Variant | Button Text | Button Color |
|---------|-------------|--------------|
| **Control** | "Start First Free Month" | LightSeaGreen |
| **Treatment** | "Join The Community!" | Plum |

---

## Results Summary

> **The treatment variant showed a statistically and practically significant improvement in conversion rate.**

| Metric | Control | Treatment | Lift |
|--------|---------|-----------|------|
| **Sample Size** | 4,997 | 5,003 | — |
| **Conversions** | 469 | 585 | — |
| **Conversion Rate** | 9.39% | 11.69% | **+2.31 pp** |
| **Relative Improvement** | — | — | **+24.6%** |

### Statistical Significance

| Test | Result | Conclusion |
|------|--------|------------|
| **Two-Proportion Z-Test** | z = 3.76, p = 0.0002 | ✅ Highly significant (p < 0.001) |
| **95% Confidence Interval** | [+1.10%, +3.51%] | Entirely above zero |
| **Bayesian Posterior** | P(Treatment > Control) > 99.9% | Near certainty |

### Recommendation

> **Roll out the treatment variant.** The plum "Join The Community!" button is projected to generate approximately **231 additional conversions per 10,000 visitors** compared to the original design.
---

## Methodology

### Variant Assignment

Users are assigned deterministically using SHA-256 hashing of their session ID, ensuring:

  Consistency — Same session always sees the same variant
  Reproducibility — Assignment is deterministic, not random
  Balance — Approximately 50/50 split

### Data Collection

Every page view and button click is logged to SQLite with:
  
  session_id — Unique per browser tab
  variant — "control" or "treatment"
  event_type — "view" or "click"
  timestamp — UTC ISO format

### Statistical Analysis
**Frequentist Approach:**

- Two-proportion z-test for hypothesis testing
- 95% confidence interval for the conversion rate difference
- Sample size validation and sanity checks

**Bayesian Approach:**

- Beta-Binomial model with uninformative Beta(1,1) priors
- Markov Chain Monte Carlo (MCMC) sampling via PyMC
- Posterior probability that treatment outperforms control

**Guardrail Metrics (for production)**

- Bounce rate monitoring
- Time-on-page analysis
- Segment-level effects (browser, device, time of day)
---

## Key Findings

1. The treatment variant clearly outperformed control with a 24.6% relative improvement in conversion rate.(p = 0.0002)
2. Both frequentist and Bayesian methods agree — the evidence strongly supports rolling out the new design.
3. The confidence interval [+1.10%, +3.51%] is entirely positive, meaning even the worst-case scenario shows improvement.
4. Business impact is meaningful — projected 231 additional sign-ups per 10,000 visitors.

---

## Technologies Used

| Technology | Purpose |
|-----------|--------|
| Python 3.11+ | Core programming language |
| Streamlit	| Interactive web application framework |
| SQLite | Lightweight database for event logging |
| Pandas & NumPy	| Data manipulation and analysis |
| SciPy & Statsmodels |	Statistical hypothesis testing |
| PyMC & ArviZ	| Bayesian inference and MCMC sampling |
| Matplotlib & Seaborn	| Data visualization |
| hashlib	| Deterministic variant assignment |

---

## Reflections


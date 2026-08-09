import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymc as pm
import arviz as az


from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Code/app
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) # Goes up 2 levels to project root

DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'experiment.db')
OUTPUT_DIR = os.path.join(PROJECT_ROOT,'outputs')

os.makedirs(OUTPUT_DIR, exist_ok = True)

# Loading Data
conn = sqlite3.connect(DB_PATH)
events = pd.read_sql_query('SELECT * from events', conn)
conn.close()


# Converting timestamp to Datetime
events['timestamp'] = pd.to_datetime(events['timestamp'])


# Pivot to get one row per session with views and clicks
views = events[events['event_type'] == 'view' ].set_index('session_id')
clicks = events[events['event_type'] == 'click' ].set_index('session_id')


# Merging to keep sessions that had a view
df = views[['variant', 'timestamp']].join(clicks[['timestamp']], how = 'left', rsuffix = '_click')
df['converted'] = df['timestamp_click'].notna().astype(int)
df = df.rename(columns ={ 'timestamp': 'view_time'})


# Sanity Checks
print('Sanity Checks')
print(f'Total sessions: {len(df)}')
print(f'Sessions per variant: \n{df['variant'].value_counts()}')


# Check for multiple clicks per session
multi_click = clicks.index.value_counts()
if any(multi_click > 1):
    print(f'Warning: {sum(multi_click > 1)} sessions clicked more than once. Keeping first click only.')

    # Already handled by join (left join takes first if multiple clicks exist). Check if needed.

print('Assignment balance (should be ~ 50/50):')
print(df['variant'].value_counts(normalize = True))


# Calculate Metrics
summary = df.groupby('variant').agg(
    total_views = ('converted', 'count'),
    clicks = ('converted', 'sum')   
)

summary['conversion_rate'] = summary['clicks']/ summary['total_views']
print('\n-------- Summary Statistics --------')
print(summary)

control = df[df['variant'] == 'control']
treatment = df[df['variant'] == 'treatment']

n_c = control.shape[0]
n_t = treatment.shape[0]
conv_c = control['converted'].sum()
conv_t = treatment['converted'].sum()


# Frequentist Statistical Test
z_stat, p_value = proportions_ztest([conv_t, conv_c], [n_t, n_c], alternative = 'two-sided')
diff = conv_t/n_t - conv_c/n_c
ci_low, ci_high = proportion_confint(conv_t, n_t, alpha = 0.05), proportion_confint(conv_c, n_c, alpha = 0.05)

# Confidence Interval for the difference
se = np.sqrt((((conv_t/n_t)*(1 - conv_t/n_t))/n_t) + (((conv_c/n_c)*(1 - conv_c/n_c))/n_c))
ci_diff_low = diff - 1.96*se
ci_diff_high = diff + 1.96*se

print('-------- A/B Test Results --------')
print(f'Control Conversion: {conv_c/n_c:.4f}  ({conv_c}/{n_c})')
print(f'Treatment Conversion: {conv_t/n_t:.4f}  ({conv_t}/{n_t})')
print(f'Lift (absolute): {diff:.4f}')
print(f'95% CI for lift: [{ci_diff_low:.4f}, {ci_diff_high:.4f}]')
print(f'Z-Stastic: {z_stat:.4f}, p-value: {p_value:.4f}')


# Visualisations
sns.set_style('whitegrid')

# Bar Plot of Conversion Rates
fig, ax = plt.subplots(figsize = (6, 4))
sns.barplot(x = 'variant',
            y= 'conversion_rate',
            data = summary.reset_index(),
            hue = 'variant',
            palette = {'control': 'LightSeaGreen', 'treatment': 'plum'},
            legend = False,
            ax = ax
            )
ax.set_title('Conversion Rate by Variant')
ax.set_ylabel('Conversion Rate')
ax.set_xlabel('Variant')
for i, row in summary.iterrows():
    ax.text(i, row['conversion_rate'] + 0.002, f'{row['conversion_rate']:.3f}', ha = 'center')

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'conversion_rates.png'), dpi = 300)
plt.close()

# Cummulative conversion over time (by view order)
df_sorted = df.sort_values('view_time')
df_sorted['cum_views'] = 1
df_sorted['cum_clicks'] = df_sorted['converted']
df_sorted['cum_views'] = df_sorted.groupby('variant')['cum_views'].cumsum()
df_sorted['cum_clicks'] = df_sorted.groupby('variant')['cum_clicks'].cumsum()
df_sorted['cum_rate'] = df_sorted['cum_clicks']/df_sorted['cum_views']

fig, ax = plt.subplots(figsize=(10, 5))
for var in ['control', 'treatment']:
    subset = df_sorted[df_sorted['variant'] == var]
    ax.plot(subset['cum_views'], subset['cum_rate'], label = var)

ax.set_xlabel('Number of Sessions')
ax.set_ylabel('Cumulative Conversion Rate')
ax.set_title('Cumulative Conversion Rate Over Time')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'cumulative_conversion.png'), dpi = 300)
plt.close()


# Reccomendation
alpha = 0.05
print('-------- Business Reccomendation --------')
if p_value < alpha:
    if diff > 0:
        print("Statistically Significant: Treatment WINS. Reccomend rolling the Plum Button 'Join the Community!'.")
    else:
        print("Statistically Significant: CONTROL WINS. Keep the Sea Green button 'Start First Free Month!'.")
else:
    print('Stastically Not Significant. Consider running the rest longer or trying a different change.')
'''
# ---------- 6. Bayesian Analysis ----------
try:
    import pymc as pm
    import arviz as az
    
    print("\n===== Bayesian Analysis =====")
    with pm.Model() as model:
        # Weak priors (Beta(1,1) = uniform)
        p_control = pm.Beta("p_control", alpha=1, beta=1)
        p_treatment = pm.Beta("p_treatment", alpha=1, beta=1)
        
        # Likelihood
        pm.Binomial("obs_control", n=n_c, p=p_control, observed=conv_c)
        pm.Binomial("obs_treatment", n=n_t, p=p_treatment, observed=conv_t)
        
        # Difference (treatment - control)
        delta = pm.Deterministic("delta", p_treatment - p_control)
        
        # Sample
        trace = pm.sample(2000, tune=1000, cores=1, random_seed=42, 
                         progressbar=True)
    
    # FIXED: Use plot_posterior (works across versions) or handle new API
    try:
        # Try new API first (arviz >= 0.20)
        az.plot_posterior(trace, var_names=["delta"], ref_val=0, figsize=(8, 4))
    except (AttributeError, TypeError):
        try:
            # Fallback for newer versions
            az.plot_prior_posterior(trace, var_names=["delta"], ref_val=0, figsize=(8, 4))
        except:
            # Last resort: manual plot
            import matplotlib.pyplot as plt
            delta_samples = trace.posterior["delta"].values.flatten()
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(delta_samples, bins=50, color='plum', edgecolor='white', alpha=0.7)
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No difference')
            ax.axvline(x=delta_samples.mean(), color='LightSeaGreen', linewidth=2, label=f'Mean: {delta_samples.mean():.4f}')
            ax.set_xlabel('Lift (Treatment - Control)')
            ax.set_ylabel('Frequency')
            ax.set_title('Posterior Distribution of Lift')
            ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "bayesian_posterior.png"))
    plt.close()
    print("✅ Saved: bayesian_posterior.png")
    
    # Probability treatment is better
    delta_samples = trace.posterior["delta"].values.flatten()
    prob_better = (delta_samples > 0).mean()
    print(f"Probability treatment is better: {prob_better:.2%}")
    
except ImportError:
    print("\n⚠️  pymc/arviz not installed. Skipping Bayesian analysis.")
    print("   Install with: pip install pymc arviz")

'''
# Bayesian Analysis
with pm.Model() as model:
    # Prior: Beta(1, 1) uniform

    p_control = pm.Beta('p_control', alpha = 1, beta = 1)
    p_treatment = pm.Beta('p_treatment', alpha = 1, beta = 1)

    # Likelihood
    pm.Binomial('obs_control', n =  n_c, p = p_control, observed = conv_c)
    pm.Binomial('obs_treatment', n = n_t, p = p_treatment, observed = conv_t)

    # Difference
    delta = pm.Deterministic('delta', p_treatment - p_control)
    trace = pm.sample(2000, tune = 1000, cores = 1, random_seed = 42)

#az.plot_prior_posterior(trace, var_names = ['delta'], ref_val = 0, figsize = (8, 4))
delta_samples = trace.posterior['delta'].values.flatten()
fig, ax = plt.subplots(figsize = (8, 4))
ax.hist(delta_samples, bins = 50, color = 'plum', edgecolor = 'white', alpha = 0.7)
ax.axvline(x = 0, color = 'red', linestyle = '--', linewidth = 2, label = 'No difference')
ax.axvline(x = delta_samples.mean(), color = 'LightSeaGreen', linewidth = 2, label = f'Mean: {delta_samples.mean():.4f}')
ax.set_xlabel('Lift (Treatment - Control)')
ax.set_ylabel('Frequency')
ax.set_title('Posterior Distribution of Lift')
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'bayesian_posterior.png'), dpi = 300)
plt.close()
print('Saved Bayesian Plot as bayesian_posterior.png')


delta_samples = trace.posterior['delta'].values.flatten()
prob_better = (delta_samples > 0).mean().item()
print(f'Probability treatment is better: {prob_better:.2f}')


# Report

report = f'''
A/B Test Report - CTA Button Experiment
---------------------------------------

Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Sessions: {len(df)}
Control Sessions: {n_c}, Treatment Sessions: n_t

Conversion Rates:
- Control: {conv_c/n_c:.4f} ({conv_c} clicks / {n_c} views)
- Treatment: {conv_t/n_t:.4f} ({conv_t} clicks / {n_t} views)
- Absolute Lift: {diff:.4f}
- Realtive Lift: {(diff/(conv_c/n_c)):.2f}
- 95% CI for difference" [{ci_diff_low:.4f}, {ci_diff_high:.4f}]
- p-value: {p_value:.4f}

Statstical Test: Two-proportion z-test (two-sided), alpha = 0.05
Conclusion: {'Significant' if p_value < alpha else 'Not Significant'}
'''

with open(os.path.join(OUTPUT_DIR, 'summary.txt'), 'w') as f:
    f.write(report)

print("\n Plots saved to 'outputs/', summary saved to 'outputs/summary.txt'. ")
print('Done.')
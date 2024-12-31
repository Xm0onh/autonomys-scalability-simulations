import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('simulation_results.csv')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

window = 100  
df['honest_ma'] = df['honest_votes'].rolling(window=window).mean()
df['malicious_ma'] = df['malicious_votes'].rolling(window=window).mean()

ax1.plot(df['blob_id'], df['honest_ma'], 
         label=f'Honest Votes (MA-{window})', color='green', linewidth=2)
ax1.plot(df['blob_id'], df['malicious_ma'], 
         label=f'Malicious Votes (MA-{window})', color='red', linewidth=2)

ax1.plot(df['blob_id'], df['honest_votes'], 
         color='lightgreen', alpha=0.2, linewidth=0.5)
ax1.plot(df['blob_id'], df['malicious_votes'], 
         color='lightcoral', alpha=0.2, linewidth=0.5)

ax1.set_xlabel('Blob ID')
ax1.set_ylabel('Number of Votes')
ax1.set_title('Voting Pattern: Moving Average of Honest vs Malicious Nodes')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)

data_to_plot = [df['honest_votes'], df['malicious_votes']]
box = ax2.boxplot(data_to_plot, 
                  labels=['Honest Votes', 'Malicious Votes'],
                  patch_artist=True)

colors = ['lightgreen', 'lightcoral']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

ax2.set_ylabel('Number of Votes')
ax2.set_title('Vote Distribution Statistics')
ax2.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('voting_pattern_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nDetailed Statistics:")
print("\nHonest Votes:")
print(f"Mean: {df['honest_votes'].mean():.2f}")
print(f"Median: {df['honest_votes'].median():.2f}")
print(f"Std Dev: {df['honest_votes'].std():.2f}")
print(f"Min: {df['honest_votes'].min()}")
print(f"Max: {df['honest_votes'].max()}")

print("\nMalicious Votes:")
print(f"Mean: {df['malicious_votes'].mean():.2f}")
print(f"Median: {df['malicious_votes'].median():.2f}")
print(f"Std Dev: {df['malicious_votes'].std():.2f}")
print(f"Min: {df['malicious_votes'].min()}")
print(f"Max: {df['malicious_votes'].max()}")

print(f"\nTotal blobs: {len(df)}")
print(f"Confirmed blobs: {df['confirmed'].sum()}")
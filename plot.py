import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read the CSV file
df = pd.read_csv('simulation_results.csv')

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Plot 1: Votes per block
block_stats = df.groupby('block_number').agg({
    'blob_id': 'count',
    'votes': lambda x: x.str.count('1').mean()  # Average positive votes
}).reset_index()

ax1.plot(block_stats['block_number'], block_stats['votes'], 
         label='Average Positive Votes', color='blue')
ax1.set_xlabel('Block Number')
ax1.set_ylabel('Average Number of Positive Votes')
ax1.set_title('Voting Pattern Over Blocks')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)

# Plot 2: Distribution of votes
df['positive_votes'] = df['votes'].str.count('1')
df['total_possible'] = df['votes'].str.len()
df['vote_ratio'] = df['positive_votes'] / df['total_possible']

sns.boxplot(y=df['vote_ratio'], ax=ax2)
ax2.set_ylabel('Ratio of Positive Votes')
ax2.set_title('Distribution of Vote Ratios')
ax2.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('voting_pattern_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# Print statistics
print("\nVoting Statistics:")
print(f"Total Blocks: {df['block_number'].nunique()}")
print(f"Total Blobs: {len(df)}")
print(f"Average Blobs per Block: {len(df) / df['block_number'].nunique():.2f}")

print("\nVote Distribution:")
print(f"Average Positive Votes per Blob: {df['positive_votes'].mean():.2f}")
print(f"Median Positive Votes per Blob: {df['positive_votes'].median():.2f}")
print(f"Std Dev of Positive Votes: {df['positive_votes'].std():.2f}")

print("\nVote Ratios:")
print(f"Average Ratio of Positive Votes: {df['vote_ratio'].mean():.2%}")
print(f"Median Ratio of Positive Votes: {df['vote_ratio'].median():.2%}")
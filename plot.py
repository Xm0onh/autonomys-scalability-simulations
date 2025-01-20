import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Read the text file and parse the table
with open('simulation_results.txt', 'r') as f:
    lines = f.readlines()

# Parse the table into a DataFrame
data = []
for line in lines[3:]:  # Skip header rows
    if '│' in line and not '─' in line:
        parts = line.split('│')
        if len(parts) >= 7:
            block = int(parts[1].strip())
            proposer_info = parts[2].strip()
            proposer = int(proposer_info.split('(')[0])
            blob_id = int(parts[3].strip())
            votes_str = parts[4].strip()
            honest_votes = int(parts[5].strip())
            malicious_votes = int(parts[6].strip())
            
            # Create single row per blob instead of per vote
            vote_parts = votes_str.split(', ')
            vote_dict = {
                'block_number': block,
                'proposer': proposer,
                'honest_votes': honest_votes,
                'malicious_votes': malicious_votes,
                'blob_id': blob_id
            }
            # Add individual votes to the same row
            for i, vote in enumerate(vote_parts):
                vote_val = int(vote[0])  # Get the first character (0 or 1)
                vote_dict[f'vote_{i}'] = vote_val
            data.append(vote_dict)

# Create DataFrame
df = pd.DataFrame(data)

# Get vote columns
vote_columns = [col for col in df.columns if col.startswith('vote_')]
total_voters = len(vote_columns)

# Calculate total votes
df['total_votes'] = df['honest_votes'] + df['malicious_votes']

# Create results directory if it doesn't exist
os.makedirs('results', exist_ok=True)

# 1. Plot votes per block showing honest vs malicious
fig1, ax1 = plt.subplots(figsize=(15, 8))
block_votes = df.groupby('block_number').agg({
    'honest_votes': 'sum',
    'malicious_votes': 'sum'
}).reset_index()

block_votes['total_votes'] = block_votes['honest_votes'] + block_votes['malicious_votes']

ax1.plot(block_votes['block_number'], block_votes['honest_votes'], 
         label='Honest Votes', color='green', marker='o')
ax1.plot(block_votes['block_number'], block_votes['malicious_votes'], 
         label='Malicious Votes', color='red', marker='o')
ax1.plot(block_votes['block_number'], block_votes['total_votes'], 
         label='Total Votes', color='blue', marker='o')
ax1.set_xlabel('Block Number')
ax1.set_ylabel('Number of Votes')
ax1.set_title('Total Votes per Block')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/honest_malicious_votes.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Plot yes/no votes
fig2, ax2 = plt.subplots(figsize=(15, 8))
vote_columns = [col for col in df.columns if col.startswith('vote_')]
df['yes_votes'] = df[vote_columns].apply(lambda x: (x == 1).sum(), axis=1)
df['no_votes'] = df[vote_columns].apply(lambda x: (x == 0).sum(), axis=1)

yes_no_votes = df.groupby('block_number').agg({
    'yes_votes': 'sum',
    'no_votes': 'sum'
}).reset_index()

yes_no_votes['total_votes'] = yes_no_votes['yes_votes'] + yes_no_votes['no_votes']

ax2.plot(yes_no_votes['block_number'], yes_no_votes['yes_votes'], 
         label='Yes Votes', color='green', marker='o')
ax2.plot(yes_no_votes['block_number'], yes_no_votes['no_votes'], 
         label='No Votes', color='red', marker='o')
ax2.plot(yes_no_votes['block_number'], yes_no_votes['total_votes'], 
         label='Total Votes', color='blue', marker='o')
ax2.set_xlabel('Block Number')
ax2.set_ylabel('Number of Votes')
ax2.set_title('Yes/No Votes per Block')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/yes_no_votes.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Plot vote distribution
fig3, ax3 = plt.subplots(figsize=(10, 8))
vote_data = pd.melt(df[['honest_votes', 'malicious_votes', 'total_votes']])
sns.boxplot(x='variable', y='value', data=vote_data, ax=ax3)
ax3.set_xlabel('Vote Type')
ax3.set_ylabel('Number of Votes')
ax3.set_title('Vote Distribution Statistics')
ax3.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/vote_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Plot proposer distribution
fig4, ax4 = plt.subplots(figsize=(10, 8))
block_proposers = df.groupby('block_number').agg({
    'proposer': 'first'
}).reset_index()

proposer_type = ['Honest' if p < 8000 else 'Malicious' for p in block_proposers['proposer']]
proposer_counts = pd.Series(proposer_type).value_counts()

sns.barplot(x=proposer_counts.index, 
            y=proposer_counts.values,
            hue=proposer_counts.index,
            palette={'Honest': 'green', 'Malicious': 'red'},
            legend=False,
            ax=ax4)

ax4.set_xlabel('Proposer Type')
ax4.set_ylabel('Number of Blocks Proposed')
ax4.set_title('Distribution of Block Proposers')
ax4.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/proposer_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Plot voting pattern heatmap
fig5, ax5 = plt.subplots(figsize=(15, 8))
vote_matrix = df[['blob_id', 'honest_votes', 'malicious_votes']].groupby('blob_id').sum().values
sns.heatmap(vote_matrix[:100], 
            cmap='YlOrRd',
            ax=ax5,
            xticklabels=['Honest', 'Malicious'],
            cbar_kws={'label': 'Number of Votes'})
ax5.set_xlabel('Vote Type')
ax5.set_ylabel('Blob ID')
ax5.set_title('Voting Pattern Heatmap (First 100 Blobs)')
plt.tight_layout()
plt.savefig('results/voting_pattern_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# Get unique blob statistics by summing votes across all appearances
blob_stats = df.groupby('blob_id').agg({
    'honest_votes': 'sum',
    'malicious_votes': 'sum',
    'total_votes': 'sum'
}).reset_index()

# Get block statistics
block_stats = df.groupby('block_number').agg({
    'honest_votes': 'sum',
    'malicious_votes': 'sum',
    'total_votes': 'sum'
}).reset_index()

print("\nDetailed Statistics:")

print("\nPer Blob Total Votes:")
print(f"Mean: {blob_stats['total_votes'].mean():.2f}")
print(f"Median: {blob_stats['total_votes'].median():.2f}")
print(f"Std Dev: {blob_stats['total_votes'].std():.2f}")
print(f"Min: {blob_stats['total_votes'].min()}")
print(f"Max: {blob_stats['total_votes'].max()}")

print("\nPer Blob Honest Votes:")
print(f"Mean: {blob_stats['honest_votes'].mean():.2f}")
print(f"Median: {blob_stats['honest_votes'].median():.2f}")
print(f"Std Dev: {blob_stats['honest_votes'].std():.2f}")
print(f"Min: {blob_stats['honest_votes'].min()}")
print(f"Max: {blob_stats['honest_votes'].max()}")

print("\nPer Blob Malicious Votes:")
print(f"Mean: {blob_stats['malicious_votes'].mean():.2f}")
print(f"Median: {blob_stats['malicious_votes'].median():.2f}")
print(f"Std Dev: {blob_stats['malicious_votes'].std():.2f}")
print(f"Min: {blob_stats['malicious_votes'].min()}")
print(f"Max: {blob_stats['malicious_votes'].max()}")

print("\nPer Block Statistics:")
print(f"Mean honest votes: {block_stats['honest_votes'].mean():.2f}")
print(f"Mean malicious votes: {block_stats['malicious_votes'].mean():.2f}")
print(f"Mean total votes: {block_stats['total_votes'].mean():.2f}")

print(f"\nTotal blobs: {df['blob_id'].nunique()}")
print(f"Total blocks: {df['block_number'].nunique()}")
print(f"Average blobs per block: {df['blob_id'].nunique() / df['block_number'].nunique():.2f}")

print("\nVoting Patterns:")
print(f"Total voters: {len(vote_columns)}")
print(f"Total votes recorded: {df['total_votes'].sum()}")

# Calculate vote correlation matrix
vote_corr = df[vote_columns].corr()
print("\nVote Correlation Summary:")
print(f"Average Correlation between Voters: {vote_corr.mean().mean():.3f}")
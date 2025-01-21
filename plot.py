import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def read_and_parse_data(filename):
    # Read the text file and parse the table
    with open(filename, 'r') as f:
        lines = f.readlines()
    
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
                
                vote_dict = {
                    'block_number': block,
                    'proposer': proposer,
                    'honest_votes': honest_votes,
                    'malicious_votes': malicious_votes,
                    'blob_id': blob_id
                }
                # Add individual votes
                for i, vote in enumerate(votes_str.split(', ')):
                    vote_dict[f'vote_{i}'] = int(vote[0])
                data.append(vote_dict)
    
    return pd.DataFrame(data)

def plot_honest_vs_malicious(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    block_votes = df.groupby('block_number').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).reset_index()
    
    block_votes['total_votes'] = block_votes['honest_votes'] + block_votes['malicious_votes']
    
    for col, color in [('honest_votes', 'green'), ('malicious_votes', 'red'), ('total_votes', 'blue')]:
        ax.plot(block_votes['block_number'], block_votes[col], 
                label=col.replace('_', ' ').title(), color=color, marker='o')
    
    ax.set_xlabel('Block Number')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Total Votes per Block')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'honest_malicious_votes.png'))

def plot_yes_no_votes(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    vote_columns = [col for col in df.columns if col.startswith('vote_')]
    
    df['yes_votes'] = df[vote_columns].apply(lambda x: (x == 1).sum(), axis=1)
    df['no_votes'] = df[vote_columns].apply(lambda x: (x == 0).sum(), axis=1)
    
    yes_no_votes = df.groupby('block_number').agg({
        'yes_votes': 'sum',
        'no_votes': 'sum'
    }).reset_index()
    
    yes_no_votes['total_votes'] = yes_no_votes['yes_votes'] + yes_no_votes['no_votes']
    
    for col, color in [('yes_votes', 'green'), ('no_votes', 'red'), ('total_votes', 'blue')]:
        ax.plot(yes_no_votes['block_number'], yes_no_votes[col], 
                label=col.replace('_', ' ').title(), color=color, marker='o')
    
    ax.set_xlabel('Block Number')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Yes/No Votes per Block')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'yes_no_votes.png'))

def plot_vote_distribution(df, output_dir):
    fig, ax = plt.subplots(figsize=(10, 8))
    vote_data = pd.melt(df[['honest_votes', 'malicious_votes', 'total_votes']])
    sns.boxplot(x='variable', y='value', data=vote_data, ax=ax)
    ax.set_xlabel('Vote Type')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Vote Distribution Statistics')
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'vote_distribution.png'))

def plot_proposer_distribution(df, output_dir, honest_threshold=8000):
    fig, ax = plt.subplots(figsize=(10, 8))
    block_proposers = df.groupby('block_number')['proposer'].first().reset_index()
    
    proposer_type = ['Honest' if p < honest_threshold else 'Malicious' 
                     for p in block_proposers['proposer']]
    proposer_counts = pd.Series(proposer_type).value_counts()
    
    sns.barplot(x=proposer_counts.index, y=proposer_counts.values,
                hue=proposer_counts.index,
                palette={'Honest': 'green', 'Malicious': 'red'},
                legend=False, ax=ax)
    
    ax.set_xlabel('Proposer Type')
    ax.set_ylabel('Number of Blocks Proposed')
    ax.set_title('Distribution of Block Proposers')
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'proposer_distribution.png'))

def plot_voting_pattern_heatmap(df, output_dir, num_blobs=100):
    fig, ax = plt.subplots(figsize=(15, 8))
    vote_matrix = df[['blob_id', 'honest_votes', 'malicious_votes']].groupby('blob_id').sum().values
    
    sns.heatmap(vote_matrix[:num_blobs], 
                cmap='YlOrRd',
                ax=ax,
                xticklabels=['Honest', 'Malicious'],
                cbar_kws={'label': 'Number of Votes'})
    
    ax.set_xlabel('Vote Type')
    ax.set_ylabel('Blob ID')
    ax.set_title(f'Voting Pattern Heatmap (First {num_blobs} Blobs)')
    save_plot(fig, os.path.join(output_dir, 'voting_pattern_heatmap.png'))

def print_statistics(df):
    blob_stats = df.groupby('blob_id').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum',
        'total_votes': 'sum'
    }).reset_index()
    
    block_stats = df.groupby('block_number').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum',
        'total_votes': 'sum'
    }).reset_index()
    
    vote_columns = [col for col in df.columns if col.startswith('vote_')]
    vote_corr = df[vote_columns].corr()
    
    print_stats_summary(blob_stats, block_stats, df, vote_columns, vote_corr)

def save_plot(fig, filepath):
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)

def print_stats_summary(blob_stats, block_stats, df, vote_columns, vote_corr):
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
    print(f"Total voters per block: {len(vote_columns)}")
    print(f"Total votes recorded: {df['total_votes'].sum()}")

    print("\nVote Correlation Summary:")
    print(f"Average Correlation between Voters: {vote_corr.mean().mean():.3f}")

def main():
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    
    df = read_and_parse_data('simulation_results.txt')
    df['total_votes'] = df['honest_votes'] + df['malicious_votes']
    
    # Generate all plots
    plot_honest_vs_malicious(df, output_dir)
    plot_yes_no_votes(df, output_dir)
    plot_vote_distribution(df, output_dir)
    plot_proposer_distribution(df, output_dir)
    plot_voting_pattern_heatmap(df, output_dir)
    
    print_statistics(df)

if __name__ == "__main__":
    main()
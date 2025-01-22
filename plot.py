import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

THRESHOLD = 3000
WINDOW = 50

def read_and_parse_data(file_path):
    print("Reading file:", file_path)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    rows = []
    for line in lines:
        # Skip header/separator lines
        if '├' in line or '┌' in line or '┐' in line or '└' in line or '┘' in line:
            continue
            
        # Clean up the line by removing table formatting
        parts = line.strip().split('│')[1:-1]
        if not parts or len(parts) < 6:
            continue
            
        try:
            block = int(parts[0].strip())
            proposer = parts[1].strip()
            blob_id = int(parts[2].strip())
            
            # Get the actual honest and malicious vote counts from the table
            honest_votes = int(parts[4].strip())
            malicious_votes = int(parts[5].strip())
            
            row = {
                'block_number': block,
                'proposer': proposer,
                'blob_id': blob_id,
                'honest_votes': honest_votes,
                'malicious_votes': malicious_votes,
                'total_votes': honest_votes + malicious_votes
            }
            rows.append(row)
            
        except Exception as e:
            print(f"Error processing line: {line}")
            print(f"Error: {e}")
            continue
    
    result_df = pd.DataFrame(rows)
    print("Processed DataFrame:", result_df.head())
    return result_df

def plot_honest_vs_malicious_per_block(df, output_dir):
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
    save_plot(fig, os.path.join(output_dir, 'honest_malicious_votes_per_block.png'))

def plot_yes_no_votes_per_block(df, output_dir):
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
    save_plot(fig, os.path.join(output_dir, 'yes_no_votes_per_block.png'))

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
    
    # Extract proposer IDs from strings like "8271(malicious)"
    proposer_ids = [int(p.split('(')[0]) for p in block_proposers['proposer']]
    proposer_type = ['Honest' if p < honest_threshold else 'Malicious' 
                     for p in proposer_ids]
    
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

def plot_honest_vs_malicious_per_blob(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    blob_votes = df.groupby('blob_id').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).reset_index()
    
    blob_votes['total_votes'] = blob_votes['honest_votes'] + blob_votes['malicious_votes']
    
    for col, color in [('honest_votes', 'green'), ('malicious_votes', 'red'), ('total_votes', 'blue')]:
        ax.plot(blob_votes['blob_id'], blob_votes[col], 
                label=col.replace('_', ' ').title(), color=color, marker='o')
    
    ax.axhline(y=THRESHOLD, color='black', linestyle='--', label=f'Threshold ({THRESHOLD:.2f})')
    
    ax.set_xlabel('Blob ID')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Total Votes per Blob')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'honest_malicious_votes_per_blob.png'))

def plot_yes_no_votes_per_blob(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    vote_columns = [col for col in df.columns if col.startswith('vote_')]
    
    df['yes_votes'] = df[vote_columns].apply(lambda x: (x == 1).sum(), axis=1)
    df['no_votes'] = df[vote_columns].apply(lambda x: (x == 0).sum(), axis=1)
    
    yes_no_votes = df.groupby('blob_id').agg({
        'yes_votes': 'sum',
        'no_votes': 'sum'
    }).reset_index()
    
    yes_no_votes['total_votes'] = yes_no_votes['yes_votes'] + yes_no_votes['no_votes']
    
    for col, color in [('yes_votes', 'green'), ('no_votes', 'red'), ('total_votes', 'blue')]:
        ax.plot(yes_no_votes['blob_id'], yes_no_votes[col], 
                label=col.replace('_', ' ').title(), color=color, marker='o')
    
    ax.set_xlabel('Blob ID')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Yes/No Votes per Blob')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'yes_no_votes_per_blob.png'))

def print_statistics(df):
    # Group by blob_id to get per-blob statistics
    blob_stats = df.groupby('blob_id').agg({
        'honest_votes': ['mean', 'median', 'std', 'min', 'max'],
        'malicious_votes': ['mean', 'median', 'std', 'min', 'max'],
        'total_votes': ['mean', 'median', 'std', 'min', 'max']
    })

    # Group by block_number to get per-block statistics
    block_stats = df.groupby('block_number').agg({
        'honest_votes': 'mean',
        'malicious_votes': 'mean',
        'total_votes': 'mean'
    })

    print("\nDetailed Statistics:")

    print("\nPer Blob Total Votes:")
    print(f"Mean: {blob_stats['total_votes']['mean']:.2f}")
    print(f"Median: {blob_stats['total_votes']['median']:.2f}")
    print(f"Std Dev: {blob_stats['total_votes']['std']:.2f}")
    print(f"Min: {blob_stats['total_votes']['min']}")
    print(f"Max: {blob_stats['total_votes']['max']}")

    print("\nPer Blob Honest Votes:")
    print(f"Mean: {blob_stats['honest_votes']['mean']:.2f}")
    print(f"Median: {blob_stats['honest_votes']['median']:.2f}")
    print(f"Std Dev: {blob_stats['honest_votes']['std']:.2f}")
    print(f"Min: {blob_stats['honest_votes']['min']}")
    print(f"Max: {blob_stats['honest_votes']['max']}")

    print("\nPer Blob Malicious Votes:")
    print(f"Mean: {blob_stats['malicious_votes']['mean']:.2f}")
    print(f"Median: {blob_stats['malicious_votes']['median']:.2f}")
    print(f"Std Dev: {blob_stats['malicious_votes']['std']:.2f}")
    print(f"Min: {blob_stats['malicious_votes']['min']}")
    print(f"Max: {blob_stats['malicious_votes']['max']}")

    print("\nPer Block Statistics:")
    print(f"Mean honest votes: {block_stats['honest_votes'].mean():.2f}")
    print(f"Mean malicious votes: {block_stats['malicious_votes'].mean():.2f}")
    print(f"Mean total votes: {block_stats['total_votes'].mean():.2f}")

    print(f"\nTotal blobs: {df['blob_id'].nunique()}")
    print(f"Total blocks: {df['block_number'].nunique()}")
    print(f"Average blobs per block: {df['blob_id'].nunique() / df['block_number'].nunique():.2f}")

    print("\nVoting Summary:")
    print(f"Total honest votes: {df['honest_votes'].sum()}")
    print(f"Total malicious votes: {df['malicious_votes'].sum()}")
    print(f"Total votes: {df['total_votes'].sum()}")

def save_plot(fig, filepath):
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_honest_vs_malicious_per_block_avg(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    block_votes = df.groupby('block_number').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).reset_index()
    
    block_votes['total_votes'] = block_votes['honest_votes'] + block_votes['malicious_votes']
        
    # Calculate rolling averages
    for col, color in [('honest_votes', 'green'), ('malicious_votes', 'red'), ('total_votes', 'blue')]:
        # Plot scattered points with low alpha
        ax.scatter(block_votes['block_number'], block_votes[col], 
                  color=color, alpha=0.2, s=20)
        # Plot rolling average line
        rolling_avg = block_votes[col].rolling(window=WINDOW, center=True).mean()
        ax.plot(block_votes['block_number'], rolling_avg,
                label=col.replace('_', ' ').title(), color=color, linewidth=2)
    
    ax.set_xlabel('Block Number')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Total Votes per Block (Rolling Average)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'honest_malicious_votes_per_block_avg.png'))

def plot_yes_no_votes_per_block_avg(df, output_dir):
    fig, ax = plt.subplots(figsize=(15, 8))
    vote_columns = [col for col in df.columns if col.startswith('vote_')]
    
    df['yes_votes'] = df[vote_columns].apply(lambda x: (x == 1).sum(), axis=1)
    df['no_votes'] = df[vote_columns].apply(lambda x: (x == 0).sum(), axis=1)
    
    yes_no_votes = df.groupby('block_number').agg({
        'yes_votes': 'sum',
        'no_votes': 'sum'
    }).reset_index()
    
    yes_no_votes['total_votes'] = yes_no_votes['yes_votes'] + yes_no_votes['no_votes']
    
    # Calculate rolling averages
    for col, color in [('yes_votes', 'green'), ('no_votes', 'red'), ('total_votes', 'blue')]:
        # Plot scattered points with low alpha
        ax.scatter(yes_no_votes['block_number'], yes_no_votes[col],
                  color=color, alpha=0.2, s=20)
        # Plot rolling average line
        rolling_avg = yes_no_votes[col].rolling(window=WINDOW, center=True).mean()
        ax.plot(yes_no_votes['block_number'], rolling_avg,
                label=col.replace('_', ' ').title(), color=color, linewidth=2)
    
    ax.set_xlabel('Block Number')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Yes/No Votes per Block (Rolling Average)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    save_plot(fig, os.path.join(output_dir, 'yes_no_votes_per_block_avg.png'))

def main():
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    
    df = read_and_parse_data('simulation_results.txt')
    
    # Calculate total honest and malicious votes from individual vote columns
    vote_columns = [col for col in df.columns if col.startswith('vote_')]
    df['honest_votes'] = df[vote_columns].sum(axis=1)  # Sum of 1s (honest votes)
    df['malicious_votes'] = df[vote_columns].count() - df['honest_votes']  # Count of 0s
    df['total_votes'] = df[vote_columns].count()  # Total number of votes
    
    # Create plots directory
    plots_dir = os.path.join(output_dir)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Generate all plots
    plot_honest_vs_malicious_per_block(df, plots_dir)
    plot_yes_no_votes_per_block(df, plots_dir)
    plot_vote_distribution(df, plots_dir)
    plot_proposer_distribution(df, plots_dir)
    plot_voting_pattern_heatmap(df, plots_dir)
    plot_honest_vs_malicious_per_blob(df, plots_dir)
    plot_yes_no_votes_per_blob(df, plots_dir)
    plot_honest_vs_malicious_per_block_avg(df, plots_dir)
    plot_yes_no_votes_per_block_avg(df, plots_dir)
    
    # Print statistics
    print_statistics(df)

if __name__ == "__main__":
    main()
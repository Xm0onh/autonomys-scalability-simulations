import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

WINDOW = 50  # For rolling averages

def read_detailed_data(file_path='simulation_results_vc.csv'):
    """Read the detailed per-block, per-blob voting data"""
    df = pd.read_csv(file_path)
    
    # Extract proposer info from the combined column
    df['proposer_id'] = df['Proposer(Status)'].str.extract(r'(\d+)').astype(int)
    df['proposer_type'] = df['Proposer(Status)'].str.extract(r'\((.*?)\)')[0]
    
    # Rename columns to match existing code
    df = df.rename(columns={
        'Block': 'block_number',
        'Blob ID': 'blob_id',
        'Honest Votes': 'honest_votes',
        'Malicious Votes': 'malicious_votes'
    })
    
    return df

def plot_votes_per_block(df, output_dir):
    """Plot honest vs malicious votes per block with rolling average"""
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Group by block number
    block_votes = df.groupby('block_number').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).reset_index()
    
    block_votes['total_votes'] = block_votes['honest_votes'] + block_votes['malicious_votes']
    
    # Plot both raw data (scattered) and rolling averages
    for col, color, label in [
        ('honest_votes', 'green', 'Honest Votes'),
        ('malicious_votes', 'red', 'Malicious Votes'),
        ('total_votes', 'blue', 'Total Votes')
    ]:
        # Scatter plot for raw data
        ax.scatter(block_votes['block_number'], block_votes[col], 
                  color=color, alpha=0.2, s=20)
        
        # Rolling average line
        rolling_avg = block_votes[col].rolling(window=WINDOW, center=True).mean()
        ax.plot(block_votes['block_number'], rolling_avg,
                label=label, color=color, linewidth=2)
    
    ax.set_xlabel('Block Number')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Votes per Block (with Rolling Average)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'votes_per_block.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_votes_per_blob(df, output_dir):
    """Plot honest vs malicious votes per blob"""
    fig, ax = plt.subplots(figsize=(15, 8))
    
    blob_votes = df.groupby('blob_id').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).reset_index()
    
    blob_votes['total_votes'] = blob_votes['honest_votes'] + blob_votes['malicious_votes']
    
    for col, color, label in [
        ('honest_votes', 'green', 'Honest Votes'),
        ('malicious_votes', 'red', 'Malicious Votes'),
        ('total_votes', 'blue', 'Total Votes')
    ]:
        ax.plot(blob_votes['blob_id'], blob_votes[col],
                label=label, color=color, marker='o', markersize=4)
    
    ax.set_xlabel('Blob ID')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Votes per Blob')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'votes_per_blob.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_proposer_distribution(df, output_dir):
    """Plot distribution of honest vs malicious proposers"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get unique proposers per block and count their types
    proposer_counts = df.groupby('block_number')['proposer_type'].first().value_counts().reset_index()
    proposer_counts.columns = ['proposer_type', 'count']
    
    # Create the bar plot
    sns.barplot(data=proposer_counts, 
                x='proposer_type', 
                y='count',
                palette={'honest': 'green', 'malicious': 'red'},
                ax=ax)
    
    ax.set_xlabel('Proposer Type')
    ax.set_ylabel('Number of Blocks Proposed')
    ax.set_title('Distribution of Block Proposers')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'proposer_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_vote_patterns(df, output_dir):
    """Create a heatmap of voting patterns"""
    # Group by blob_id and create vote matrix
    vote_matrix = df.groupby('blob_id').agg({
        'honest_votes': 'sum',
        'malicious_votes': 'sum'
    }).values
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(vote_matrix, 
                cmap='YlOrRd',
                xticklabels=['Honest', 'Malicious'],
                ax=ax,
                cbar_kws={'label': 'Number of Votes'})
    
    ax.set_ylabel('Blob ID')
    ax.set_title('Voting Pattern Heatmap')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vote_patterns_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()

def print_statistics(df):
    """Print comprehensive statistics about the simulation"""
    print("\n=== Simulation Statistics ===\n")
    
    # Block statistics
    print("Block Statistics:")
    print(f"Total blocks: {df['block_number'].nunique()}")
    print(f"Honest proposers: {df.groupby('block_number')['proposer_type'].first().value_counts().get('honest', 0)}")
    print(f"Malicious proposers: {df.groupby('block_number')['proposer_type'].first().value_counts().get('malicious', 0)}")
    
    # Blob statistics
    print("\nBlob Statistics:")
    print(f"Total blobs: {df['blob_id'].nunique()}")
    print(f"Average blobs per block: {df['blob_id'].nunique() / df['block_number'].nunique():.2f}")
    
    # Vote statistics
    print("\nVote Statistics:")
    total_honest = df['honest_votes'].sum()
    total_malicious = df['malicious_votes'].sum()
    print(f"Total honest votes: {total_honest}")
    print(f"Total malicious votes: {total_malicious}")
    print(f"Total votes: {total_honest + total_malicious}")
    print(f"Honest vote percentage: {(total_honest / (total_honest + total_malicious) * 100):.2f}%")
    
    # Per-blob vote statistics
    blob_stats = df.groupby('blob_id').agg({
        'honest_votes': ['mean', 'median', 'std', 'min', 'max'],
        'malicious_votes': ['mean', 'median', 'std', 'min', 'max']
    })
    
    print("\nPer-blob Vote Statistics:")
    print("\nHonest Votes:")
    print(f"Mean: {blob_stats['honest_votes']['mean'].mean():.2f}")
    print(f"Median: {blob_stats['honest_votes']['median'].mean():.2f}")
    print(f"Std Dev: {blob_stats['honest_votes']['std'].mean():.2f}")
    print(f"Min: {blob_stats['honest_votes']['min'].min()}")
    print(f"Max: {blob_stats['honest_votes']['max'].max()}")
    
    print("\nMalicious Votes:")
    print(f"Mean: {blob_stats['malicious_votes']['mean'].mean():.2f}")
    print(f"Median: {blob_stats['malicious_votes']['median'].mean():.2f}")
    print(f"Std Dev: {blob_stats['malicious_votes']['std'].mean():.2f}")
    print(f"Min: {blob_stats['malicious_votes']['min'].min()}")
    print(f"Max: {blob_stats['malicious_votes']['max'].max()}")

def main():
    # Create output directory
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Read data
    df = read_detailed_data('simulation_results_vc.csv')
    
    # Generate plots
    plot_votes_per_block(df, output_dir)
    plot_votes_per_blob(df, output_dir)
    plot_proposer_distribution(df, output_dir)
    plot_vote_patterns(df, output_dir)
    
    # Print statistics
    print_statistics(df)

if __name__ == "__main__":
    main()
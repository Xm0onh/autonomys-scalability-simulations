use crate::models::{Blob, Block};
use prettytable::{format, Cell, Row, Table};
use std::collections::{HashMap, HashSet};
use std::io::{BufWriter, Write};

pub mod csv_writer;

// General table for different scenarios
pub fn create_results_table(blocks: &[Block], honest_nodes: &HashSet<usize>) -> Table {
    let mut table = Table::new();
    table.set_format(*format::consts::FORMAT_BOX_CHARS);

    table.add_row(Row::new(vec![
        Cell::new("Block"),
        Cell::new("Proposer(Status)"),
        Cell::new("Blob ID"),
        Cell::new("Votes(Status)"),
        Cell::new("Honest Votes"),
        Cell::new("Malicious Votes"),
    ]));

    for block in blocks {
        let proposer_status = if honest_nodes.contains(&block.proposer) {
            "honest"
        } else {
            "malicious"
        };
        let proposer_str = format!("{}({})", block.proposer, proposer_status);

        for (blob_id, blob_votes) in &block.votes {
            let mut honest_count = 0;
            let mut malicious_count = 0;

            let votes: Vec<String> = block
                .selected_nodes
                .iter()
                .enumerate()
                .map(|(i, &node)| {
                    let is_honest = honest_nodes.contains(&node);
                    let vote = blob_votes[i];

                    if is_honest {
                        if vote.is_some() {
                            honest_count += 1;
                        }
                    } else {
                        if vote.is_some() {
                            malicious_count += 1;
                        }
                    }

                    format!(
                        "{}({})",
                        if vote.is_some() { "1" } else { "0" },
                        if is_honest { "honest" } else { "malicious" }
                    )
                })
                .collect();

            table.add_row(Row::new(vec![
                Cell::new(&block.number.to_string()),
                Cell::new(&proposer_str),
                Cell::new(&blob_id.to_string()),
                Cell::new(
                    &votes
                        .iter()
                        .filter(|v| !v.starts_with("0"))
                        .map(|s| s.as_str())
                        .collect::<Vec<_>>()
                        .join(", "),
                ),
                Cell::new(&honest_count.to_string()),
                Cell::new(&malicious_count.to_string()),
            ]));
        }
    }

    table
}

// Works for vote censorship NOT basic
pub fn create_voting_summary_per_block(blocks: &[Block], honest_nodes: &HashSet<usize>) -> Table {
    let mut table = Table::new();
    table.set_format(*format::consts::FORMAT_BOX_CHARS);

    // Add headers
    table.add_row(Row::new(vec![
        Cell::new("Blob"),
        Cell::new("Block Proposer Status"),
        Cell::new("Total Votes"),
        Cell::new("Honest Votes"),
        Cell::new("Malicious Votes"),
    ]));

    // Process each block
    for block in blocks {
        let proposer_status = if honest_nodes.contains(&block.proposer) {
            "Honest"
        } else {
            "Malicious"
        };

        // Calculate total votes across all blobs in this block
        let mut block_total_votes = 0;
        let mut block_honest_votes = 0;
        let mut block_malicious_votes = 0;

        // Process votes for each blob
        for (_blob_id, blob_votes) in &block.votes {
            block_total_votes += blob_votes.iter().filter(|vote| vote.is_some()).count();

            // Count honest and malicious votes
            for (i, _) in blob_votes.iter().enumerate() {
                let voter = block.selected_nodes[i];
                if honest_nodes.contains(&voter) && blob_votes[i].is_some() {
                    block_honest_votes += 1;
                } else if !honest_nodes.contains(&voter) && blob_votes[i].is_some() {
                    block_malicious_votes += 1;
                }
            }
        }

        // Add block summary row
        table.add_row(Row::new(vec![
            Cell::new(&block.number.to_string()),
            Cell::new(proposer_status),
            Cell::new(&block_total_votes.to_string()),
            Cell::new(&block_honest_votes.to_string()),
            Cell::new(&block_malicious_votes.to_string()),
        ]));
    }

    table
}

pub fn create_voting_summary_per_blob(blobs: &HashMap<usize, Blob>) -> Table {
    // first sort blobs by their id
    let mut blobs: Vec<Blob> = blobs.values().cloned().collect();
    blobs.sort_by_key(|blob| blob.id);

    let mut table = Table::new();
    table.set_format(*format::consts::FORMAT_BOX_CHARS);

    // Add headers
    table.add_row(Row::new(vec![
        Cell::new("Blob"),
        Cell::new("Blob Proposer Status"),
        Cell::new("Total Votes"),
        Cell::new("Honest Votes"),
        Cell::new("Malicious Votes"),
    ]));

    // Process each block
    for blob in blobs {
        // Add block summary row
        table.add_row(Row::new(vec![
            Cell::new(&blob.id.to_string()),
            Cell::new(&blob.proposer_status.to_string()),
            Cell::new(&(blob.votes_honest + blob.votes_malicious).to_string()),
            Cell::new(&blob.votes_honest.to_string()),
            Cell::new(&blob.votes_malicious.to_string()),
        ]));
    }

    table
}

pub fn write_table_buffered<W: Write>(
    table: &Table,
    writer: &mut BufWriter<W>,
) -> std::io::Result<()> {
    write!(writer, "{}", table.to_string())?;
    writer.flush()?;
    Ok(())
}

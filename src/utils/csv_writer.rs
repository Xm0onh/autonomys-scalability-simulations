use crate::models::Block;
use std::collections::HashSet;
use std::io::{BufWriter, Write};

pub fn create_results_csv<W: Write>(
    blocks: &[Block],
    honest_nodes: &HashSet<usize>,
    writer: &mut BufWriter<W>,
) -> std::io::Result<()> {
    // Write header
    writeln!(
        writer,
        "Block,Proposer(Status),Blob ID,Votes(Status),Honest Votes,Malicious Votes"
    )?;

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

            let votes_str = votes
                .iter()
                .filter(|v| !v.starts_with("0"))
                .cloned()
                .collect::<Vec<String>>()
                .join(";");

            writeln!(
                writer,
                "{},{},{},\"{}\",{},{}",
                block.number, proposer_str, blob_id, votes_str, honest_count, malicious_count
            )?;
        }
    }
    writer.flush()?;
    Ok(())
}

use prettytable::{Table, Row, Cell, format};
use std::collections::HashSet;
use crate::models::Block;

pub fn create_results_table(blocks: &[Block], honest_nodes: &HashSet<usize>) -> Table {
    let mut table = Table::new();
    table.set_format(*format::consts::FORMAT_BOX_CHARS);
    
    table.add_row(Row::new(vec![
        Cell::new("Block"),
        Cell::new("Proposer(Status)"),
        Cell::new("Blob ID"),
        Cell::new("Votes(Status)"),
        Cell::new("Honest Votes"),
        Cell::new("Malicious Votes")
    ]));
    
    for block in blocks {
        let proposer_status = if honest_nodes.contains(&block.proposer) { "honest" } else { "malicious" };
        let proposer_str = format!("{}({})", block.proposer, proposer_status);
        
        for (blob_id, blob_votes) in &block.votes {
            let mut honest_count = 0;
            let mut malicious_count = 0;
            
            let votes: Vec<String> = block.selected_nodes.iter()
                .enumerate()
                .map(|(i, &node)| {
                    let is_honest = honest_nodes.contains(&node);
                    let vote = blob_votes[i];
                    
                    if is_honest {
                        if vote { honest_count += 1; }
                    } else {
                        malicious_count += 1; 
                    }
                    
                    format!("{}({})", 
                        if vote { "1" } else { "0" }, 
                        if is_honest { "honest" } else { "malicious" }
                    )
                })
                .collect();
            
            table.add_row(Row::new(vec![
                Cell::new(&block.number.to_string()),
                Cell::new(&proposer_str),
                Cell::new(&blob_id.to_string()),
                Cell::new(&votes.join(", ")),
                Cell::new(&honest_count.to_string()),
                Cell::new(&malicious_count.to_string())
            ]));
        }
    }
    
    table
} 
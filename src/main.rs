use rand::seq::SliceRandom;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::Write;
use serde::Deserialize;
use prettytable::{Table, Row, Cell, format};

#[derive(Debug, Deserialize)]
struct Settings {
    total_nodes: usize,
    malicious_nodes: usize,
    nodes_per_block: usize,
    confirmation_depth: usize,
    malicious_power_block: usize,
    total_blocks: usize,
    reliable_nodes: usize,
}

fn load_config() -> Settings {
    config::Config::builder()
        .add_source(config::File::with_name("config"))
        .build()
        .unwrap()
        .try_deserialize()
        .unwrap()
}

#[derive(Debug, Clone)]
struct Blob {
    id: usize,
    votes_honest: usize,
    votes_malicious: usize,
    is_confirmed: bool,
    proposer_status: String 
}

fn reliable_nodes(all_nodes: &HashSet<usize>, num_nodes: usize) -> HashSet<usize> {
    let mut rng = rand::thread_rng();
    all_nodes
        .iter()
        .cloned()
        .collect::<Vec<_>>()
        .choose_multiple(&mut rng, num_nodes)
        .cloned()
        .collect()
}

#[derive(Debug, Clone)]
struct Block {
    number: usize,
    proposer: usize,
    selected_nodes: Vec<usize>,
    votes: HashMap<usize, Vec<bool>>, // blob_id -> vector of votes from selected nodes
}

fn create_results_table(blocks: &[Block], honest_nodes: &HashSet<usize>) -> Table {
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

#[allow(unused_variables)]
fn main() {
    let config = load_config();
    let mut rng = rand::thread_rng();

    let honest_nodes: HashSet<usize> = (0..(config.total_nodes - config.malicious_nodes)).collect();
    let malicious_nodes: HashSet<usize> = ((config.total_nodes - config.malicious_nodes)..config.total_nodes).collect();
    let all_nodes: HashSet<usize> = (0..config.total_nodes).collect();

    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;

    let mut blocks: Vec<Block> = Vec::new();

    for block in 1..=config.total_blocks {
        let block_proposer = *all_nodes.iter().collect::<Vec<_>>().choose(&mut rng).unwrap();
        
        // Create new blob for this block
        let new_blob = Blob {
            id: next_blob_id,
            votes_honest: 0,
            votes_malicious: 0,
            is_confirmed: false,
            proposer_status: "honest".to_string(),
        };
        blobs.insert(next_blob_id, new_blob);
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        // Select nodes for this block
        let selected_nodes: Vec<usize> = all_nodes
            .iter()
            .cloned()
            .collect::<Vec<_>>()
            .choose_multiple(&mut rng, config.nodes_per_block)
            .cloned()
            .collect();

        // Create votes for each unconfirmed blob
        let mut block_votes: HashMap<usize, Vec<bool>> = HashMap::new();
        
        for &blob_id in &unconfirmed_blobs {
            let mut votes = Vec::with_capacity(selected_nodes.len());
            
            for &node in &selected_nodes {
                let vote = if honest_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                    true
                } else if malicious_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                    false // Assuming malicious nodes vote false for now!!!
                } else {
                    false
                };
                votes.push(vote);
            }
            
            block_votes.insert(blob_id, votes);
        }

        let block = Block {
            number: block,
            proposer: *block_proposer,
            selected_nodes,
            votes: block_votes,
        };

        // Handle confirmation logic
        if block.number >= config.confirmation_depth {
            let confirmed_blob_id = block.number - config.confirmation_depth;
            if let Some(blob) = blobs.get_mut(&confirmed_blob_id) {
                blob.is_confirmed = true;
                unconfirmed_blobs.remove(&confirmed_blob_id);
            }
        }
        println!("Block Number: {}", block.number);
        blocks.push(block);
    }

    let table = create_results_table(&blocks, &honest_nodes);
    
    let mut file = File::create("simulation_results.txt").expect("Unable to create file");
    write!(file, "{}", table.to_string()).expect("Unable to write table");

    println!("Simulation complete. Results written to 'simulation_results.txt'.");
}

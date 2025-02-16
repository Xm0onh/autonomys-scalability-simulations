use rand::seq::SliceRandom;
use sim::{
    models::{Blob, Block, Settings},
    utils::csv_writer::create_results_csv,
};
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::BufWriter;

pub fn run() {
    let config = Settings::load("config");
    let mut rng = rand::thread_rng();

    // Divide nodes into honest and malicious groups
    let honest_nodes: HashSet<usize> = (0..(config.total_nodes - config.malicious_nodes)).collect();
    let _malicious_nodes: HashSet<usize> = ((config.total_nodes - config.malicious_nodes)..config.total_nodes).collect();
    let all_nodes: HashSet<usize> = (0..config.total_nodes).collect();

    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;
    let mut blocks: Vec<Block> = Vec::new();

    // Define a threshold for triggering the withholding attack. 
    // This threshold represents the number of honest votes a blob must have to trigger malicious withholding.
    let smart_threshold = 2; // You may also load this from config if desired

    for block_number in 1..=config.total_blocks {
        // Randomly select a block proposer
        let block_proposer = *all_nodes.iter().collect::<Vec<_>>().choose(&mut rng).unwrap();

        // Create a new blob for this block
        let new_blob = Blob::new(next_blob_id);
        blobs.insert(next_blob_id, new_blob);
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        // Randomly select the nodes that will vote in this block
        let selected_nodes: Vec<usize> = all_nodes
            .iter()
            .cloned()
            .collect::<Vec<_>>()
            .choose_multiple(&mut rng, config.nodes_per_block)
            .cloned()
            .collect();

        // Simulate votes for each unconfirmed blob
        let mut block_votes: HashMap<usize, Vec<Option<bool>>> = HashMap::new();

        for &blob_id in &unconfirmed_blobs {
            let mut votes = Vec::new();
            for &node in &selected_nodes {
                if honest_nodes.contains(&node) {
                    // Honest nodes always vote yes, because they successfully download and verify the blob sample
                    votes.push(Some(true));
                    if let Some(blob) = blobs.get_mut(&blob_id) {
                        blob.votes_honest += 1;
                    }
                } else {
                    // Malicious nodes use a smart strategy: if the blob has already accumulated enough honest votes, they withhold (vote no);
                    // otherwise, they vote yes to support their own chain.
                    let current_honest_votes = blobs.get(&blob_id).map(|blob| blob.votes_honest).unwrap_or(0);
                    if current_honest_votes >= smart_threshold {
                        votes.push(Some(false));
                        if let Some(blob) = blobs.get_mut(&blob_id) {
                            blob.votes_malicious += 1;
                        }
                    } else {
                        votes.push(Some(true));
                    }
                }
            }
            block_votes.insert(blob_id, votes);
        }

        // Create the block with the votes cast
        let block = Block {
            number: block_number,
            proposer: *block_proposer,
            selected_nodes: selected_nodes.clone(),
            votes: block_votes,
            buffered_votes: HashMap::new(),
        };

        // Confirm blobs when they are k blocks deep
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

    // Write out the simulation results to a new CSV file for the smart data withholding scenario
    let file = File::create("simulation_results_smart_data_withholding.csv")
        .expect("Unable to create file");
    let mut writer = BufWriter::new(file);
    create_results_csv(&blocks, &honest_nodes, &mut writer)
        .expect("Unable to write CSV");

    println!("Smart data withholding simulation complete. Results written to 'simulation_results_smart_data_withholding.csv'.");
} 
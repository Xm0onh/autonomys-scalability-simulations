use rand::seq::SliceRandom;
use sim::{
    models::{Blob, Block, Settings},
    utils::csv_writer::create_results_csv,
};
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::BufWriter;

#[allow(dead_code)]
pub fn run() {
    let config = Settings::load("config");
    let mut rng = rand::thread_rng();

    let honest_nodes: HashSet<usize> = (0..(config.total_nodes - config.malicious_nodes)).collect();
    let _malicious_nodes: HashSet<usize> =
        ((config.total_nodes - config.malicious_nodes)..config.total_nodes).collect();
    let all_nodes: HashSet<usize> = (0..config.total_nodes).collect();

    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;

    let mut blocks: Vec<Block> = Vec::new();

    for block in 1..=config.total_blocks {
        let block_proposer = *all_nodes
            .iter()
            .collect::<Vec<_>>()
            .choose(&mut rng)
            .unwrap();

        // Create new blob for this block
        let new_blob = sim::models::Blob::new(next_blob_id);
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
        let mut block_votes: HashMap<usize, Vec<Option<bool>>> = HashMap::new();

        for &blob_id in &unconfirmed_blobs {
            let mut votes = Vec::with_capacity(selected_nodes.len());

            for &node in &selected_nodes {
                let vote = if honest_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                    Some(true)
                } else {
                    blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                    Some(false)
                };
                votes.push(vote);
            }

            block_votes.insert(blob_id, votes);
        }

        let block = sim::models::Block {
            number: block,
            proposer: *block_proposer,
            selected_nodes,
            votes: block_votes,
            buffered_votes: HashMap::new(),
        };

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

    let file = File::create("simulation_results.csv").expect("Unable to create file");
    let mut writer = BufWriter::new(file);
    create_results_csv(&blocks, &honest_nodes, &mut writer).expect("Unable to write CSV");

    println!("Simulation complete. Results written to 'simulation_results_basic.txt'.");
}

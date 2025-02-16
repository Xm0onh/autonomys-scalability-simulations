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

    // Define our node groups
    let honest_nodes: HashSet<usize> = (0..(config.total_nodes - config.malicious_nodes)).collect();
    let _malicious_nodes: HashSet<usize> =
        ((config.total_nodes - config.malicious_nodes)..config.total_nodes).collect();
    let all_nodes: HashSet<usize> = (0..config.total_nodes).collect();

    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;
    let mut blocks: Vec<Block> = Vec::new();

    // Parameters for data withholding
    // E.g., last K_f blocks will be attack blocks (data withholding active)
    let attack_start_block = config.total_blocks.saturating_sub(config.k_f);

    for block_number in 1..=config.total_blocks {
        let block_proposer = *all_nodes.iter().collect::<Vec<_>>().choose(&mut rng).unwrap();

        // Create a blob for the new block and keep track of unconfirmed blobs
        let new_blob = Blob::new(next_blob_id);
        blobs.insert(next_blob_id, new_blob);
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        // Select the voter nodes to participate in this block
        let selected_nodes: Vec<usize> = all_nodes.iter().cloned().collect::<Vec<_>>()
            .choose_multiple(&mut rng, config.nodes_per_block)
            .cloned()
            .collect();

        // For each unconfirmed blob, simulate the vote
        let mut block_votes: HashMap<usize, Vec<Option<bool>>> = HashMap::new();

        for &blob_id in &unconfirmed_blobs {
            let mut votes = Vec::new();

            // Check if this block falls into the data withholding phase
            let data_withholding_active = block_number >= attack_start_block;
            
            for &node in &selected_nodes {
                // For honest nodes:
                if honest_nodes.contains(&node) {
                    if data_withholding_active {
                        // Data is withheld, so honest nodes cannot verify the blob sample.
                        // They vote "No" (or you could decide None to simulate an abstention).
                        votes.push(Some(false));
                        // Optionally update the blob counters if you track failure votes
                        blobs.get_mut(&blob_id).unwrap().votes_honest += 0;
                    } else {
                        // Normal behavior: download sample and verify, then vote Yes
                        votes.push(Some(true));
                        blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                    }
                } else {
                    // For malicious nodes, choose their behavior arbitrarily.
                    // They might vote "Yes" in attack blocks to artificially help their chain.
                    let vote = if data_withholding_active {
                        // Attack behavior: may vote Yes even if withholding data
                        Some(true)
                    } else {
                        // Normal malicious strategy; in a real simulation, the choice could be random.
                        Some(false)
                    };
                    votes.push(vote);
                    if vote == Some(false) {
                        blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                    }
                }
            }
            block_votes.insert(blob_id, votes);
        }

        // Create the block; you might want to record additional info (like data_withholding flag) for analysis.
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

    // Write out the simulation results
    let file = File::create("simulation_results_data_withholding.csv").expect("Unable to create file");
    let mut writer = BufWriter::new(file);
    create_results_csv(&blocks, &honest_nodes, &mut writer).expect("Unable to write CSV");

    // Optionally, you could also write the table summaries similar to the other scenarios
    println!("Simulation complete. Results written to 'simulation_results_data_withholding.csv'.");
} 
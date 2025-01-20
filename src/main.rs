use rand::seq::SliceRandom;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::Write;
use serde::Deserialize;

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

    for block in 1..=config.total_blocks {
        let nodes_vec: Vec<_> = all_nodes.iter().cloned().collect();
        let block_proposer = nodes_vec.choose(&mut rng).unwrap();
        let new_blob: Blob;
        if malicious_nodes.contains(block_proposer) {
            new_blob = Blob {
                id: next_blob_id,
                votes_honest: 0,
                votes_malicious: 0,
                is_confirmed: false,
                proposer_status: "malicious".to_string(),
            };
        } else {
            new_blob = Blob {
                id: next_blob_id,
                votes_honest: 0,
                votes_malicious: 0,
                is_confirmed: false,
                proposer_status: "honest".to_string(),
            };
        }
        blobs.insert(next_blob_id, new_blob.clone());
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        let selected_nodes: Vec<usize> = all_nodes
            .iter()
            .cloned()
            .collect::<Vec<_>>()
            .choose_multiple(&mut rng, config.nodes_per_block)
            .cloned()
            .collect();

        let reliable_nodes = reliable_nodes(&honest_nodes, config.reliable_nodes);

        for &blob_id in &unconfirmed_blobs {
            for &node in &selected_nodes {
                if honest_nodes.contains(&node) && block < (config.confirmation_depth - config.malicious_power_block) {
                    blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                } else if malicious_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                }
            }
        }

        if block >= config.confirmation_depth {
            let confirmed_blob_id = block - config.confirmation_depth;
            if let Some(blob) = blobs.get_mut(&confirmed_blob_id) {
                blob.is_confirmed = true;
                unconfirmed_blobs.remove(&confirmed_blob_id);
            }
        }
        println!("Block Number: {}", block);
    }

    let mut file = File::create("simulation_results.csv").expect("Unable to create file");
    writeln!(
        file,
        "blob_id,total_votes,honest_votes,malicious_votes,confirmed,proposer_status"
    )
    .expect("Unable to write header");
    // size of the blobs
    println!("Size of the blobs: {}", blobs.len());
    for (_, blob) in &blobs {
        writeln!(
            file,
            "{},{},{},{},{},{}",
            blob.id,
            blob.votes_honest + blob.votes_malicious,
            blob.votes_honest,
            blob.votes_malicious,
            blob.is_confirmed,
            blob.proposer_status
        )
        .expect("Unable to write row");
    }

    println!("Simulation complete. Results written to 'simulation_results.csv'.");
}

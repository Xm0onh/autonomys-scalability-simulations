use rand::seq::SliceRandom;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::Write;

// Parameters
const N: usize = 10000; // Total nodes
const F: usize = 2000; // Malicious nodes
const M: usize = 10; // Nodes voting per block
const K: usize = 150; // Confirmation depth
const K_F: usize = 14000; // Start block number for malicious nodes to gain power
const T: usize = 15000; // Number of blocks
const EPSILON: usize = 1000; // Number of reliable nodes

#[derive(Debug, Clone)]
struct Blob {
    id: usize,
    votes_honest: usize,
    votes_malicious: usize,
    is_confirmed: bool,
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

fn main() {
    let mut rng = rand::thread_rng();

    let honest_nodes: HashSet<usize> = (0..(N - F)).collect();
    let malicious_nodes: HashSet<usize> = ((N - F)..N).collect();
    let all_nodes: HashSet<usize> = (0..N).collect();

    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;

    for block in 1..=T {
        let new_blob = Blob {
            id: next_blob_id,
            votes_honest: 0,
            votes_malicious: 0,
            is_confirmed: false,
        };
        blobs.insert(next_blob_id, new_blob.clone());
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        let selected_nodes: Vec<usize> = all_nodes
            .iter()
            .cloned()
            .collect::<Vec<_>>()
            .choose_multiple(&mut rng, M)
            .cloned()
            .collect();

        let reliable_nodes = reliable_nodes(&honest_nodes, EPSILON);

        for &blob_id in &unconfirmed_blobs {
            for &node in &selected_nodes {
                if honest_nodes.contains(&node) && reliable_nodes.contains(&node) && block < K_F {
                    blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                } else if malicious_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                }
            }
        }

        if block >= K {
            let confirmed_blob_id = block - K;
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
        "blob_id,total_votes,honest_votes,malicious_votes,confirmed"
    )
    .expect("Unable to write header");
    for (_, blob) in &blobs {
        if blob.id > blobs.len() - K {
            continue;
        }
        writeln!(
            file,
            "{},{},{},{},{}",
            blob.id,
            blob.votes_honest + blob.votes_malicious,
            blob.votes_honest,
            blob.votes_malicious,
            blob.is_confirmed
        )
        .expect("Unable to write row");
    }

    println!("Simulation complete. Results written to 'simulation_results.csv'.");
}

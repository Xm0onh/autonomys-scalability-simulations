use rand::seq::SliceRandom;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::Write;

// Parameters
const N: usize = 100; // Total nodes
const F: usize = 20;  // Malicious nodes
const M: usize = 10;  // Nodes voting per block
const K: usize = 1;   // Confirmation depth
const T: usize = 50;  // Number of blocks

#[derive(Debug, Clone)]
struct Blob {
    id: usize,
    votes_honest: usize,
    votes_malicious: usize,
    is_confirmed: bool,
}

fn main() {
    let mut rng = rand::thread_rng();

    // Nodes (honest nodes are indices 0..(N-F), malicious nodes are (N-F)..N)
    let honest_nodes: HashSet<usize> = (0..(N - F)).collect();
    let malicious_nodes: HashSet<usize> = ((N - F)..N).collect();

    // Data structures
    let mut blobs: HashMap<usize, Blob> = HashMap::new();
    let mut unconfirmed_blobs: HashSet<usize> = HashSet::new();
    let mut next_blob_id = 0;

    // Simulate blocks
    for block in 1..=T {
        // Add new blobs to unconfirmed set
        let new_blob = Blob {
            id: next_blob_id,
            votes_honest: 0,
            votes_malicious: 0,
            is_confirmed: false,
        };
        blobs.insert(next_blob_id, new_blob.clone());
        unconfirmed_blobs.insert(next_blob_id);
        next_blob_id += 1;

        // Randomly select M nodes to vote
        let all_nodes: Vec<usize> = (0..N).collect();
        let selected_nodes: Vec<usize> = all_nodes.choose_multiple(&mut rng, M).cloned().collect();

        // Vote on unconfirmed blobs
        for &blob_id in &unconfirmed_blobs {
            for &node in &selected_nodes {
                if honest_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_honest += 1;
                } else if malicious_nodes.contains(&node) {
                    blobs.get_mut(&blob_id).unwrap().votes_malicious += 1;
                }
            }
        }

        // Confirm blobs K blocks deep
        if block >= K {
            let confirmed_blob_id = block - K;
            if let Some(blob) = blobs.get_mut(&confirmed_blob_id) {
                blob.is_confirmed = true;
                unconfirmed_blobs.remove(&confirmed_blob_id);
            }
        }
    }

    // Write results to a file
    let mut file = File::create("simulation_results.csv").expect("Unable to create file");
    writeln!(file, "blob_id,total_votes,honest_votes,malicious_votes,confirmed").expect("Unable to write header");
    for (_, blob) in &blobs {
        writeln!(
            file,
            "{},{},{},{},{}",
            blob.id, blob.votes_honest + blob.votes_malicious, blob.votes_honest, blob.votes_malicious, blob.is_confirmed
        )
        .expect("Unable to write row");
    }

    println!("Simulation complete. Results written to 'simulation_results.csv'.");
}

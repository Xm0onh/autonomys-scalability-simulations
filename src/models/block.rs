use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Block {
    pub number: usize,
    pub proposer: usize,
    pub selected_nodes: Vec<usize>,
    pub votes: HashMap<usize, Vec<Option<bool>>>,
}

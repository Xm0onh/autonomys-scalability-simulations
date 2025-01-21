#[derive(Debug, Clone)]
pub struct Blob {
    pub id: usize,
    pub votes_honest: usize,
    pub votes_malicious: usize,
    pub is_confirmed: bool,
    pub proposer_status: String,
}

impl Blob {
    pub fn new(id: usize) -> Self {
        Self {
            id,
            votes_honest: 0,
            votes_malicious: 0,
            is_confirmed: false,
            proposer_status: "honest".to_string(),
        }
    }
} 
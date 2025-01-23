use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub total_nodes: usize,
    pub malicious_nodes: usize,
    pub nodes_per_block: usize,
    pub confirmation_depth: usize,
    pub malicious_power_block: usize,
    pub total_blocks: usize,
    pub reliable_nodes: usize,
    pub k_f: usize,
}

impl Settings {
    pub fn load(config_path: &str) -> Self {
        config::Config::builder()
            .add_source(config::File::with_name(config_path))
            .build()
            .unwrap()
            .try_deserialize()
            .unwrap()
    }
}

use std::env;
mod scenarios;

fn print_usage() {
    println!("Usage: cargo run <scenario>");
    println!("Available scenarios:");
    println!("  basic    - Basic simulation scenario");
    println!("  vote_censorship    - Vote censorship simulation scenario");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    match args.get(1).map(|s| s.as_str()) {
        Some("basic") => scenarios::basic::run(),
        Some("vote_censorship") => scenarios::vote_censorship::run(),
        Some("data_withholding") => scenarios::data_withholding::run(),
        Some(unknown_scenario) => {
            println!("Unknown scenario: {}", unknown_scenario);
            print_usage();
        }
        None => {
            println!("No scenario specified.");
            print_usage();
        }
    }
}

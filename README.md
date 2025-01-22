# Autonomys Scalability Design Simulation

## Configuration
Copy the `config.example.toml` file to `config.toml` and edit the file to set the parameters for the simulation.

```bash
cp config.example.toml config.toml
```

Edit the `config.toml` file to set the parameters for the simulation.

## Requirements
Create a virtual environment and install the dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Scenarios

- `basic` - Basic scenario
- `vote_censorship` - Vote censorship scenario

## Run the simulation
```
cargo run <scenario>
```

## Plot the results
```
python3 plot.py
```
Then, find the results in the `results` folder.

#### Note: the name of results file for each scenario is `simulation_results_<scenario>.csv`. Update the `plot.py` file to use the correct file name.

```python
df = read_detailed_data('simulation_results_<scenario>.csv')
```




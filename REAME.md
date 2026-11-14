# Introduction to Artificial Intelligence (503043) - Final Project

## Requirements and Installation

1. Python version: Python 3.10+
2. Install required libraries:
```bash
pip install -r requirement.txt
```
(Or `pip install -r requirements.txt`)

## Project Structure

- `task1/`: Task 1 - Local Search (Min-Conflicts) & Propositional Logic (CNF with Glucose3) for N-Queens Problem
- `task2/`: Task 2 - Adversarial Search (Minimax & Alpha-Beta Pruning) for Tank Battle Game
- `task3/`: Task 3 - Constraint Satisfaction Problems (Backtracking, MRV, LCV, AC-3) for Kakuro Puzzle

## Running Each Task

### Task 1: N-Queens Problem
```bash
cd task1
python main.py
```
Experimental notebooks:
- `task1/experiment_min_conflicts.ipynb`
- `task1/experiment_cnf.ipynb`

### Task 2: Tank Battle Game
Launch the interactive PyGame GUI:
```bash
cd task2
python main.py
```
Run the CLI benchmark comparing the 4 adversarial search configurations across depths:
```bash
cd task2
python main.py --experiment
```
Load an external agent class for Player 2:
```bash
cd task2
python main.py --ext-p2 path/to/agent_file.py --ext-class CustomAgent
```
Experimental notebook:
- `task2/experiment_tank.ipynb`

### Task 3: Kakuro Puzzle
Launch the PyGame UI (boards: `simple`, `medium`, `hard`, `expert`):
```bash
cd task3
python main.py --board simple
```
Run headless in CLI mode:
```bash
cd task3
python main.py --board simple --no-ui
```
Experimental notebook:
- `task3/experiment.ipynb`

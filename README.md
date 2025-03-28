# 🛡️ Advanced Reliability Analysis Tool

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

> **A sophisticated tool for system reliability analysis featuring advanced visualization, multiple cut set algorithms, and Monte Carlo simulation.**

## ✨ Features

- **🎭 Interactive System Builder**
  - Drag-and-drop component creation
  - Predefined system templates (series, parallel, bridge networks)
  - Real-time system visualization

- **🔍 Advanced Cut Set Analysis**
  - MOCUS algorithm implementation
  - Binary Decision Diagram (BDD) approach
  - Algorithm performance comparison
  - Visual highlighting of minimal cut sets

- **📊 Monte Carlo Simulation**
  - Comprehensive reliability prediction
  - Statistical analysis with confidence intervals
  - Interactive reliability/unreliability plots
  - Multiple failure distribution models

- **📝 Comprehensive Reporting**
  - Symbolic expression generation
  - Mean Time To Failure (MTTF) calculation
  - Time-to-reliability thresholds

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/MahmoudKebbi/System_Reliability_Analysis.git
cd System_Reliability_Analysis

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source ./venv/bin/activate

# Install dependencies
pip install -e .
```

## 🖥️ Usage

```bash
# Run the application
cd src/interface
streamlit run app.py
```

### Building a System

1. Navigate to the **System Builder** page
2. Add components with failure rates
3. Create connections between components
4. Alternatively, select a template system


### Analyzing Cut Sets

1. Navigate to the **Cut Set Analysis** page
2. Choose analysis algorithm (MOCUS, BDD, or comparison)
3. Run analysis to get minimal cut sets
4. View visual representation of cut sets


### Running Monte Carlo Simulation

1. Navigate to the **Simulation Analysis** page
2. Set simulation parameters
3. Run simulation
4. View reliability plots and statistics


## 🧪 Example Systems

The tool includes templates for common reliability configurations:

- Series systems
- Parallel systems
- Series-parallel hybrid systems
- Bridge networks

## 🛠️ Technologies

- **Core**: Python 3.9+
- **Graph Analysis**: NetworkX
- **Numerical Computing**: NumPy, SciPy
- **Symbolic Math**: SymPy
- **Visualization**: Matplotlib, Plotly
- **Interface**: Streamlit

## 📖 Theory

This tool implements several key reliability engineering concepts:

- **Minimal Cut Sets**: Sets of components that, when failed, cause system failure
- **Structure Function**: Mathematical representation of system behavior
- **Reliability Function**: Probability that system works at time t
- **Monte Carlo Method**: Statistical sampling for reliability estimation

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Dr. Raymond Ghajar at the Lebanese American University 
- NetworkX development team
- Streamlit for the interactive web framework

## Contributers

[MahmoudKebbi](https://github.com/MahmoudKebbi)

## Link To Web Application

To try out the tool please press [here](mahmoud-kebbi-system-reliability-analysis-coe553.streamlit.app)

---

<p align="center">
  Made with ❤️ for the Reliability System Evaluation Course
</p>

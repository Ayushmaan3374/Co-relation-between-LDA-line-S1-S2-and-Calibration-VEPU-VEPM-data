# Co-relation between LDA line S1, S2 and Calibration VEPU, 
# VEPM data

## 📘 Project Overview
In modern manufacturing, calibration delays are common due to weak correlations between pump output values (S1/S2) and input parameters like `VEPM_MP`, `VEPU_MP`, and `VEP_MP`. These inefficiencies demand frequent manual corrections during test bench calibration, reducing overall throughput and precision.

This project applies machine learning to automate and streamline the calibration process.

## 🎯 Objective
Develop an accurate and efficient model to:
- Predict `S1` and `S2` pump values simultaneously
- Minimize manual adjustments and correction cycles
- Improve decision-making speed on the production line

## 🧠 Approach
The solution adopts a **MultiOutput Regression** framework:
- Input features: `VEPM_MP`, `VEPU_MP`, `VEP_MP`
- Output targets: `S1`, `S2` pump values
- Model: **MultiOutput XGBoost Regressor**

This setup captures complex nonlinear relationships between input and output variables while maintaining high predictive accuracy.

## 🚀 Key Benefits
- 📉 Reduced manual correction time
- ⚙️ Enhanced calibration reliability
- ⏱ Accelerated setup and testing cycles
- 📊 Facilitated data-driven decision-making on the shop floor

## 🛠️ Tech Stack
- Python
- XGBoost
- scikit-learn
- pandas, NumPy, matplotlib

## 📁 Repository Structure

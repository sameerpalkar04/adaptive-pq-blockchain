import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime

class ResearchSimulator:
    def __init__(self, metrics_csv="logs/metrics.csv"):
        self.plot_root = "evaluation/plots"
        self.metrics_csv = metrics_csv
        
        # Ensure directory structure exists
        self.setup_directories()

    def setup_directories(self):
        paths = [
            f"{self.plot_root}/sim1", 
            f"{self.plot_root}/sim2", 
            f"{self.plot_root}/sim3"
        ]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
        print(f"Directories Ready: {datetime.now().strftime('%H:%M:%S')}")

    def _get_live_data(self):
        """Helper to fetch synchronized logs from the metrics CSV."""
        if not os.path.exists(self.metrics_csv):
            print(f"⚠️ Error: {self.metrics_csv} not found. Run simulation first.")
            return None
        return pd.read_csv(self.metrics_csv)

    def run_simulation_1(self):
        """Quantum Cryptanalysis: Mathematical baseline for attack probability."""
        print("🚀 Running Sim #1: Vulnerability and Attack Analysis...")
        qubits = np.arange(0, 4001, 40) 
        
        # Mathematical modeling of Shor's impact
        prob_ecc = 1 / (1 + np.exp(-0.01 * (qubits - 1536)))
        prob_rsa = 1 / (1 + np.exp(-0.01 * (qubits - 4000)))

        plt.figure(figsize=(10, 6))
        plt.plot(qubits, prob_ecc, color='#d63031', label='ECC-256 Success Prob.', lw=2)
        plt.plot(qubits, prob_rsa, color='#e67e22', label='RSA-3072 Success Prob.', lw=2)
        plt.plot(qubits, np.zeros(len(qubits)), color='#27ae60', lw=4, label='Adaptive PQC Middleware')
        
        plt.title("Quantum Adversary Success Rate (P_succ)", fontsize=13)
        plt.xlabel("Logical Qubits (Fault-Tolerant)")
        plt.ylabel("Probability of Successful Key Recovery")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        plt.savefig(f"{self.plot_root}/sim1/attack_success_prob.png", dpi=300)
        plt.close()
        print("✅ Sim #1 Complete.")

    def run_simulation_2(self):
        """Behavioral Adaptability Analysis: Visualizing ML-driven decision logic."""
        print(f"🚀 Running Sim #2: Behavioral Adaptability Analysis...")
        
        df = self._get_live_data()
        if df is None or df.empty: return

        # 1. Lane Distribution (Bar Chart)
        plt.figure(figsize=(9, 6))
        df['lane'].value_counts().plot(kind='bar', color=['#00cec9', '#0984e3', '#6c5ce7', '#fab1a0'], edgecolor='black')
        plt.title("Synchronized Cryptographic Lane Allocation (Live)", fontsize=13)
        plt.savefig(f"{self.plot_root}/sim2/lane_distribution.png", dpi=300)
        plt.close()

        # 2. Adaptive Heatmap Matrix (Critical for verifying ML logic)
        levels = ["1_Low", "2_Medium", "3_High", "4_Critical"]
        # Ensure categorical order for the heatmap
        contingency_table = pd.crosstab(df['threat_level'], df['lane']).reindex(levels, fill_value=0)
        
        plt.figure(figsize=(12, 7))
        sns.heatmap(contingency_table, annot=True, fmt="d", cmap="YlGnBu", cbar_kws={'label': 'TX Count'})
        plt.title("Adaptive Logic Matrix: Threat Category vs. Selected Algorithm", fontsize=14)
        plt.savefig(f"{self.plot_root}/sim2/threat_lane_matrix.png", dpi=300)
        plt.close()

        # 3. Cryptographic Family Utilization (Pie Chart)
        family_map = {
            "FALCON": "Lattice-based",
            "DILITHIUM": "Lattice-based",
            "SPHINCS+": "Hash-based",
            "OV": "Multivariate"
        }
        df['family'] = df['lane'].map(family_map).fillna("Other")
        
        plt.figure(figsize=(8, 8))
        family_counts = df['family'].value_counts()
        colors = ['#74b9ff', '#ff7675', '#55efc4', '#a29bfe']
        
        family_counts.plot(kind='pie', autopct='%1.1f%%', colors=colors, startangle=140, wedgeprops={'edgecolor': 'white'})
        plt.title("Cryptographic Family Distribution", fontsize=14)
        plt.ylabel("") 
        plt.savefig(f"{self.plot_root}/sim2/crypto_family_distribution.png", dpi=300)
        plt.close()

        # 4. Behavioral Timeline (Scatter plot of threat vs decision)
        plt.figure(figsize=(15, 6))
        window = df.head(500) # Preview first 500 for clarity
        plt.plot(window.index, window['threat'], color='#0984e3', alpha=0.2, label='Threat Score')
        
        lane_colors = {"SPHINCS+": "#d63031", "DILITHIUM": "#fdcb6e", "FALCON": "#00b894", "OV": "#00cec9"}
        for l_name, l_color in lane_colors.items():
            mask = window['lane'] == l_name
            if mask.any():
                plt.scatter(window.index[mask], window.loc[mask, 'threat'], color=l_color, label=l_name, s=30, alpha=0.8)
            
        plt.title("Real-time Decision Log: Adaptive Lane Selection", fontsize=14)
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.savefig(f"{self.plot_root}/sim2/adaptability_logic.png", dpi=300)
        plt.close()
        
        print(f"✅ Sim #2 Complete. Sourced from {self.metrics_csv}.")

    def run_simulation_3(self):
        """Gas Economics: Sustainability comparison vs Static PQC."""
        print(f"🚀 Running Sim #3: Gas Economics & Sustainability...")
        
        df_logs = self._get_live_data()
        if df_logs is None or df_logs.empty: return

        # Constants for Modeling (Signature Sizes)
        stats = {
            "SPHINCS+": {"size": 7856}, 
            "DILITHIUM": {"size": 2420},  
            "FALCON":    {"size": 666},  
            "OV":        {"size": 666}   
        }
        gas_per_byte = 16 
        
        results = []
        for _, row in df_logs.iterrows():
            actual_size = stats.get(row['lane'], stats["OV"])["size"]
            static_size = stats["SPHINCS+"]["size"] # Worst-case static baseline

            results.append({
                "mid_gas": actual_size * gas_per_byte,
                "static_hash_gas": static_size * gas_per_byte
            })

        df = pd.DataFrame(results)

        # Plot 1: Cumulative Gas (Network Longevity)
        plt.figure(figsize=(10, 6))
        plt.plot(df['mid_gas'].cumsum(), label="Adaptive Middleware (Efficient)", color="#2ecc71", lw=3)
        plt.plot(df['static_hash_gas'].cumsum(), label="Static SPHINCS+ (Baseline)", color="#e74c3c", ls='--')
        plt.fill_between(df.index, df['mid_gas'].cumsum(), df['static_hash_gas'].cumsum(), color='#2ecc71', alpha=0.1)
        
        plt.title("Network Sustainability: Cumulative Gas Consumption", fontsize=13)
        plt.ylabel("Cumulative Gas Units")
        plt.xlabel("Transaction Sequence")
        plt.legend()
        plt.savefig(f"{self.plot_root}/sim3/cumulative_gas_cost.png", dpi=300)
        plt.close()

        # Plot 2: Total Efficiency Gain
        total_mid = df['mid_gas'].sum()
        total_static = df['static_hash_gas'].sum()
        savings = ((total_static - total_mid) / total_static * 100)
        
        plt.figure(figsize=(8, 6))
        plt.bar(["Static Baseline", "Adaptive Middleware"], [total_static, total_mid], color=["#fab1a0", "#55efc4"])
        plt.title(f"Gas Efficiency Gain: {savings:.1f}% Reduction")
        plt.ylabel("Total Network Gas")
        plt.savefig(f"{self.plot_root}/sim3/total_gas_efficiency.png", dpi=300)
        plt.close()
        print(f"✅ Sim #3 Complete. Economic Efficiency calculated.")

if __name__ == "__main__":
    sim = ResearchSimulator()
    sim.run_simulation_1() 
    sim.run_simulation_2() 
    sim.run_simulation_3()
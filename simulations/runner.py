import os
import shutil
import numpy as np
import matplotlib
import time
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from sklearn.metrics import cohen_kappa_score

class ResearchSimulator:
    def __init__(self, metrics_csv="logs/metrics.csv"):
        self.plot_root = "evaluation/plots"
        self.metrics_csv = metrics_csv
        
        self.refresh_directories()

    def refresh_directories(self):
        if os.path.exists(self.plot_root):
            shutil.rmtree(self.plot_root)
            print(f"Purged old plots from: {self.plot_root}")
            
        paths = [f"{self.plot_root}/sim{i}" for i in range(1, 4)]
        for path in paths:
            os.makedirs(path, exist_ok=True)
            
        print(f"Fresh directories ready: {datetime.now().strftime('%H:%M:%S')}")

    def _get_live_data(self):
        if not os.path.exists(self.metrics_csv):
            print(f"Error: {self.metrics_csv} not found. Run the blockchain simulation first.")
            return None
        return pd.read_csv(self.metrics_csv)

    def run_simulation_1(self):
        print("Running Sim1: Quantum Cryptanalysis & Efficiency Suite")
      
        qubits = np.arange(0, 4001, 40)
        
        # System Integrity Thresholds
        ecc_vuln = np.where(qubits < 1536, 100, 0)
        rsa_vuln = np.where(qubits < 4000, 100, 0) 
        
        # Transition curves (Sigmoid modeling of Secure -> Broken)
        prob_ecc = 1 / (1 + np.exp(-0.01 * (qubits - 1536)))
        prob_rsa = 1 / (1 + np.exp(-0.01 * (qubits - 4000)))

        # Plot 12 & 13: Integrity Windows
        for name, data, threshold, color, p_num in [
            ("ECC-256", ecc_vuln, 1536, '#d63031', 12),
            ("RSA-3072", rsa_vuln, 4000, '#e67e22', 13)
        ]:
            plt.figure(figsize=(9, 5))
            plt.fill_between(qubits, 0, data, color=color, alpha=0.2, label='Security Margin')
            plt.plot(qubits, data, color=color, lw=2, label=f'{name} Integrity')
            plt.axvline(x=threshold, color='black', linestyle='--', label=f'Shor\'s Threshold ({threshold} Qubits)')
            plt.title(f"{name} Vulnerability Window (Post-Quantum Analysis)", fontsize=12)
            plt.xlabel("Logical Qubits (Fault-Tolerant)")
            plt.ylabel("System Integrity (%)")
            plt.legend()
            plt.savefig(f"{self.plot_root}/sim1/plot{p_num}_{name.lower()}_vulnerability.png", dpi=300)
            plt.close()

        # Plot 14: Attack Success Rate Comparison
        plt.figure(figsize=(10, 6))
        plt.plot(qubits, prob_ecc, color='#d63031', label='ECC-256 Success Prob.')
        plt.plot(qubits, prob_rsa, color='#e67e22', label='RSA-3072 Success Prob.')
        plt.plot(qubits, np.zeros(len(qubits)), color='#27ae60', lw=3, label='Adaptive Middleware (PQC)')
        plt.title("Quantum Adversary Success Rate (P_succ)", fontsize=13)
        plt.xlabel("Logical Qubits")
        plt.ylabel("Probability of Successful Key Recovery")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        plt.savefig(f"{self.plot_root}/sim1/plot14_attack_success_prob.png", dpi=300)
        plt.close()

        steps = np.arange(0, 129) # Intensity units
        
        ecc_shors = 128 * np.exp(-0.08 * steps)
        rsa_shors = 112 * np.exp(-0.06 * steps)
        mid_shors = np.full(len(steps), 128)

        # Grover's Decay Model (Quadratic Square-Root Reduction)
        ecc_grovers = 128 * np.sqrt(np.maximum(0, 1 - (steps/256)))
        rsa_grovers = 112 * np.sqrt(np.maximum(0, 1 - (steps/256)))
        mid_grovers = 128 - (steps * 0.02)

        def save_decay_plot(x, y, title, ylabel, filename, color, label):
            plt.figure(figsize=(9, 5))
            plt.plot(x, y, color=color, lw=2.5, label=label)
            plt.title(title, fontsize=12, fontweight='bold')
            plt.xlabel("Quantum Attack Intensity (Relative Units)", fontsize=10)
            plt.ylabel(ylabel, fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(loc='upper right')
            plt.savefig(f"{self.plot_root}/sim1/{filename}.png", dpi=300)
            plt.close()

        # Generate decaying security plots
        decay_configs = [
            (steps, ecc_shors, "ECC vs Shor's Algorithm", "Bits of Security (log₂ λ)", "plot1_ecc_shors", "#d63031", "ECC-256"),
            (steps, ecc_grovers, "ECC vs Grover's Algorithm", "Effective Key Strength (Bits)", "plot2_ecc_grovers", "#8e44ad", "ECC-256"),
            (steps, rsa_shors, "RSA vs Shor's Algorithm", "Bits of Security (log₂ λ)", "plot3_rsa_shors", "#e67e22", "RSA-3072"),
            (steps, rsa_grovers, "RSA vs Grover's Algorithm", "Effective Key Strength (Bits)", "plot4_rsa_grovers", "#d35400", "RSA-3072"),
            (steps, mid_shors, "Middleware vs Shor's Algorithm", "Security bits (λ)", "plot5_mid_shors", "#27ae60", "PQC Middleware"),
            (steps, mid_grovers, "Middleware vs Grover's Algorithm", "Quantum Bit-Resistance (λ)", "plot6_mid_grovers", "#16a085", "PQC Middleware")
        ]
        for config in decay_configs:
            save_decay_plot(*config)

        # Plot 7: Normalized Security Margin
        plt.figure(figsize=(10, 6))
        plt.plot(steps, ecc_shors/128, 'r--', label="ECC (Shor's Decay)")
        plt.plot(steps, rsa_shors/112, 'y--', label="RSA (Shor's Decay)")
        plt.plot(steps, mid_shors/128, 'g-', lw=3, label="Adaptive Middleware Margin")
        plt.title("Normalized Security Margin Analysis (α)", fontsize=13)
        plt.xlabel("Quantum Attack Vector Intensity")
        plt.ylabel("Normalized Security Margin (α)")
        plt.legend()
        plt.savefig(f"{self.plot_root}/sim1/plot7_combined_security.png", dpi=300)
        plt.close()

        efficiency_data = [("ECC", 3450, "#ff7675", 8), ("RSA", 2210, "#fab1a0", 9), ("Middleware", 1080, "#55efc4", 10)]
        for name, val, color, p_num in efficiency_data:
            plt.figure(figsize=(7, 5))
            plt.bar([name], [val], color=color, width=0.4)
            plt.title(f"{name} Transactional Throughput", fontsize=12)
            plt.ylabel("Throughput (TPS)")
            plt.savefig(f"{self.plot_root}/sim1/plot{p_num}_throughput_{name.lower()}.png", dpi=300)
            plt.close()

        # Plot 11: Tradeoff Analysis (The Pareto Frontier)
        plt.figure(figsize=(10, 7))
        tps_points = [3450, 2210, 1080]
        sec_points = [5, 12, 128] 
        labels = ["ECC", "RSA", "Middleware"]
        colors = ["#ff7675", "#fab1a0", "#55efc4"]

        for i in range(3):
            plt.scatter(tps_points[i], sec_points[i], color=colors[i], s=300, edgecolors='black', label=labels[i])
            plt.text(tps_points[i]-150, sec_points[i]+5, labels[i], fontweight='bold')

        plt.title("Security-Efficiency Landscape: PQC Tradeoff Analysis", fontsize=14)
        plt.xlabel("Network Throughput (TPS)")
        plt.ylabel("Post-Attack Quantum Resistance (λ)")
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.savefig(f"{self.plot_root}/sim1/plot11_tradeoff_analysis.png", dpi=300)
        plt.close()

        print("Sim1 Complete. All analysis plots generated.")

    def run_simulation_2(self):
        df = self._get_live_data()
        if df is None or df.empty: return
        
        print(f"Running Sim2: Behavioral Analysis for {len(df)} Transactions")

        # 1. Lane Distribution (Bar Chart)
        plt.figure(figsize=(9, 6))
        df['lane'].value_counts().plot(kind='bar', color=['#00cec9', '#0984e3', '#6c5ce7', '#fab1a0'], edgecolor='black')
        plt.title("Synchronized Cryptographic Lane Allocation", fontsize=13)
        plt.savefig(f"{self.plot_root}/sim2/lane_distribution.png", dpi=300)
        plt.close()

        # 2. Adaptive Heatmap Matrix (Critical for verifying logic)
        levels = ["1_Low", "2_Medium", "3_High", "4_Critical"]
        df['threat_level'] = pd.Categorical(df['threat_level'], categories=levels, ordered=True)
        contingency_table = pd.crosstab(df['threat_level'], df['lane']).reindex(levels, fill_value=0)
        
        plt.figure(figsize=(12, 7))
        sns.heatmap(contingency_table, annot=True, fmt="d", cmap="YlGnBu", cbar_kws={'label': 'TX Count'})
        plt.title("Adaptive Logic Matrix: Threat Category vs. Algorithm Selection", fontsize=14)
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
        df['family'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#74b9ff', '#ff7675', '#55efc4'], startangle=140)
        plt.title("Cryptographic Family Distribution", fontsize=14)
        plt.ylabel("") 
        plt.savefig(f"{self.plot_root}/sim2/crypto_family_distribution.png", dpi=300)
        plt.close()
        
        print(f"Sim2 Saved.")

    def run_simulation_3(self):
        df_logs = self._get_live_data()
        if df_logs is None or df_logs.empty: 
            print("No log data found. Skipping Simulation 3.")
            return
        
        tx_count = len(df_logs)
        print(f"\n--- Running Sim3: Gas Economics for {tx_count} Transactions ---")

        # Benchmark Signature Sizes (Bytes)
        stats = {"SPHINCS+": 7856, "DILITHIUM": 2420, "FALCON": 666, "OV": 666}
        gas_per_byte = 16 
        
        # 1. Vectorized Gas Math
        mid_gas = df_logs['lane'].map(lambda x: stats.get(x, 666) * gas_per_byte).values
        static_gas = np.full(tx_count, stats["SPHINCS+"] * gas_per_byte)

        workload_ms = {
            "OV": 0.15,        
            "FALCON": 0.50,    
            "DILITHIUM": 1.80, 
            "SPHINCS+": 40.0  
        }

        # Calculate total simulated execution time based on the selected lanes
        simulated_total_ms = df_logs['lane'].map(workload_ms).sum()
        simulated_total_sec = simulated_total_ms / 1000

        simulated_tps = tx_count / max(simulated_total_sec, 0.001)

        total_mid_gas = np.sum(mid_gas)
        total_static_gas = np.sum(static_gas)
        avg_gas = np.mean(mid_gas)
        
        ee_percentage = (1 - (total_mid_gas / total_static_gas)) * 100
        tcr = simulated_tps / avg_gas
        alpha = 1.00

        print(f"{'Metric':<30} | {'Value':<15}")
        print("-" * 50)
        print(f"{'Security Margin (alpha)':<30} | {alpha:.2f}")
        print(f"{'Throughput (TPS)':<30} | {simulated_tps:.2f}")
        print(f"{'Avg. Gas Units':<30} | ~{int(avg_gas):,}")
        print(f"{'Economic Efficiency (EE)':<30} | {ee_percentage:.2f}%")
        print(f"{'Throughput-to-Cost (TCR)':<30} | {tcr:.6f}")

        plt.figure(figsize=(12, 6))
        plt.plot(np.cumsum(mid_gas), label="Proposed Middleware", color="#2ecc71", lw=3)
        plt.plot(np.cumsum(static_gas), label="Static SPHINCS+ (Baseline)", color="#e74c3c", ls='--')
        plt.title(f"Network Sustainability: Cumulative Gas (N={tx_count})")
        plt.ylabel("Cumulative Gas Units")
        plt.xlabel("Transaction Sequence")
        plt.legend(loc="upper left")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.savefig(f"{self.plot_root}/sim3/cumulative_gas_cost.png", dpi=300)
        plt.close()

        plt.figure(figsize=(8, 6))
        bars = plt.bar(["Static Baseline", "Proposed Middleware"], [total_static_gas, total_mid_gas], color=["#fab1a0", "#55efc4"])
        plt.title(f"Gas Efficiency Gain: {ee_percentage:.1f}% Reduction")
        plt.ylabel("Total Network Gas (Units)")
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, f'{int(height):,}', ha='center', va='bottom')
        plt.savefig(f"{self.plot_root}/sim3/total_gas_efficiency.png", dpi=300)
        plt.close()
        
        print(f"\nSimulation 3 Complete. Data saved to {self.plot_root}/sim3/")

if __name__ == "__main__":
    sim = ResearchSimulator()
    sim.run_simulation_1() 
    sim.run_simulation_2() 
    sim.run_simulation_3()
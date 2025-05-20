from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import math
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

class QuantumPoetryGenerator:
    def __init__(self):
        self.simulator = AerSimulator()
        
        self.datasets = {
            'words': ["vui", "buồn", "yêu", "ghét", "hy vọng", "thất vọng"],
            'emotions': ["hạnh phúc", "tức giận", "sợ hãi", "ngạc nhiên", "chán nản"],
            'themes': ["thiên nhiên", "tình yêu", "cái chết", "thời gian", "kỷ niệm"]
        }
        
    def calculate_optimal_shots(self, N):
        base_shots = 1000
        scaling_factor = max(1, math.log2(N)**2)
        return min(100000, int(base_shots * scaling_factor))
    
    def create_quantum_circuit(self, data):
        N = len(data)
        num_qubits = max(1, math.ceil(math.log2(N)))
        
        qc = QuantumCircuit(num_qubits, num_qubits)
        
        for qubit in range(num_qubits):
            qc.h(qubit)
        
        if N > 1:
            theta = 2 * np.arcsin(np.sqrt(1/N))
            qc.ry(theta, 0)
        
        qc.measure_all()
        return qc
    
    def safe_state_conversion(self, state, N):
        try:
            state_int = int(state, 2)
            return state_int if state_int < N else None
        except ValueError:
            return None
    
    def generate_poetry(self, dataset_name, show_plot=False):
        data = self.datasets.get(dataset_name)
        if not data:
            raise ValueError(f"Dataset {dataset_name} không tồn tại. Chọn một trong: {list(self.datasets.keys())}")
        
        N = len(data)
        shots = self.calculate_optimal_shots(N)
        qc = self.create_quantum_circuit(data)
        
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Xử lý kết quả an toàn
        output = defaultdict(int)
        total_valid = 0
        
        for state, count in counts.items():
            state_int = self.safe_state_conversion(state, N)
            if state_int is not None:
                output[data[state_int]] += count
                total_valid += count
        
        # Chuẩn hóa kết quả
        if total_valid > 0:
            for word in output:
                output[word] = int(output[word] / total_valid * shots)
        
        if show_plot:
            self.plot_results(counts, data, dataset_name)
            
        return dict(output)
    
    def plot_results(self, counts, data, title):
        N = len(data)
        states = []
        probs = []
        
        for state in sorted(counts.keys()):
            state_int = self.safe_state_conversion(state, N)
            if state_int is not None:
                label = f"{state}\n({data[state_int]})"
            else:
                label = f"{state}\n(Invalid)"
            states.append(label)
            probs.append(counts[state]/sum(counts.values()))
        
        plt.figure(figsize=(10, 5))
        plt.bar(states, probs)
        plt.xlabel('Trạng thái lượng tử')
        plt.ylabel('Xác suất')
        plt.title(f'Phân phối xác suất cho {title}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Sử dụng
generator = QuantumPoetryGenerator()

# Kiểm tra với số shots nhỏ trước
print("=== Kết quả test ===")
test_result = generator.generate_poetry('words', show_plot=True)
print(test_result)
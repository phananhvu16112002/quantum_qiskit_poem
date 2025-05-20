from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.qasm2 import dump
import math
import numpy as np
from collections import defaultdict
import json

class QuantumPoetryGenerator:
    def __init__(self, data, weights=None, max_qubits=20, num_groups=10, epsilon=0.01):
        if not data:
            raise ValueError("Danh sách dữ liệu không được rỗng")
        self.data = data
        self.N = len(data)
        self.weights = self.assign_group_weights(num_groups) if weights is None else weights
        self.weights = np.array(self.weights) / sum(self.weights)
        self.num_qubits = math.ceil(math.log2(self.N))
        if self.num_qubits > max_qubits:
            raise ValueError("Dữ liệu quá lớn, vượt quá số qubit hỗ trợ")
        self.simulator = Aer.get_backend('qasm_simulator')
        self.qubit_weights = np.random.uniform(0.5, 1.5, self.num_qubits)
        self.epsilon = epsilon  # Sai số mong muốn
    
    def assign_group_weights(self, num_groups=10):
        """Gán trọng số cho các nhóm từ"""
        group_size = max(1, self.N // num_groups)
        group_weights = np.random.uniform(0.5, 2.0, num_groups)
        weights = []
        for i in range(self.N):
            group_idx = i // group_size
            weights.append(group_weights[min(group_idx, num_groups - 1)])
        return np.array(weights)
    
    def calculate_optimal_shots(self):
        """Tính số shots động dựa trên N, num_qubits, và epsilon"""
        base_shots = 1000
        max_shots = 100000
        # Công thức: shots = base_shots * (log2(N) + 1) * (2^num_qubits / N) * (1 / epsilon^2)
        shots = base_shots * (math.log2(max(2, self.N)) + 1) * (2**self.num_qubits / max(1, self.N)) * (1 / (self.epsilon ** 2))
        return min(max_shots, round(shots))
    
    def map_state_to_item(self, state):
        """Ánh xạ trạng thái qubit sang phần tử dữ liệu với xáo trộn ngẫu nhiên"""
        state_int = int(state, 2)
        np.random.seed(None)
        shuffled_indices = np.random.permutation(self.N)
        return self.data[shuffled_indices[state_int]] if state_int < self.N else None
    
    def create_quantum_circuit(self):
        """Tạo mạch lượng tử với các góc xoay ngẫu nhiên và rối"""
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        
        for i in range(self.num_qubits):
            theta_y = np.random.uniform(0, np.pi) * self.qubit_weights[i]
            theta_x = np.random.uniform(0, np.pi) * self.qubit_weights[i]
            qc.ry(theta_y, i)
            qc.rx(theta_x, i)
        
        for i in range(self.num_qubits - 1):
            if np.random.random() > 0.3:
                qc.cx(i, i + 1)
            if np.random.random() > 0.3:
                qc.cz(i, i + 1)
        
        for i in range(self.num_qubits):
            if np.random.random() > 0.5:
                qc.h(i)
        
        qc.measure(range(self.num_qubits), range(self.num_qubits))
        return qc
    
    def shuffle_data(self):
        """Thực hiện xáo trộn lượng tử với xác suất ngẫu nhiên"""
        try:
            qc = self.create_quantum_circuit()
            shots = self.calculate_optimal_shots()
            result = self.simulator.run(qc, shots=shots).result()
            counts = result.get_counts()
        except Exception as e:
            raise RuntimeError(f"Lỗi khi chạy mô phỏng: {str(e)}")
        
        output_dict = defaultdict(int)
        total_valid = 0
        
        for state, count in counts.items():
            item = self.map_state_to_item(state)
            if item is not None:
                output_dict[item] += count
                total_valid += count
        
        if total_valid == 0:
            raise ValueError("Không có trạng thái hợp lệ nào được đo lường")
        
        for item in output_dict:
            output_dict[item] = round(output_dict[item] / total_valid * shots)
        
        return dict(sorted(output_dict.items(), key=lambda x: x[1], reverse=True))
    
    def generate_poem(self, num_lines=4, style="free"):
        """Tạo bài thơ từ kết quả xáo trộn"""
        result = self.shuffle_data()
        top_words = list(result.keys())[:min(num_lines, len(result))]
        if style == "luc_bat":
            poem = []
            for i in range(0, len(top_words), 2):
                if i + 1 < len(top_words):
                    poem.append(f"{top_words[i]} vang vọng trời {top_words[i+1]}")
                else:
                    poem.append(f"{top_words[i]} vang vọng mãi")
        elif style == "haiku":
            if len(top_words) >= 3:
                poem = [f"{top_words[0]} lặng lẽ bay", f"{top_words[1]} trong gió chiều tà", f"{top_words[2]} vương vấn."]
            else:
                poem = [f"{word} lặng lẽ bay" for word in top_words]
        else:
            poem = [f"{word} như gió thoảng qua" for word in top_words]
        return "\n".join(poem)
    
    def print_results(self):
        """In kết quả xáo trộn và bài thơ mẫu"""
        result = self.shuffle_data()
        total_shots = sum(result.values())
        
        print("\nKết quả xáo trộn lượng tử (từ cao đến thấp):")
        print("| Phần tử      | Số lần | Tỷ lệ  |")
        print("|--------------|--------|--------|")
        for item, count in result.items():
            print(f"| {item:<12} | {count:>6} | {(count/total_shots)*100:>5.1f}% |")
        
        print("\nBài thơ mẫu:")
        print(self.generate_poem())
    
    def check_randomness(self, num_runs=3):
        """Kiểm tra tính ngẫu nhiên qua các lần chạy"""
        distributions = [self.shuffle_data() for _ in range(num_runs)]
        print("\nSo sánh phân bố qua các lần chạy:")
        for i, dist in enumerate(distributions):
            total = sum(dist.values())
            print(f"\nLần chạy {i+1}:")
            for item, count in dist.items():
                print(f"{item}: {(count/total)*100:.1f}%")
    
    def save_results(self, filename="quantum_poetry.json"):
        """Lưu kết quả xáo trộn vào file"""
        result = self.shuffle_data()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Kết quả đã được lưu vào {filename}")
    
    def save_circuit(self, filename="quantum_circuit.qasm"):
        """Lưu mạch lượng tử vào file"""
        qc = self.create_quantum_circuit()
        with open(filename, 'w', encoding='utf-8') as f:
            dump(qc, f)
        print(f"Mạch lượng tử đã được lưu vào {filename}")

# Sử dụng
if __name__ == "__main__":
    data = ["vui", "đã", "sướng", "hạnh phúc", "thú vị"]
    weights = [1.0, 1.0, 1.0, 1.0, 1.0]
    poet = QuantumPoetryGenerator(data, weights, epsilon=0.01)
    poet.print_results()
    poet.check_randomness(num_runs=3)
    poet.save_results()
    poet.save_circuit()
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.qasm2 import dump
import math
import numpy as np
from collections import defaultdict
import json

class QuantumPoetryGenerator:
    # Danh sách từ thơ để mở rộng tập dữ liệu
    POETIC_WORDS = {
        "vui": ["rạng rỡ", "hạnh phúc", "nụ cười"],
        "sướng": ["thỏa nguyện", "hân hoan"],
        "đã": ["tuyệt", "phấn khích"],
        "buồn": ["lặng", "mờ", "u uất"],
        "mây": ["trời", "bồng bềnh", "phiêu diêu"],
        "mưa": ["ướt", "lạnh", "tí tách"],
        "nắng": ["sáng", "ấm", "rực rỡ"],
        "gió": ["thoảng", "vi vu"],
        "sương": ["mịt mù", "mỏng manh"]
    }

    # Suy ra thời tiết từ thời gian
    TIME_WEATHER = {
        "sáng": ["nắng", "sương"],
        "tối": ["mưa", "gió"],
        "mùa xuân": ["nắng", "mưa"],
        "mùa thu": ["mát", "gió"],
        "mùa hè": ["nắng", "nóng"],
        "mùa đông": ["lạnh", "sương"]
    }

    def __init__(self, data, weights=None, max_qubits=20, num_groups=10, epsilon=0.01, emotion=None, space=None, time=None):
        if not data:
            raise ValueError("Danh sách dữ liệu không được rỗng")
        self.emotion = emotion
        self.space = space
        self.time = time
        self.weather = self.infer_weather(time)
        self.data = self.expand_data(data)
        self.N = len(self.data)
        self.weights = self.adjust_weights(weights, num_groups)
        self.weights = np.array(self.weights) / sum(self.weights)
        self.num_qubits = math.ceil(math.log2(self.N))
        if self.num_qubits > max_qubits:
            raise ValueError("Dữ liệu quá lớn, vượt quá số qubit hỗ trợ")
        self.simulator = Aer.get_backend('qasm_simulator')
        self.qubit_weights = np.random.uniform(0.5, 1.5, self.num_qubits)
        self.epsilon = epsilon
    
    def infer_weather(self, time):
        """Suy ra thời tiết từ thời gian"""
        if not time or time not in self.TIME_WEATHER:
            return None
        return np.random.choice(self.TIME_WEATHER[time])
    
    def expand_data(self, data):
        """Mở rộng tập dữ liệu dựa trên cảm xúc, không gian, thời gian, thời tiết"""
        expanded_data = list(data)
        for word in data:
            if word in self.POETIC_WORDS:
                expanded_data.extend(self.POETIC_WORDS[word])
        if self.emotion in self.POETIC_WORDS:
            expanded_data.extend(self.POETIC_WORDS[self.emotion])
        if self.space in self.POETIC_WORDS:
            expanded_data.extend(self.POETIC_WORDS[self.space])
        if self.weather in self.POETIC_WORDS:
            expanded_data.extend(self.POETIC_WORDS[self.weather])
        # Loại bỏ trùng lặp và giữ tập từ hợp lý
        return list(dict.fromkeys(expanded_data))[:16]  # Giới hạn 16 từ để tránh quá lớn
    
    def adjust_weights(self, weights, num_groups):
        """Điều chỉnh trọng số dựa trên cảm xúc, không gian, thời gian, thời tiết"""
        if weights is not None and len(weights) == self.N:
            adjusted_weights = weights.copy()
        else:
            adjusted_weights = self.assign_group_weights(num_groups)
        
        # Tăng trọng số cho từ phù hợp
        for i, word in enumerate(self.data):
            boost = 1.0
            if self.emotion and (word == self.emotion or word in self.POETIC_WORDS.get(self.emotion, [])):
                boost *= 2.0
            if self.space and (word == self.space or word in self.POETIC_WORDS.get(self.space, [])):
                boost *= 2.0
            if self.weather and (word == self.weather or word in self.POETIC_WORDS.get(self.weather, [])):
                boost *= 2.0
            adjusted_weights[i] *= boost
        
        return adjusted_weights
    
    def assign_group_weights(self, num_groups=10):
        group_size = max(1, self.N // num_groups)
        group_weights = np.random.uniform(0.5, 2.0, num_groups)
        weights = []
        for i in range(self.N):
            group_idx = i // group_size
            weights.append(group_weights[min(group_idx, num_groups - 1)])
        return np.array(weights)
    
    def calculate_optimal_shots(self):
        base_shots = 1000
        max_shots = 100000
        shots = base_shots * (math.log2(max(2, self.N)) + 1) * (2**self.num_qubits / max(1, self.N)) * (1 / (self.epsilon ** 2))
        return min(max_shots, round(shots))
    
    def map_state_to_item(self, state):
        state_int = int(state, 2)
        np.random.seed(None)
        shuffled_indices = np.random.permutation(self.N)
        return self.data[shuffled_indices[state_int]] if state_int < self.N else None
    
    def create_quantum_circuit(self):
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
        
        return dict(sorted(output_dict.items(), key=lambda x: x[1], reverse=True)), shots, total_valid
    
    # def generate_poem(self, num_lines=4, style="free"):
    #     result, shots, total_valid = self.shuffle_data()
    #     top_words = list(result.keys())[:min(num_lines, len(result))]
        
    #     # Thêm bối cảnh
    #     prefix = ""
    #     if self.space:
    #         prefix += f"Trong {self.space}, "
    #     if self.time:
    #         prefix += f"vào {self.time}, "
    #     if self.weather:
    #         prefix += f"giữa {self.weather}, "
    #     if self.emotion:
    #         prefix += f"lòng {self.emotion}, "
    #     if prefix:
    #         prefix = prefix[:-2] + "\n"
        
    #     if style == "luc_bat":
    #         poem = []
    #         for i in range(0, len(top_words), 2):
    #             if i + 1 < len(top_words):
    #                 poem.append(f"{top_words[i]} vang vọng trời {top_words[i+1]}")
    #             else:
    #                 poem.append(f"{top_words[i]} vang vọng mãi")
    #     elif style == "haiku":
    #         if len(top_words) >= 3:
    #             poem = [f"{top_words[0]} lặng lẽ bay", f"{top_words[1]} trong gió chiều tà", f"{top_words[2]} vương vấn."]
    #         else:
    #             poem = [f"{word} lặng lẽ bay" for word in top_words]
    #     else:
    #         poem = [f"{word} như gió thoảng qua" for word in top_words]
        
    #     poem_text = prefix + "\n".join(poem)
    #     return poem_text, result, shots, total_valid, self.data
    
    def print_results(self):
        result, shots, total_valid = self.shuffle_data()
        total_shots = sum(result.values())
        print("\nKết quả xáo trộn lượng tử (từ cao đến thấp):")
        print("| Phần tử      | Số lần | Tỷ lệ  |")
        print("|--------------|--------|--------|")
        for item, count in result.items():
            print(f"| {item:<12} | {count:>6} | {(count/total_shots)*100:>5.1f}% |")
    
    def check_randomness(self, num_runs=3):
        distributions = [self.shuffle_data()[0] for _ in range(num_runs)]
        print("\nSo sánh phân bố qua các lần chạy:")
        for i, dist in enumerate(distributions):
            total = sum(dist.values())
            print(f"\nLần chạy {i+1}:")
            for item, count in dist.items():
                print(f"{item}: {(count/total)*100:.1f}%")
    
    def save_results(self, filename="quantum_poetry.json"):
        result, _, _ = self.shuffle_data()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Kết quả đã được lưu vào {filename}")
    
    def save_circuit(self, filename="quantum_circuit.qasm"):
        qc = self.create_quantum_circuit()
        with open(filename, 'w', encoding='utf-8') as f:
            dump(qc, f)
        print(f"Mạch lượng tử đã được lưu vào {filename}")
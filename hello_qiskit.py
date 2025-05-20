from qiskit import QuantumCircuit
from qiskit_aer import Aer
import math
import numpy as np
from collections import defaultdict

class QuantumDataShuffler:
    def __init__(self, data):
        self.data = data
        self.N = len(data)
        self.num_qubits = math.ceil(math.log2(self.N))
        self.simulator = Aer.get_backend('qasm_simulator')
        
    def calculate_optimal_shots(self):
        """Tính số shots tối ưu dựa trên kích thước dữ liệu"""
        base_shots = 1000
        scaling_factor = max(1, math.log2(self.N)**2)
        return min(100000, int(base_shots * scaling_factor))
    
    def map_state_to_item(self, state):
        """Ánh xạ trạng thái qubit sang phần tử dữ liệu"""
        state_int = int(state, 2)
        return self.data[state_int] if state_int < self.N else None
    
    def create_quantum_circuit(self):
        """Tạo mạch lượng tử"""
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        
        # Áp dụng cổng xoay RY để tạo giao thoa lượng tử
        theta = 2 * np.arccos(np.sqrt(self.N / 2**self.num_qubits))
        qc.ry(theta, 0)
        
        # Áp dụng cổng Hadamard cho các qubit còn lại
        for i in range(1, self.num_qubits):
            qc.h(i)
            
        qc.measure(range(self.num_qubits), range(self.num_qubits))
        return qc
    
    def shuffle_data(self):
        """Thực hiện xáo trộn lượng tử và trả về kết quả đã sắp xếp"""
        qc = self.create_quantum_circuit()
        shots = self.calculate_optimal_shots()
        
        # Chạy mô phỏng
        result = self.simulator.run(qc, shots=shots).result()
        counts = result.get_counts()
        
        # Xử lý kết quả
        output_dict = defaultdict(int)
        total_valid = 0
        
        for state, count in counts.items():
            item = self.map_state_to_item(state)
            if item is not None:
                output_dict[item] += count
                total_valid += count
        
        # Chuẩn hóa kết quả
        if total_valid > 0:
            for item in output_dict:
                output_dict[item] = round(output_dict[item] / total_valid * shots)
        
        # Sắp xếp từ cao đến thấp
        sorted_results = sorted(output_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_results)
    
    # def print_results(self):
    #     """In kết quả đã sắp xếp và phân bố xác suất"""
    #     result = self.shuffle_data()
    #     total_shots = sum(result.values())
        
    #     print("\nKết quả xáo trộn lượng tử (từ cao đến thấp):")
    #     for item, count in result.items():
    #         print(f"- {item}: {count} lần ({(count/total_shots)*100:.1f}%)")
    def print_results(self):
        result = self.shuffle_data()
        total_shots = sum(result.values())
    
        print("\nKết quả xáo trộn lượng tử:")
        print("| Phần tử      | Số lần | Tỷ lệ  |")
        print("|--------------|--------|--------|")
        for item, count in result.items():
            print(f"| {item:<12} | {count:>6} | {(count/total_shots)*100:>5.1f}% |")


# Sử dụng
if __name__ == "__main__":
    data = ["vui", "đã", "sướng", "hạnh phúc", "thú vị"]
    shuffler = QuantumDataShuffler(data)
    
    print(f"Dữ liệu đầu vào: {data}")
    print(f"Số shots được tính toán tự động: {shuffler.calculate_optimal_shots()}")
    shuffler.print_results()
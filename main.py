from hello_qiskit import QuantumPoetryGenerator
from qiskit import QuantumCircuit

def main():
    # Thiết lập tham số
    data = ["vui", "sướng", "đã"]
    weights = [1.0, 1.0, 1.0]
    emotion = "buồn"
    space = "mưa"
    time = "tối"
    
    # Khởi tạo QuantumPoetryGenerator
    poet = QuantumPoetryGenerator(
        data=data,
        weights=weights,
        epsilon=0.01,
        num_groups=5,
        emotion=emotion,
        space=space,
        time=time
    )
    
    # In kết quả xáo trộn và bài thơ
    poet.print_results()
    
    # Kiểm tra tính ngẫu nhiên qua 3 lần chạy
    # poet.check_randomness(num_runs=3)
    
    # Lưu kết quả và mạch lượng tử
    # poet.save_results()
    # poet.save_circuit()
    # qc = QuantumCircuit.from_qasm_file("quantum_circuit.qasm")
    # print(qc.draw())
    

if __name__ == "__main__":
    main()
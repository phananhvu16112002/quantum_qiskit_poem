Quantum Poetry Generator API
This is a FastAPI application that uses Qiskit’s quantum computing framework to shuffle a list of words with quantum-inspired randomness. The app provides a /shuffle endpoint that accepts an array of strings (e.g., ["vui", "sướng", "đã"]) and returns a probability distribution of the shuffled words, computed using a quantum circuit simulated locally with AerSimulator.
Features

Endpoint: POST /shuffle accepts a JSON payload with a data field containing an array of strings.
Output: Returns a dictionary with words and their frequency counts, simulating quantum randomness.
Error Handling: Returns HTTP 404 for invalid input formats (e.g., non-string arrays, empty arrays) with descriptive messages.
Local Simulation: Uses Qiskit’s AerSimulator, no IBM Quantum account needed.
Shots: ~50,000 quantum circuit shots by default (epsilon=0.01), adjustable in quantum_poetry_generator.py.

Prerequisites

Python: Version 3.9 or higher (recommended: 3.11).
pip: Package manager for installing dependencies.
Git (optional): For cloning the repository.

Setup Instructions
1. Save Files
Clone or create the following files in a project directory (e.g., quantum-poetry-fastapi):

quantum_poetry_generator.py: Core quantum shuffling logic using Qiskit.
main.py: FastAPI application with the /shuffle endpoint.
requirements.txt: List of Python dependencies.

Example directory structure:
quantum-poetry-fastapi/
├── quantum_poetry_generator.py
├── main.py
├── requirements.txt

2. Install Dependencies
Navigate to the project directory and install the required libraries:
pip install -r requirements.txt

Dependencies (from requirements.txt):

qiskit>=0.46.0
qiskit-aer>=0.13.0
numpy>=1.21.0
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.8.0

3. Run the FastAPI Server
Start the FastAPI server locally:
python main.py


The server runs at http://localhost:8000.
Access the interactive Swagger UI at http://localhost:8000/docs to test the endpoint.

4. Test the /shuffle Endpoint
Use curl, Postman, or Swagger UI to send a POST request to http://localhost:8000/shuffle.
Example Request (using curl):
curl -X POST "http://localhost:8000/shuffle" -H "Content-Type: application/json" -d '{
    "data": ["vui", "sướng", "đã"]
}'

Sample Response (output is randomized due to quantum simulation):
{
    "distribution": {
        "vui": 18000,
        "sướng": 16000,
        "đã": 16000
    }
}


Explanation:
The distribution maps each word to its frequency count, derived from ~50,000 quantum circuit shots (epsilon=0.01).
Probabilities are nearly uniform due to default weights in assign_group_weights.
Actual counts vary per run due to quantum randomness.



Error Responses (HTTP 404):

Invalid format (e.g., {"data": [1, 2, 3]}):{
    "detail": "Sai format: data phải là mảng chuỗi"
}


Empty array (e.g., {"data": []}):{
    "detail": "Danh sách dữ liệu không được rỗng"
}



5. Notes

Performance: With ~50,000 shots, responses take a few seconds on typical hardware. For faster results, adjust epsilon in quantum_poetry_generator.py (e.g., epsilon=0.1 reduces shots to ~500).
Local Simulation: No internet or IBM Quantum account required, as AerSimulator runs locally.
Deployment: For production, consider deploying to platforms like Railway (recommended for heavy Qiskit apps) or Vercel (requires size optimization due to 250 MB limit). See deployment guides for details.
Customization: Modify max_qubits, num_groups, or epsilon in quantum_poetry_generator.py to tweak quantum circuit behavior.

Troubleshooting

Dependency Errors: Ensure Python 3.9+ and run pip install -r requirements.txt again.
Server Not Starting: Check main.py logs for errors (e.g., missing dependencies, port conflicts).
404 Errors: Verify JSON payload format ({"data": ["word1", "word2", ...]}) and endpoint (/shuffle).

License
MIT License (or specify your preferred license).

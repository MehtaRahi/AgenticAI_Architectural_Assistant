import requests
import mlflow
import time
import os

# Set S3/MinIO credentials for MLflow artifact logging
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "password"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"

# Define the local backend endpoint
BACKEND_URL = "http://localhost:8000/api/chat"

# Set up MLflow tracking
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Agent_Architecture_Evaluation")

# Benchmark questions
test_queries = [
    "What is the minimum clear width required for doorways under ADA Section 404?",
    "What clearance is required for a U-shaped kitchen?",
    "Does a hallway need to be 36 inches or 42 inches wide?"
]

def run_evaluation():
    print("Starting AI Agent Benchmarking...")
    
    with mlflow.start_run(run_name="Baseline_Test"):
        for i, query in enumerate(test_queries):
            print(f"\n--- Testing Query {i+1} ---")
            print(f"Q: {query}")
            
            start_time = time.time()
            try:
                response = requests.post(BACKEND_URL, json={"query": query}, timeout=180)
                response.raise_for_status()
                data = response.json()
                
                latency = time.time() - start_time
                
                print(f"Latency: {latency:.2f} seconds")
                print(f"Retrieved Codes: {len(data.get('retrieved_codes', []))}")
                
                # Log metrics to MLflow
                mlflow.log_metric(f"latency_q{i}", latency)
                mlflow.log_metric(f"retrieved_docs_q{i}", len(data.get('retrieved_codes', [])))
                
                # Log inputs and outputs as dicts or text
                mlflow.log_dict(data, f"responses/response_q{i}.json")
                mlflow.log_text(query, f"prompts/prompt_q{i}.txt")
                
            except Exception as e:
                print(f"Error querying backend: {e}")

if __name__ == "__main__":
    run_evaluation()

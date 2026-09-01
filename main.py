from src.graph import nexus_app

def run_nexus():
    print("--- Nexus Agent: Self-Correcting RAG Initialized ---")
    question = input("\nApna question puchiye: ")
    
    inputs = {
        "question": question,
        "retry_count": 0
    }
    
    print("\nProcessing with self-correction checks...\n")
    for output in nexus_app.stream(inputs):
        for key, value in output.items():
            print(f"Node Executed: [{key}]")
    
    final_output = value.get("generation", "No generation produced.")
    print("\n" + "="*50)
    print("FINAL ANSWER:")
    print(final_output)
    print("="*50)

if __name__ == "__main__":
    run_nexus()
import os
from dotenv import load_dotenv
from workflow.graph import OrchestratorGraph

# Load environment variables
load_dotenv()

def main():
    # Initialize the orchestrator
    orchestrator = OrchestratorGraph()
    
    # Example query
    query = "How do I authenticate API requests?"
    
    # Run the workflow
    result = orchestrator.invoke(query)
    
    print(f"Query: {query}")
    print(f"\nFinal Answer:\n{result['final_answer']}")
    
    # Print sources if needed
    print(f"\nSources consulted:")
    for r in result.get('results', []):
        print(f"- {r['source']}")

if __name__ == "__main__":
    main()
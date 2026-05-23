# main.py

from dotenv import load_dotenv
load_dotenv()  # Loads ANTHROPIC_API_KEY from .env

from graph.orchestrator import build_graph

# Build the graph
graph = build_graph()

# Define the initial state
initial_state = {
    "issue": "Fix the login bug where users can't reset their password",
    "code_context": None,
    "plan": None,
    "patch": None,
    "tests": None,
    "pr_url": None,
}

# Run the graph
print("\n=== Starting Multi-Agent Pipeline ===\n")
result = graph.invoke(initial_state)

print("\n=== Pipeline Complete. Final State: ===\n")
for key, value in result.items():
    print(f"  {key}: {value}")

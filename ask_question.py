from rag import query_data

question = "what is sharding for"
print(f"Question: {question}\n")
print("Searching and generating answer...")
answer = query_data(question)
print(f"\nAnswer: {answer}")


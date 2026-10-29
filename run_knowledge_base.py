
from forgebid.knowledge_base import CompanyKnowledgeBase


def main():
    knowledge_base = CompanyKnowledgeBase()

    count = knowledge_base.index_documents()
    print(f"\nIndexed {count} chunks successfully.")

    query = "What security practices does the company follow?"
    results = knowledge_base.search(query, top_k=3)

    print(f"\nQuestion: {query}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk_number']}")
        print(f"Distance: {result['distance']:.4f}")
        print(result["text"])


if __name__ == "__main__":
    main()

import dspy
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)
embedder = dspy.Embedder(model="openai/text-embedding-3-large")


def convert_pdf_to_markdown(pdf_path):
    result = md.convert(pdf_path)
    markdown = result.text_content
    return markdown


def create_embeddings(documents, batch_size=1):
    embeddings = embedder(documents, batch_size=batch_size)
    return embeddings


if __name__ == "__main__":
    documents = ["hello", "world"]
    embeddings = create_embeddings(documents)
    print(embeddings.shape)

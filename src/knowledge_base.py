from langchain.schema.retriever import BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from .logger_config import logger
from .settings import DATA_FILE_PATH


def load_documents(file_path: str) -> list:
    """Loads documents from the specified file path using TextLoader.

    Args:
        file_path: The path to the markdown file.

    Returns:
        A list of loaded documents.
    """
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    return documents


def create_retriever_from_documents(documents: list) -> BaseRetriever:
    """Creates a FAISS vector store and retriever from a list of documents.

    Args:
        documents: A list of documents to process.

    Returns:
        A Langchain retriever instance.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    if not texts:
        raise ValueError(
            'No text content found after splitting documents. Cannot create vector store.'
        )

    try:
        vectorstore = FAISS.from_documents(texts, embeddings)
    except Exception as e:
        logger.exception('Error creating FAISS vector store: %s', e)
        raise

    return vectorstore.as_retriever(search_kwargs={'k': 3})  # Retrieve top 3 relevant chunks


_restaurant_retriever: BaseRetriever | None = None


def get_restaurant_retriever() -> BaseRetriever:
    """Initializes and returns a singleton retriever for the restaurant knowledge base.

    This function ensures that the document loading and vector store creation
    happens only once.

    Returns:
        The initialized Langchain retriever.

    Raises:
        FileNotFoundError: If the data file specified in settings is not found.
        ValueError: If no text content is found in the documents.
    """
    global _restaurant_retriever  # pylint: disable=global-statement
    if _restaurant_retriever is None:
        if not DATA_FILE_PATH.exists():
            raise FileNotFoundError(f'Knowledge base file not found at: {DATA_FILE_PATH}')

        documents = load_documents(str(DATA_FILE_PATH))
        if not documents:
            raise ValueError(f'No documents were loaded from {DATA_FILE_PATH}.')

        _restaurant_retriever = create_retriever_from_documents(documents)

    return _restaurant_retriever

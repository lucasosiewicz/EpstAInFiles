from ai.embeddings import EmbeddingModel
from db import Database, DocumentRepository
from utils import download_dataset, get_dataset_files, load_dataset_file_as_jsons, build_document_text


class IngestionPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.db = Database()

    def run(self):
        dataset_path = download_dataset()
        dataset_filepaths = get_dataset_files(dataset_path)

        with self.db.session() as session:
            repo = DocumentRepository(session)
            for filepath in dataset_filepaths:
                for data in load_dataset_file_as_jsons(filepath):
                    text = build_document_text(data)
                    chunks, embeddings = self.embedding_model.embed_documents([text])
                    repo.insert(data, chunks, embeddings)
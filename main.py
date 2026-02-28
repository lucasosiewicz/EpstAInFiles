from src.pipelines.ingestion_pipeline import IngestionPipeline

def main():
    ingestion_pipeline = IngestionPipeline()
    ingestion_pipeline.run()


if __name__ == "__main__":
    main()

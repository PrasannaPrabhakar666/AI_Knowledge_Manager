import os
from dotenv import load_dotenv
from storage_connectors import S3StorageConnector, LocalStorageConnector
from metadata_extractor import MetadataExtractor, NodeMetadataEncoder
from semantic_chunker import SemanticChunker
import json

def main():
    # Load environment variables
    load_dotenv()
    genai_user = os.getenv("USER_NAME")
    genai_pass = os.getenv("PASSWORD")
    ca_bundle_path = os.getenv("REQUESTS_CA_BUNDLE")

    if not all([genai_user, genai_pass, ca_bundle_path]):
        raise ValueError("Missing required environment variables.")

    # Initialize storage connectors
    local_connector = LocalStorageConnector()
    s3_connector = S3StorageConnector(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_key=os.getenv("AWS_SECRET_KEY"),
        bucket_name=os.getenv("S3_BUCKET_NAME")
    )

    # Initialize metadata extractor
    metadata_extractor = MetadataExtractor(genai_user, genai_pass, ca_bundle_path)

    # Initialize semantic chunker
    semantic_chunker = SemanticChunker(genai_user, genai_pass, ca_bundle_path)

    # Define input and output directories
    input_directory = "/path/to/input/directory"
    output_directory = "/path/to/output/directory"

    # Process files
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                
                # Extract metadata
                metadata = metadata_extractor.process_pdfs(os.path.dirname(file_path))
                
                # Save metadata
                metadata_output_path = os.path.join(output_directory, f"{file}_metadata.json")
                with open(metadata_output_path, 'w') as f:
                    json.dump(metadata, f, cls=NodeMetadataEncoder, indent=4)
                
                # Perform semantic chunking
                semantic_chunker.process_file(file_path, os.path.basename(root), output_directory)
                
                # Store results in S3 (if needed)
                s3_connector.connect()
                s3_connector.write(f"processed/{file}_metadata.json", json.dumps(metadata, cls=NodeMetadataEncoder))
                
                print(f"Processed {file}")

    print("All files processed successfully.")

if __name__ == "__main__":
    main()
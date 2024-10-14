# GenAI Knowledge Management Solution

This project provides a comprehensive GenAI knowledge management solution, allowing companies to connect to various storage systems, extract metadata from documents, and perform semantic chunking for improved information retrieval and analysis.

## Project Structure

The project consists of the following main components:

1. `storage_connectors.py`: Contains classes for connecting to various storage systems (Local, SQL, S3, SharePoint, Confluence).
2. `metadata_extractor.py`: Implements metadata extraction from PDF documents using OpenAI's GPT model.
3. `semantic_chunker.py`: Performs semantic chunking on text documents for improved information retrieval.
4. `main.py`: The main script that orchestrates the entire process.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/PrasannaPrabhakar666/AI_Knowledge_Manager.git
   cd genai-knowledge-management
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the necessary environment variables. Create a `.env` file in the project root with the following variables:
   ```
   GENAI_USER=your_genai_username
   GENAI_PASS=your_genai_password
   REQUESTS_CA_BUNDLE=/path/to/your/ca/bundle
   AWS_ACCESS_KEY=your_aws_access_key
   AWS_SECRET_KEY=your_aws_secret_key
   S3_BUCKET_NAME=your_s3_bucket_name
   ```

## Usage

1. Modify the `input_directory` and `output_directory` variables in `main.py` to point to your desired input and output locations.

2. Run the main script:
   ```
   python main.py
   ```

The script will process all PDF files in the input directory, extract metadata, perform semantic chunking, and store the results in the output directory and optionally in S3.

## Components

### Storage Connectors

The `storage_connectors.py` file provides classes for connecting to various storage systems:

- `LocalStorageConnector`: For local file system operations.
- `SQLStorageConnector`: For SQLite database operations.
- `S3StorageConnector`: For Amazon S3 operations.
- `SharePointConnector`: For Microsoft SharePoint operations.
- `ConfluenceConnector`: For Atlassian Confluence operations.

To use a specific connector, initialize it with the necessary credentials and use its `connect()`, `read()`, and `write()` methods.

### Metadata Extractor

The `metadata_extractor.py` file contains the `MetadataExtractor` class, which uses OpenAI's GPT model to extract metadata from PDF documents. The extracted metadata includes:

- Abstract
- Summary
- Top Questions
- Document Description
- Intent or Purpose
- Target Audience
- Tone/Style Guidelines
- Confidentiality or Access Level
- Usage Guidelines or Instructions
- Sensitive Data Indicators
- Contextual Relevance
- Bias Indicators
- Source Credibility
- AI-Generated Content Flag

### Semantic Chunker

The `semantic_chunker.py` file contains the `SemanticChunker` class, which performs the following operations:

1. Splits the input text into sentences.
2. Combines sentences with a sliding window approach.
3. Generates embeddings for the combined sentences.
4. Calculates cosine distances between adjacent embeddings.
5. Identifies breakpoints to create semantic chunks.
6. Generates visualizations of the chunking process.
7. Saves the chunks and embeddings for future use.

## Customization

You can easily extend this solution by:

1. Adding new storage connectors in `storage_connectors.py`.
2. Modifying the metadata extraction process in `metadata_extractor.py`.
3. Adjusting the semantic chunking parameters in `semantic_chunker.py`.
4. Adding new processing steps in `main.py`.


## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.

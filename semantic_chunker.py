import os
import httpx
import re
import numpy as np
import matplotlib.pyplot as plt
from langchain.openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

class SemanticChunker:
    def __init__(self, genai_user, genai_pass, ca_bundle_path):
        self.http_client = httpx.Client(verify=ca_bundle_path, headers={
            "GENAI_USER": genai_user,
            "GENAI_PASS": genai_pass
        })
        self.oaiembeds = OpenAIEmbeddings(model="text-embedding-ada-002", http_client=self.http_client)

    def process_file(self, file_path, folder_name, output_path):
        with open(file_path, 'r') as file:
            essay = file.read()
        
        print(f"Processing file: {file_path}")
        single_sentences_list = re.split(r'(?<=[.?!])\s+|\n+', essay)
        sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
        sentences = self.combine_sentences(sentences)
        print("Sentence combining done")

        embeddings = self.oaiembeds.embed_documents([x['combined_sentence'] for x in sentences])
        print("Embedding done")

        for i, sentence in enumerate(sentences):
            sentence['combined_sentence_embedding'] = embeddings[i]

        distances, sentences = self.calculate_cosine_distances(sentences)
        print("Cosine distances calculated")

        chunks = self.create_chunks(distances, sentences)
        print("Chunking done")

        self.save_graph(distances, chunks, folder_name, os.path.basename(file_path), output_path)
        self.save_markdown(chunks, folder_name, os.path.basename(file_path), output_path)
        self.save_embeddings(embeddings, folder_name, os.path.basename(file_path), output_path)

        print("Processing complete")
        return embeddings

    def combine_sentences(self, sentences, buffer_size=60):
        for i in range(len(sentences)):
            combined_sentence = ""
            for j in range(max(0, i-buffer_size), min(len(sentences), i+buffer_size+1)):
                combined_sentence += sentences[j]['sentence'] + " "
            sentences[i]['combined_sentence'] = combined_sentence.strip()
        return sentences

    def calculate_cosine_distances(self, sentences):
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i+1]['combined_sentence_embedding']
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            distance = 1 - similarity
            distances.append(distance)
            sentences[i]['distance_to_next'] = distance
        return distances, sentences

    def create_chunks(self, distances, sentences):
        breakpoint_percentile_threshold = 95
        breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)
        indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]
        
        chunks = []
        start_index = 0
        for end_index in indices_above_thresh + [len(sentences)]:
            chunk = " ".join([sentences[j]['sentence'] for j in range(start_index, end_index)])
            chunks.append(chunk)
            start_index = end_index
        
        return chunks

    def save_graph(self, distances, chunks, folder_name, file_name, output_path):
        plt.figure(figsize=(12, 6))
        plt.plot(distances)
        plt.ylim(0, 0.2)
        plt.xlim(0, len(distances))

        breakpoint_distance_threshold = np.percentile(distances, 95)
        plt.axhline(y=breakpoint_distance_threshold, color='r', linestyle='-')

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        start_index = 0
        for i, chunk in enumerate(chunks):
            end_index = start_index + len(chunk.split())
            plt.axvspan(start_index, end_index, facecolor=colors[i % len(colors)], alpha=0.25)
            plt.text(x=np.average([start_index, end_index]),
                     y=breakpoint_distance_threshold + 0.2/20,
                     s=f"Chunk #{i+1}",
                     horizontalalignment='center',
                     rotation="vertical")
            start_index = end_index

        plt.ylabel("Cosine distance between sequential sentences")
        plt.title(f"Essay Chunks Based On Embedding Breakpoints\n{folder_name}_{file_name}")
        plt.xlabel("Index of sentences in essay (Sentence Position)")

        graphs_dir = os.path.join(output_path, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        graph_output_path = os.path.join(graphs_dir, f"{folder_name}_{file_name}.png")
        plt.savefig(graph_output_path)
        plt.close()

    def save_markdown(self, chunks, folder_name, file_name, output_path):
        markdown_dir = os.path.join(output_path, 'markdown')
        os.makedirs(markdown_dir, exist_ok=True)
        markdown_output_path = os.path.join(markdown_dir, f"{folder_name}_{file_name}.md")
        with open(markdown_output_path, 'w') as md_file:
            for i, chunk in enumerate(chunks):
                md_file.write(f"## Chunk {i+1}\n")
                md_file.write(f"{chunk}\n\n")

    def save_embeddings(self, embeddings, folder_name, file_name, output_path):
        embeddings_dir = os.path.join(output_path, 'embeddings')
        os.makedirs(embeddings_dir, exist_ok=True)
        embeddings_output_path = os.path.join(embeddings_dir, f"{folder_name}_{file_name}_embeddings.npy")
        np.save(embeddings_output_path, embeddings)

    def process_directory(self, directory_path, output_path):
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith(".txt"):
                    folder_name = os.path.basename(root)
                    file_path = os.path.join(root, filename)
                    self.process_file(file_path, folder_name, output_path)
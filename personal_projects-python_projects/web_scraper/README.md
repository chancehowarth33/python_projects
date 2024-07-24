# Web Scraping Algorithims


GraphSearcher: Serving as the foundational class for various graph traversal techniques, GraphSearcher outlines the basic structure and methods for depth-first search (DFS) and breadth-first search (BFS) across a graph-like data structure. It's designed to be extended by subclasses, each implementing the visit_and_get_children method for different types of data sources. While it doesn't directly perform web scraping, its architecture is crucial for subclasses that might deal with web-based or other complex data structures, providing a flexible template for traversing and processing interconnected nodes.

MatrixSearcher: This class is designed to navigate through data structured as an adjacency matrix within a pandas DataFrame. It is not directly related to web scraping, but it could be used to analyze and traverse a graph-like structure, potentially representing web link connections or site architecture.

FileSearcher: This class focuses on reading and traversing through a file-based system, extracting linked data from files. While not inherently a web scraping tool, it could be utilized to process and navigate through locally saved web content or site map structures stored in files.

WebSearcher: Specifically tailored for web scraping, this class uses a Selenium WebDriver to navigate web pages. It extracts and compiles data from these pages, particularly focusing on scraping tables and following hyperlinks to traverse through connected web pages.


# MCP_EPO
This folder contains FastMCP client code for interacting with the EPO (European Patent Office) OPS API. The main functionality is implemented in the `main.py` file, which provides the following features:

1. **`search_patents`**: Used to search for published patents using EPO OPS CQL syntax. It supports fields like applicant (`pa`), title (`ti`), abstract (`ab`), publication date (`pd`), and more. It can retrieve results in a specified range.

2. **`get_biblio`**: Retrieves bibliographic information for a given patent, publication, or application number, including applicant, inventor, title, and other metadata.

3. **`get_abstract`**: Fetches the abstract text of a patent, publication, or application number, along with associated metadata.

4. **`get_full_cycle`**: Retrieves full-cycle data for a patent, including citations, search reports, and other related documents.

5. **`get_family`**: Provides INPADOC family information for a patent, including bibliographic and legal data across different patent offices.

6. **`get_legal`**: Gets legal status and event data for a patent, such as the current legal status and procedural steps.

7. **`convert_number`**: Converts patent numbers between different formats (e.g., `epodoc`, `docdb`, or `original`).

The script also includes a `main` block that runs the FastMCP server using the standard input/output transport (`stdio`), which can be used for testing or running the client interactively.

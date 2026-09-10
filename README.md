# Citation Network Explorer

Interactive exploration of academic citation networks using Dash and Neo4j.

Citation Network Explorer is a research-oriented dashboard for exploring relationships between articles, authors, and research fields. It combines graph queries with visual analysis to make citation structures easier to inspect.

## Features

- Search articles, authors, and research fields.
- Find shortest paths between articles or authors.
- Explore research-field evolution over time.
- Identify top graph communities.
- Analyze node centrality with graph algorithms.
- Inspect interactive graph visualizations.

## Project Structure

```text
.
├── app/
│   ├── app.py
│   ├── pages/
│   │   ├── field_evolution.py
│   │   ├── home.py
│   │   ├── node_centrality.py
│   │   ├── search.py
│   │   ├── shortest_path.py
│   │   └── top_communities.py
│   └── utils/
│       ├── common_layout.py
│       ├── data_preparation.py
│       ├── queries.py
│       └── stylesheet.py
├── data-processing/
│   └── data_processing.ipynb
├── database/
│   ├── constraints/
│   ├── standard-import/
│   └── bulk-import/
├── .gitignore
├── README.md
└── requirements.txt
```

## Technology Stack

- Python
- Dash
- Dash Cytoscape
- Neo4j
- Neo4j Graph Data Science
- NumPy, pandas, and ijson

## Getting Started

### Requirements

- Python 3.11 or later
- Neo4j Desktop 2
- A local Neo4j database with the Graph Data Science plugin
- The original publication dataset, available from [this JSON dataset link](ADD_JSON_DATASET_URL_HERE)

### Install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Set up Neo4j Desktop

1. Create a local database in Neo4j Desktop 2 using a Neo4j 5.x version compatible with Graph Data Science.
2. Set the database credentials to match the current application configuration:

	```text
	Username: neo4j
	Password: CitationGraph123
	```

3. Configure the Bolt connection to use port `7687`.
4. Install the `Graph Data Science` plugin from the database's Plugins section.
5. Start the database and verify it in Neo4j Browser:

	```cypher
	RETURN 1;
	RETURN gds.version();
	```

### Prepare the data

The `data-processing/data_processing.ipynb` notebook transforms the original JSON dataset into the CSV files required by Neo4j. Place the downloaded JSON file where the notebook expects it, then run the notebook with the project's `.venv` kernel.

The generated files are:

```text
articles.csv
autors.csv
fieldOfStudy.csv
articles_autors.csv
articles_articles.csv
articles_fieldOfStudy.csv
```

The original JSON dataset and generated CSV files are not intended to be committed to Git. Keep them in the local `data/` directory.

### Copy CSV files to Neo4j

Copy the six generated CSV files into the `import` directory of the Neo4j Desktop database. The database scripts use `file:///...` paths, so Neo4j must be able to find the files there:

```text
<neo4j-database-folder>/import/
├── articles.csv
├── autors.csv
├── fieldOfStudy.csv
├── articles_autors.csv
├── articles_articles.csv
└── articles_fieldOfStudy.csv
```

### Import the graph

Run the three scripts in `database/constraints/` first. Then choose one import workflow:

- `database/standard-import/` for a normal-sized dataset.
- `database/bulk-import/` for a large dataset; these scripts use transactions optimized for larger imports.

Run the node imports before the relationship imports. Do not run both workflows on the same database unless you have reset the database first.

You can verify the imported graph in Neo4j Browser:

```cypher
MATCH (n)
RETURN labels(n), count(n);

MATCH ()-[r]->()
RETURN type(r), count(r);
```

### Run the dashboard

With Neo4j Desktop still running, activate the virtual environment and start the Dash application:

```powershell
.venv\Scripts\activate
cd app
python app.py
```

The dashboard will be available at `http://127.0.0.1:8050/`.

## Database Scripts

The `database/` directory contains the Cypher scripts used to prepare and populate the Neo4j database.

### Script groups

- `database/constraints/` creates the uniqueness constraints required by the graph model.
- `database/standard-import/` imports the data using regular `LOAD CSV` operations.
- `database/bulk-import/` contains transaction-based scripts optimized for larger datasets.

## Application Pages

| Page | Route |
| --- | --- |
| Search | `/search` |
| Shortest Path | `/shortest-path` |
| Top Communities | `/top-communities` |
| Node Centrality | `/node-centrality` |
| Research Field Evolution | `/field-evolution` |

## Scope

This project was developed as a final-year project focused on graph-based analysis of academic citations. The repository contains the dashboard, data preparation notebook, and database import resources required to understand the project workflow.

## Author

Gerard

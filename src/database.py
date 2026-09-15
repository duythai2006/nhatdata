import duckdb
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "research.duckdb"

def get_connection():
    return duckdb.connect(str(DB_PATH))

def init_database():
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker VARCHAR PRIMARY KEY,
            company_name VARCHAR,
            exchange VARCHAR,
            industry VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS financial_data (
            id BIGINT,
            ticker VARCHAR,
            period VARCHAR,
            metric VARCHAR,
            value DOUBLE,
            unit VARCHAR,
            source VARCHAR,
            source_url VARCHAR,
            source_page VARCHAR,
            confidence VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id BIGINT,
            ticker VARCHAR,
            title VARCHAR,
            source_type VARCHAR,
            url VARCHAR,
            publication_date VARCHAR,
            reliability VARCHAR,
            notes VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS theses (
            id BIGINT,
            ticker VARCHAR,
            thesis TEXT,
            evidence TEXT,
            counter_argument TEXT,
            valuation_link TEXT,
            score DOUBLE,
            status VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized.")

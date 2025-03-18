import sqlite3
import os

from pydantic import BaseModel

from dotenv import load_dotenv
from typing import Optional

load_dotenv()

CF_ACCOUNTID=os.getenv("CF_ACCOUNTID")
CF_ZONEID=os.getenv("CF_ZONEID")
DB_LOCATION=f"{os.getcwd()}/dumped_db"

class WebAnalytics(BaseModel):
    domain_name: str
    date: str
    page_views: float
    visits: float

class Overview(BaseModel):
    zone_id: str
    date: str
    bytes: float
    cached_bytes: float
    cached_requests: float
    page_views: float
    requests: float
    threats: float

class CountryOverview(BaseModel):
    zone_id: str
    date: str
    code: str
    data_bytes: float
    requests: float
    threats: float

DBFILE = f"{DB_LOCATION}/{CF_ACCOUNTID}.db"

def initialize_db():
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_analytics (
        domain_name TEXT NOT NULL,
        date TEXT NOT NULL,
        page_views REAL,
        visits REAL,
        PRIMARY KEY (domain_name, date)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS overview (
        zone_id TEXT NOT NULL,
        date TEXT NOT NULL,
        bytes REAL,
        cached_bytes REAL,
        cached_requests REAL,
        page_views REAL,
        requests REAL,
        threats REAL,
        PRIMARY KEY (zone_id, date)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS country_overview (
        zone_id TEXT NOT NULL,
        date TEXT NOT NULL,
        code TEXT,
        bytes REAL,
        requests REAL,
        threats REAL,
        PRIMARY KEY (zone_id, date)
    );
    """)

    conn.commit()
    conn.close()

def insertWebAnalytics(data: WebAnalytics) -> bool:
    try:
        conn = sqlite3.connect(DBFILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO web_analytics (domain_name, date, page_views, visits)
            VALUES(?, ?, ?, ?)
        """, (data.domain_name, data.date, data.page_views, data.visits))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting web_analytics {e}")
        return False
    return False

def getDomainData(domainName: str, tableName: str):
    try:
        conn = sqlite3.connect(DBFILE)
        cursor = conn.cursor()
        query = f"SELECT date, page_views, visits from {tableName} where domain_name='{domainName}'"
        cursor.execute(query)
        conn.commit()
        result = cursor.fetchall()
        conn.close()

        return result

    except Exception as e:
        print(f"Error fetching {domainName} from {tableName}")
        return None
    return None

def getDomainDate(domainName: str, date: str, tableName: str):
    try:
        conn = sqlite3.connect(DBFILE)
        cursor = conn.cursor()
        query = f"SELECT domain_name, date from {tableName} where domain_name='{domainName}' and date='{date}'"
        cursor.execute(query)
        conn.commit()
        result = cursor.fetchone()
        conn.close()

        return result

    except Exception as e:
        print(f"Error fetching {domainName} from {tableName}")
        return None
    return None

def getDateRange(tableName: str):
    try:
        conn = sqlite3.connect(DBFILE)
        cursor = conn.cursor()
        query = f"SELECT MIN(date), MAX(date) from {tableName}"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        if len(result) >0:
            if result[0] is not None and result[1] is not None:
                return result[0], result[1] 
            else:
                return 0,0
        else:
            return 0,0

        return 0, 0
    except Exception as e:
        print(f"Error fetching newest and oldest date from {tableName} : {e}")
        return None, None

def getSecondNewestDate(tableName: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        query = f"SELECT DISTINCT date FROM {table_name}  ORDER BY date DESC LIMIT 2"
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()

        if len(result) == 2:
            return result[1][0]  # Return the second newest date
        return None
    except Exception as e:
        print(f"Error fetching second newest date from {table_name}: {e}")
        return None

initialize_db()

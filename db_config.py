import os
import sys
import tempfile
import urllib.parse

try:
    import pyodbc
except ImportError:
    pyodbc = None

# Server có thể cấu hình qua biến môi trường MSSQL_SERVER
DEFAULT_SERVER = os.environ.get("MSSQL_SERVER", "localhost")
DEFAULT_USER = os.environ.get("MSSQL_USER", None)
DEFAULT_PASSWORD = os.environ.get("MSSQL_PASSWORD", None)


def get_available_driver():
    """Tự động tìm ODBC driver SQL Server thích hợp nhất đã cài trên máy."""
    if pyodbc is None:
        return None
    env_driver = os.environ.get("MSSQL_DRIVER")
    if env_driver:
        return env_driver
    try:
        installed = pyodbc.drivers()
    except Exception:
        return None
    preferred = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server Native Client RDA 11.0",
        "SQL Server",
    ]
    for d in preferred:
        if d in installed:
            return d
    return "ODBC Driver 17 for SQL Server"


def get_connection_parts(db_name="master"):
    """Tạo chuỗi ODBC connection parameters."""
    driver = get_available_driver()
    server = DEFAULT_SERVER

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={db_name}",
    ]

    if DEFAULT_USER and DEFAULT_PASSWORD:
        parts.append(f"UID={DEFAULT_USER}")
        parts.append(f"PWD={DEFAULT_PASSWORD}")
    else:
        parts.append("Trusted_Connection=yes")

    parts.append("TrustServerCertificate=yes")

    return ";".join(parts) + ";"


def get_mssql_uri(db_name="BookNest_Ch08"):
    """Trả về SQLAlchemy Database URI cho SQL Server qua pyodbc."""
    odbc_str = get_connection_parts(db_name)
    params = urllib.parse.quote_plus(odbc_str)
    return f"mssql+pyodbc:///?odbc_connect={params}"


def get_database_uri(db_name="BookNest_Ch08"):
    """
    Tự động xác định Database URI tối ưu:
    1. Nếu có DATABASE_URL (Cloud PostgreSQL / Neon / Supabase): sử dụng.
    2. Nếu đang chạy trên Vercel (os.environ.get('VERCEL')) hoặc không có pyodbc: dùng SQLite.
    3. Mặc định trên môi trường local Windows có SQL Server: kết nối SQL Server qua pyodbc.
    """
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # Nếu đang ở môi trường Cloud Serverless Vercel hoặc không có pyodbc
    is_vercel = os.environ.get("VERCEL") is not None
    if is_vercel or pyodbc is None:
        # Trên Vercel thư mục /tmp được phép ghi
        db_path = os.path.join(tempfile.gettempdir(), "cinenest.db")
        return f"sqlite:///{db_path}"

    # Môi trường local: ưu tiên SQL Server
    try:
        driver = get_available_driver()
        if driver:
            return get_mssql_uri(db_name)
    except Exception:
        pass

    # Fallback an toàn về SQLite nếu SQL Server không khả dụng
    db_path = os.path.join(tempfile.gettempdir(), "cinenest.db")
    return f"sqlite:///{db_path}"


def reset_database(db_name="BookNest_Ch08"):
    """Xóa và tạo lại database trắng tinh trên SQL Server (nếu dùng SQL Server)."""
    if pyodbc is None:
        return
    odbc_master = get_connection_parts("master")
    conn = pyodbc.connect(odbc_master, autocommit=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sys.databases WHERE name = ?", (db_name,))
        if cur.fetchone():
            cur.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            cur.execute(f"DROP DATABASE [{db_name}]")
        cur.execute(f"CREATE DATABASE [{db_name}]")
        print(f"[SQL Server] Da tao moi hoan toan database: {db_name}")
    finally:
        conn.close()


def ensure_database_exists(db_name="BookNest_Ch08"):
    """Tự động tạo database trên SQL Server nếu chưa tồn tại."""
    if pyodbc is None:
        return
    odbc_master = get_connection_parts("master")
    try:
        conn = pyodbc.connect(odbc_master, autocommit=True)
    except Exception as e:
        fallback_servers = [".", "localhost\\SQLEXPRESS", "localhost\\TAMSQL", "127.0.0.1"]
        conn = None
        driver = get_available_driver()
        for srv in fallback_servers:
            try:
                test_parts = [
                    f"DRIVER={{{driver}}}",
                    f"SERVER={srv}",
                    "DATABASE=master",
                    "Trusted_Connection=yes",
                    "TrustServerCertificate=yes;",
                ]
                conn = pyodbc.connect(";".join(test_parts), autocommit=True)
                global DEFAULT_SERVER
                DEFAULT_SERVER = srv
                break
            except Exception:
                continue
        if conn is None:
            raise ConnectionError(
                f"Không thể kết nối tới SQL Server ({DEFAULT_SERVER}). Lỗi: {e}\n"
                "Vui lòng đảm bảo SQL Server service đang chạy và tên Server hợp lệ."
            )

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM sys.databases WHERE name = ?", (db_name,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE [{db_name}]")
            print(f"[SQL Server] Da tao database: {db_name}")
        else:
            print(f"[SQL Server] Database da ton tai: {db_name}")
    finally:
        conn.close()

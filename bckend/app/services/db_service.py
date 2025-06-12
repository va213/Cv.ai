import psycopg2
from config import DB_CONFIG
from ..log_config import setup_logger


def insert_to_db(data):
    logger=setup_logger()

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO cv_data (
            name, email, phone, location, education, skills,
            experience_years, current_company, expected_salary,
            notice_period, portfolio_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data.get("Name", ""),
        data.get("Email", ""),
        data.get("Phone", ""),
        data.get("Location"),
        data.get("Education"),
        data.get("Skills"),
        data.get("Experience Years"),
        data.get("Current Company"),
        data.get("Expected Salary"),
        data.get("Notice Period"),
        data.get("Portfolio Link")
    )
    logger.info(f"insert values: {values}")

    cursor.execute(insert_query, values)
    conn.commit()
    cursor.close()
    conn.close()

def get_all_cv_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone, location, education, skills, experience_years, current_company, portfolio_link FROM cv_data")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
import mysql.connector  
  
  
def get_database_connection():  
    return mysql.connector.connect(  
        host="localhost",  
        user="root",  # Replace with your MySQL username  
        password="1234",  # Replace with your MySQL password  
        database="news_db"  # Replace with your database name  
    )  
  

def save_to_database(news_data):  
    conn = get_database_connection()  
    cursor = conn.cursor()  
      
    for heading, details in news_data:  
        cursor.execute(  
            "INSERT INTO news (news_heading, news_details) VALUES (%s, %s)",  
            (heading, details)  
        )  
      
    conn.commit()  
    cursor.close()  
    conn.close()  
    
def fetch_all_news():  
    conn = get_database_connection()  
    cursor = conn.cursor()  
    cursor.execute("SELECT * FROM news")  
    results = cursor.fetchall()  
    cursor.close()  
    conn.close()  
    return results  
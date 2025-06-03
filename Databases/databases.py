import sqlite3
def load_data():
    conn = sqlite3.connect("catch_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catches (    
            user_id TEXT,
            catch_name TEXT,
            catch_id TEXT,
            catch_atk TEXT,
            catch_hp TEXT,
            catch_time TEXT,
            favorite BOOLEAN DEFAULT FALSE,
            past_owner TEXT DFAULT NULL
        )
    ''')
    conn.commit()
    conn2 = sqlite3.connect('ball_data.db')
    cursor2 = conn2.cursor()
    cursor2.execute('''
        CREATE TABLE IF NOT EXISTS ball_data (
            ball_name TEXT PRIMARY KEY,
            emoji_id TEXT,
            base_atk TEXT,
            base_hp TEXT,
            ball_ability TEXT,
            ball_description TEXT,  
            ball_rarity TEXT        
        )
    ''')
    conn2.commit()
    conn3 = sqlite3.connect('user_data.db')
    cursor3 = conn3.cursor()
    cursor3.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT,
            ball_name TEXT        
        )
    ''')
    conn3.commit()
    return cursor, cursor2, cursor3, conn, conn2, conn3

load_data()
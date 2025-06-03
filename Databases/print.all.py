import sqlite3

# Connect to the database
conn = sqlite3.connect('ball_data.db')
c = conn.cursor()

def print_all_balls():
    # Retrieve all data from the ball_data table
    c.execute('SELECT * FROM ball_data')
    rows = c.fetchall()
    
    if rows:
        print("\nBall Data in Database:")
        for row in rows:
            print(f"Name: {row[0]}, Emoji ID: {row[1]}, ATK: {row[2]}, HP: {row[3]}, Ability: {row[4]}, Description: {row[5]}, Rarity: {row[6]}")
    else:
        print("No balls found in the database.")

# Call the function to print all data
print_all_balls()

# Close the database connection
conn.close()
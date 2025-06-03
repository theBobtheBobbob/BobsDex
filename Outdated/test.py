import sqlite3

# Connect to the database
conn = sqlite3.connect('ball_data.db')
c = conn.cursor()

def update_ball_name():
    old_name = input("Enter the current ball name to update: ")
    new_name = input("Enter the new ball name: ")
    
    # Check if the old ball name exists in the database
    c.execute('SELECT * FROM ball_data WHERE ball_name = ?', (old_name,))
    row = c.fetchone()
    
    if row:
        # Update the ball name for the specified entry
        c.execute('UPDATE ball_data SET ball_name = ? WHERE ball_name = ?', (new_name, old_name))
        conn.commit()
        print(f"Ball name has been updated from '{old_name}' to '{new_name}'.")
    else:
        print(f"Error: Ball with name '{old_name}' not found in the database.")

# Run the function to update the ball name
update_ball_name()

# Close the database connection
conn.close()
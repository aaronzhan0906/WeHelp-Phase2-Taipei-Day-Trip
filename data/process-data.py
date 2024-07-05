import json
from database import get_cursor, conn_commit
from mysql.connector import Error

with open("taipei-attractions.json", "r", encoding="utf-8") as file:
    data = json.load(file)


cursor, conn = get_cursor()

# deal with json data 
for item in data["result"]["results"]:
    name = item["name"]
    category = item["CAT"]
    description = item["description"]
    address = item["address"]
    transport = item["direction"]
    mrt = item["MRT"]
    latitude = item["latitude"]
    longitude = item["longitude"]
    
    # image
    images_str = item["file"]
    images_list = images_str.split("https://")
    filtered_images = ["https://" + image for image in images_list if image.lower().endswith(('.jpg', '.png'))]
    images = json.dumps("\n".join(filtered_images))
    
    insert_mySQL = """
    INSERT INTO attractions (name, category, description, address, transport, mrt, latitude, longitude, images) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(insert_mySQL, (name, category, description, address, transport, mrt, latitude, longitude, images))
    except Error as err:
        print(f"Error: {err}")

    finally:
        conn_commit(conn)
        

print("Data had been inserted")


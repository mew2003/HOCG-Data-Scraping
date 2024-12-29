import requests
import csv
import shutil
from bs4 import BeautifulSoup

# File names
file_name = "output.html"
csv_file_name = "output.csv"
edit_file = "edit_this_file.csv"
association_file = "hololive-association.csv"

# Get Web data
def get_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Write HTML file on computer
def write_data(data):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(str(data))

# Read card associations from file
def read_associations(file_path):
    card_associations = {}
    
    with open(file_path, mode='r', encoding='utf-8') as associations_file:
        reader = csv.reader(associations_file, delimiter=';')
        next(reader)  # Skip header
        for row in reader:
            card_associations[row[0].lower()] = (row[1], row[2])  # Use lowercase for comparison

    return card_associations

# Extract and process card data
def process_cards(soup, associations):
    cards_data = []
    groups = soup.find_all("div", id="card-list3")

    for group in groups:
        rarity = group.find("h3", recursive=False).find("span", recursive=False).text.strip()
        cards_by_rarity = group.find_all("div", class_="card-product")

        for card in cards_by_rarity:
            card_id = card.find("span", recursive=False).text.strip()
            card_name = card.find("h4").text.strip()
            card_price = int(card.find("strong").text.strip().replace("円", "").replace(",", ""))
            card_url = card.find("a")["href"]
            card_group, oshi_name = 'Unknown', 'None'

            # Match association
            for association_name, (group_name, extra_info) in associations.items():
                if association_name in card_name.lower():
                    card_group, oshi_name = group_name, extra_info
                    break

            cards_data.append([rarity, card_id, card_name, oshi_name, card_group, card_url, card_price, 0])

    return cards_data

# Write data to CSV file
def write_csv(cards_data, file_path):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_file.write('\ufeff')  # BOM for UTF-8 encoding
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['Rarity', 'ID', 'Card Name', 'Oshi Name', 'Association', 'URL', 'Price', 'Possessed'])
            writer.writerows(cards_data)
    except IOError as e:
        print(f"Error writing CSV file: {e}")

# Main execution steps
def main():
    url = "https://yuyu-tei.jp/sell/hocg/s/search?search_word=&rare=&type=&kizu=0"
    
    # Step 1: Get data from website and save HTML
    soup = get_data(url)
    if soup:
        write_data(soup)
    
        # Step 2: Manipulate data
        associations = read_associations(association_file)
        cards_data = process_cards(soup, associations)
        write_csv(cards_data, csv_file_name)
        
        # Step 3: Copy to editable file
        shutil.copy(csv_file_name, edit_file)

# Run the main function
if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

def scrape_liturgia_diaria():
    """
    Scrapes daily Catholic readings from Liturgia Canção Nova website.
    Extracts first reading, psalm, and gospel.
    Saves data to CSV file in output/ directory.
    """
    
    # Configuration
    base_url = "https://liturgia.cancaonova.com/pb/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    print(f"🔎 Fetching daily readings from {base_url}...")
    
    try:
        # Make HTTP request
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        print(f"✅ Connection successful! Status Code: {response.status_code}")
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Prepare data list
        readings_data = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract First Reading
        primeira_leitura_div = soup.find("div", id="liturgia-1")
        if primeira_leitura_div:
            titulo = primeira_leitura_div.find("p", text=lambda t: t and "Primeira Leitura" in t)
            texto_paragraphs = primeira_leitura_div.find_all("p")[1:]
            
            if titulo and texto_paragraphs:
                texto = " ".join([p.text.strip() for p in texto_paragraphs])
                readings_data.append({
                    "Date": current_date,
                    "Type": "Primeira Leitura",
                    "Title": titulo.text.strip(),
                    "Text": texto
                })
                print("✅ First reading extracted")
        
        # Extract Psalm
        salmo_div = soup.find("div", id="liturgia-2")
        if salmo_div:
            titulo = salmo_div.find("p", text=lambda t: t and "Responsório" in t)
            texto_paragraphs = salmo_div.find_all("p")[1:]
            
            if titulo and texto_paragraphs:
                texto = " ".join([p.text.strip() for p in texto_paragraphs])
                readings_data.append({
                    "Date": current_date,
                    "Type": "Salmo Responsorial",
                    "Title": titulo.text.strip(),
                    "Text": texto
                })
                print("✅ Psalm extracted")
        
        # Extract Gospel
        evangelho_div = soup.find("div", id="liturgia-4")
        if evangelho_div:
            titulo = evangelho_div.find("p", text=lambda t: t and "Evangelho" in t)
            texto_paragraphs = evangelho_div.find_all("p")[1:]
            
            if titulo and texto_paragraphs:
                texto = " ".join([p.text.strip() for p in texto_paragraphs])
                readings_data.append({
                    "Date": current_date,
                    "Type": "Evangelho",
                    "Title": titulo.text.strip(),
                    "Text": texto
                })
                print("✅ Gospel extracted")
        
        # Save to CSV file
        if readings_data:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Define CSV file path
            csv_file = "output/daily_liturgy.csv"
            
            # Write to CSV
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                fieldnames = ["Date", "Type", "Title", "Text"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(readings_data)
            
            print(f"✅ Daily readings saved successfully to {csv_file}")
            print(f"📊 Total readings extracted: {len(readings_data)}")
            
        else:
            print("❌ No readings found.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    scrape_liturgia_diaria()
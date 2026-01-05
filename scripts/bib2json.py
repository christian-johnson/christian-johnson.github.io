import bibtexparser
import json
import os

def main():
    input_path = os.path.join('assets', 'bib', 'papers.bib')
    output_path = os.path.join('data', 'publications.json')
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Reading {input_path} using bibtexparser...")
    try:
        with open(input_path, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        
        entries = bib_database.entries
        print(f"Found {len(entries)} entries.")
        
        for entry in entries:
            entry['key'] = entry.get('ID')
            for field in entry:
                if isinstance(entry[field], str):
                    # Remove all curly braces used for LaTeX escaping
                    entry[field] = entry[field].replace('{', '').replace('}', '')
                    # Unescape common LaTeX characters
                    entry[field] = entry[field].replace('\\&', '&').replace('\\%', '%')
            
            if 'author' in entry:
                # Split by ' and ' to get individual authors
                authors = entry['author'].split(' and ')
                # Clean up each author
                cleaned_authors = []
                for a in authors:
                    a = a.replace('{', '').replace('}', '').strip()
                    cleaned_authors.append(a)
                entry['author_list'] = cleaned_authors
                # Keep 'author' as string for backward compatibility or simple use
                entry['author'] = ", ".join(cleaned_authors)
        
        # Group by year
        grouped_entries = {}
        for entry in entries:
            year = entry.get('year', 'Unknown')
            if year not in grouped_entries:
                grouped_entries[year] = []
            grouped_entries[year].append(entry)
        
        # Sort years descending
        sorted_years = sorted(grouped_entries.keys(), reverse=True)
        final_data = []
        for year in sorted_years:
            # Sort entries within each year by month if possible, but for now just keep order
            final_data.append({
                "year": year,
                "items": grouped_entries[year]
            })
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)
            
        print(f"Successfully wrote to {output_path}")
        
    except Exception as e:
        print(f"Error parsing BibTeX: {e}")

if __name__ == "__main__":
    main()

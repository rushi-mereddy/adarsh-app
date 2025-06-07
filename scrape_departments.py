import requests
from bs4 import BeautifulSoup
import json

def scrape_adarsh_departments():
    """Scrape departments from Adarsh website"""
    url = "https://adarsh.ac.in/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for department sections
        departments = []
        
        # Find all course/department items
        course_items = soup.find_all('div', class_='course-item')
        
        for item in course_items:
            try:
                # Extract title
                title_elem = item.find('h5')
                if title_elem:
                    title = title_elem.get_text().strip()
                    
                    # Extract image
                    img_elem = item.find('img')
                    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
                    
                    # Extract program type from tag
                    tag_elem = item.find('div', class_='course-tag')
                    program_type = 'UG'  # default
                    if tag_elem:
                        tag_text = tag_elem.get_text().strip()
                        if 'Post Graduation' in tag_text or 'M.Tech' in tag_text:
                            program_type = 'PG'
                        elif 'Under Graduation' in tag_text or 'B.Tech' in tag_text:
                            program_type = 'UG'
                    
                    # Generate department code
                    code = generate_dept_code(title)
                    
                    departments.append({
                        'name': title,
                        'code': code,
                        'program': program_type,
                        'image_url': image_url,
                        'description': f"Comprehensive {program_type} program in {title.replace('(', '').replace(')', '')}"
                    })
                    
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
                
        return departments
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def generate_dept_code(name):
    """Generate department code from name"""
    # Remove common words and extract key parts
    name = name.upper()
    
    # Specific mappings
    code_mappings = {
        'COMPUTER SCIENCE': 'CSE',
        'ARTIFICIAL INTELLIGENCE & MACHINE LEARNING': 'AIML',
        'ARTIFICIAL INTELLIGENCE & DATA SCIENCE': 'AIDS',
        'ELECTRONICS AND COMMUNICATION': 'ECE',
        'ELECTRICAL AND ELECTRONICS': 'EEE',
        'MECHANICAL ENGINEERING': 'MECH',
        'CIVIL ENGINEERING': 'CIVIL',
        'BACHELOR OF BUSINESS ADMINISTRATION': 'BBA',
        'BACHELOR OF COMPUTER APPLICATIONS': 'BCA',
        'THERMAL ENGINEERING': 'MT_THERM',
        'INFORMATION TECHNOLOGY': 'IT',
        'AERONAUTICAL': 'AERO',
        'AUTOMOBILE': 'AUTO'
    }
    
    for key, code in code_mappings.items():
        if key in name:
            if 'M.TECH' in name or 'POST GRADUATION' in name:
                return f"MT_{code}" if not code.startswith('MT_') else code
            return code
    
    # Fallback: first letters of major words
    words = [w for w in name.split() if len(w) > 2 and w not in ['AND', 'THE', 'OF', 'IN']]
    return ''.join([w[0] for w in words[:3]])[:10]

if __name__ == "__main__":
    departments = scrape_adarsh_departments()
    print(json.dumps(departments, indent=2))
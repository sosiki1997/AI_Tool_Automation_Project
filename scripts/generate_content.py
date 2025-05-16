import os
import json
import logging
import sqlite3
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.db_path = "data/tools.db"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def enhance_tool_descriptions(self):
        """Enhance tool descriptions using AI"""
        tools = self._get_tools_from_db()
        enhanced_tools = []
        
        for tool in tools:
            try:
                enhanced_info = self._generate_enhanced_content(tool)
                enhanced_tools.append(enhanced_info)
                self._update_tool_in_db(tool['name'], enhanced_info)
                logging.info(f"Enhanced description for: {tool['name']}")
            except Exception as e:
                logging.error(f"Error enhancing tool {tool['name']}: {str(e)}")
                
        return enhanced_tools
    
    def _get_tools_from_db(self):
        """Get tools from database that haven't been enhanced"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT name, description, url, source, discovered_date
            FROM tools
            WHERE enhanced_description IS NULL
            ORDER BY discovered_date DESC
        ''')
        
        tools = []
        for row in c.fetchall():
            tools.append({
                'name': row[0],
                'description': row[1],
                'url': row[2],
                'source': row[3],
                'discovered_date': row[4]
            })
            
        conn.close()
        return tools
    
    def _generate_enhanced_content(self, tool):
        """Generate enhanced content using DeepSeek API"""
        prompt = f"""
        Please analyze this AI tool and provide enhanced information:
        
        Name: {tool['name']}
        Current Description: {tool['description']}
        URL: {tool['url']}
        
        Please provide:
        1. A more detailed description
        2. Key features and capabilities
        3. Best use cases
        4. Potential limitations
        5. Related tools or alternatives
        
        Format the response as a JSON object with these fields:
        - enhanced_description
        - key_features
        - use_cases
        - limitations
        - alternatives
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an AI tool analyst. Provide detailed, accurate information about AI tools."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        
        try:
            enhanced_info = json.loads(response.json()['choices'][0]['message']['content'])
            return {
                **tool,
                **enhanced_info
            }
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse AI response for {tool['name']}: {str(e)}")
            return tool
    
    def _update_tool_in_db(self, tool_name, enhanced_info):
        """Update tool information in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            ALTER TABLE tools ADD COLUMN IF NOT EXISTS enhanced_description TEXT
        ''')
        
        c.execute('''
            UPDATE tools
            SET enhanced_description = ?
            WHERE name = ?
        ''', (json.dumps(enhanced_info), tool_name))
        
        conn.commit()
        conn.close()

def main():
    generator = ContentGenerator()
    enhanced_tools = generator.enhance_tool_descriptions()
    print(f"Enhanced {len(enhanced_tools)} tools")

if __name__ == "__main__":
    main() 
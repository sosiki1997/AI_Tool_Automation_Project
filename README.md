# AI Tools Automation Project

This project automatically collects AI tool information from various sources, generates engaging content, and pushes it to a Notion database.

## Features

- Automated data collection from Product Hunt and GitHub
- AI-powered content generation using GPT-3.5
- Automatic Notion integration
- Daily scheduled updates
- Comprehensive logging

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Tool_Automation_Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
```

4. Configure settings:
Edit `config/settings.py` to update:
- Notion database ID
- Email address
- Other configuration options

## Usage

Run the automation script:
```bash
python run_automation.py
```

The script will:
1. Run immediately on startup
2. Schedule daily runs at 9:00 AM
3. Collect AI tool information
4. Generate content and image prompts
5. Push to your Notion database

## Project Structure

```
/AI_Tool_Automation_Project
│
├── /scripts
│   ├── data_collection.py       # Data collection script
│   ├── generate_content.py      # Content generation script
│   └── push_to_notion.py        # Notion integration script
│
├── /config
│   ├── settings.py              # Configuration settings
│
├── /logs
│   └── automation_log.txt       # Log file
│
├── run_automation.py            # Main automation script
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## Logging

Logs are stored in `logs/automation_log.txt` and include:
- Data collection status
- Content generation results
- Notion integration status
- Any errors or exceptions

## Contributing

Feel free to submit issues and enhancement requests! 
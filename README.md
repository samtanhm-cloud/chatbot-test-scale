# 🎭 Streamlit MDC Automation Executor

A web application that allows users to execute MDC (Model Context) automation files with Playwright MCP through natural language prompts, similar to the Cursor AI experience.

## 🌟 Features

- **Natural Language Interface**: Enter prompts in plain English to trigger automations
- **Intelligent Matching**: Uses Claude AI to match prompts to appropriate MDC files
- **Playwright MCP Integration**: Full browser automation capabilities
- **Real-time Execution**: See results as your automations run
- **Execution History**: Track all your automation runs
- **Beautiful UI**: Modern, responsive interface built with Streamlit

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** installed
- **Anthropic API Key** (for AI-powered prompt matching)
- Your **MDC automation files**

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd streamlit_mdc_app

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Install Playwright MCP Server
npx -y @executeautomation/playwright-mcp-server
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 3. Add Your MDC Files

Place your MDC automation files in the project directory or a subdirectory. The app will automatically detect them.

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📝 MDC File Format

Your MDC files should contain Playwright MCP commands in the following format:

```markdown
# Link Validation Automation

This automation validates links on a webpage.

```mcp
{
  "tool": "browser_navigate",
  "params": { "url": "https://example.com" }
}
```

```mcp
{
  "tool": "browser_snapshot",
  "params": {}
}
```

```mcp
{
  "tool": "browser_click",
  "params": { 
    "element": "Check Links button",
    "ref": "#check-links"
  }
}
```
```

## 🔧 Usage

### Basic Workflow

1. **Enter a Prompt**: Type what you want to automate in natural language
   - Example: "Validate all links on the German documentation page"

2. **Execute or Analyze**: 
   - Click "Execute" to run the automation
   - Click "Analyze Only" to see which MDC file would be used

3. **View Results**: See the execution output and any errors

4. **Check History**: Review past executions in the sidebar

### Example Prompts

- "Validate email links in Draftr content"
- "Check AEM page for broken links"
- "Validate localization links for Japanese content"
- "Extract and validate links from TermWeb"

## 🌐 Deploying to Streamlit Community Cloud

### Step 1: Prepare Your Repository

1. Create a GitHub repository for your app
2. Push your code:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### Step 2: Deploy on Streamlit

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set the main file path: `streamlit_mdc_app/app.py`
5. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud, go to your app settings and add secrets:

```toml
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxx"
```

### Step 4: Install System Dependencies

Create a `packages.txt` file in your repository root:

```txt
nodejs
npm
```

This ensures Node.js is available for running the MCP executor.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Web Interface           │
│   (app.py)                          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Prompt Processor                  │
│   (Uses Claude API)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   MDC Executor                      │
│   (Python wrapper)                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Node.js MDC Executor              │
│   (mdc_executor.js)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Playwright MCP Server             │
│   (Browser Automation)              │
└─────────────────────────────────────┘
```

## 🔐 Security Considerations

### For Production Deployment:

1. **API Keys**: Never commit API keys to your repository
   - Use Streamlit secrets management
   - Use environment variables

2. **Rate Limiting**: Implement rate limiting for API calls
   ```python
   # Add to app.py
   import time
   from functools import wraps
   
   def rate_limit(seconds=1):
       def decorator(func):
           last_called = [0]
           @wraps(func)
           def wrapper(*args, **kwargs):
               elapsed = time.time() - last_called[0]
               if elapsed < seconds:
                   time.sleep(seconds - elapsed)
               result = func(*args, **kwargs)
               last_called[0] = time.time()
               return result
           return wrapper
       return decorator
   ```

3. **Input Validation**: Sanitize all user inputs
4. **Execution Timeouts**: Prevent long-running processes
5. **Resource Limits**: Monitor CPU and memory usage

## 📊 Monitoring and Logging

Enable logging in your Streamlit app:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## 🐛 Troubleshooting

### Issue: MDC files not detected

**Solution**: Ensure your MDC files have the `.mdc` extension and are in the configured directory.

### Issue: MCP server fails to start

**Solution**: 
```bash
# Verify Node.js installation
node --version

# Reinstall Playwright MCP
npm install @executeautomation/playwright-mcp-server
```

### Issue: API key errors

**Solution**: Verify your Anthropic API key is correct and has sufficient credits.

### Issue: Execution timeouts

**Solution**: Increase timeout in `app.py`:
```python
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=600  # Increase to 10 minutes
)
```

## 🎨 Customization

### Change Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"  # Your brand color
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Add Custom MDC Templates

Create a `templates/` directory with preset MDC files:

```python
# In app.py
templates_dir = Path("templates")
template_files = list(templates_dir.glob("*.mdc"))
```

### Customize Prompt Examples

Edit the `examples` list in `app.py`:

```python
examples = [
    "Your custom prompt 1",
    "Your custom prompt 2",
    # Add more...
]
```

## 📚 Advanced Features

### Multi-Step Automations

Chain multiple MDC files together:

```python
def execute_multi_mdc(mdc_files: List[str]):
    results = []
    for mdc_file in mdc_files:
        result = executor.execute_mdc_file(mdc_file)
        results.append(result)
        if not result['success']:
            break
    return results
```

### Scheduled Executions

Use Streamlit's experimental features:

```python
import streamlit as st
from datetime import datetime, timedelta

# Add scheduling UI
schedule_time = st.time_input("Schedule for", value=None)
if schedule_time:
    st.info(f"Automation scheduled for {schedule_time}")
```

### Export Results

Add result export functionality:

```python
import csv
import json

def export_results(results, format='csv'):
    if format == 'csv':
        # Export to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(results)
        return output.getvalue()
    elif format == 'json':
        return json.dumps(results, indent=2)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

- Open an issue on GitHub
- Check the troubleshooting section
- Review Streamlit documentation: https://docs.streamlit.io

## 🎯 Roadmap

- [ ] Add support for more MCP tools
- [ ] Implement user authentication
- [ ] Add automation scheduling
- [ ] Support for parallel executions
- [ ] Enhanced error reporting
- [ ] Export results to various formats
- [ ] Integration with CI/CD pipelines
- [ ] Mobile-responsive design improvements

## ⭐ Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Anthropic Claude](https://www.anthropic.com/) for AI
- Powered by [Playwright MCP](https://github.com/executeautomation/playwright-mcp-server)

---

**Made with ❤️ for automation enthusiasts**


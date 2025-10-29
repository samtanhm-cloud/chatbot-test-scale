"""
Streamlit MDC Executor with Playwright MCP
Allows users to execute MDC automation files via natural language prompts
"""

import streamlit as st
import subprocess
import json
import os
import time
from pathlib import Path
import asyncio
from typing import Dict, List, Optional
from openai import OpenAI
import requests
from datetime import datetime, timedelta

# ============================================================================
# NPM INSTALL CHECK - Install MCP SDK if not present
# ============================================================================
def ensure_npm_packages():
    """
    Ensure npm packages are installed before app starts.
    This is needed because Streamlit Cloud doesn't automatically run npm install.
    """
    import sys
    
    # Check if running on Streamlit Cloud
    is_cloud = os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud' or os.path.exists('/mount/src')
    
    # Path to node_modules
    node_modules_path = Path(__file__).parent / 'node_modules'
    mcp_sdk_path = node_modules_path / '@modelcontextprotocol' / 'sdk'
    
    # Check if MCP SDK is installed
    if not mcp_sdk_path.exists():
        print("⚠️  MCP SDK not found, installing npm packages...")
        
        try:
            # Run npm install
            result = subprocess.run(
                ['npm', 'install', '--production', '--prefer-offline'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ npm packages installed successfully")
                print(result.stdout)
            else:
                print(f"❌ npm install failed: {result.stderr}")
                # Continue anyway - app might still work in degraded mode
        except subprocess.TimeoutExpired:
            print("⚠️  npm install timed out after 5 minutes")
        except FileNotFoundError:
            print("❌ npm not found - Node.js may not be installed")
        except Exception as e:
            print(f"❌ Error installing npm packages: {e}")
    else:
        print("✅ MCP SDK already installed")

# Install npm packages on first run
ensure_npm_packages()

# Page configuration
st.set_page_config(
    page_title="MDC Automation Executor",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

class MDCExecutor:
    """Handles execution of MDC files with Playwright MCP"""
    
    def __init__(self, mdc_directory: str = ".", remote_url: str = None):
        self.mdc_directory = Path(mdc_directory)
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
        self.remote_url = remote_url or os.getenv("MDC_REMOTE_URL")
        self.cache_duration = int(os.getenv("MDC_CACHE_MINUTES", "30"))  # Cache for 30 minutes
        self.cache_file = Path(".mdc_cache.json")
        self.last_fetch = None
        
    def get_available_mdc_files(self) -> List[Dict[str, str]]:
        """Get available MDC files from local directory or remote server"""
        # Use remote only if explicitly configured
        if self.remote_url:
            try:
                return self._fetch_remote_mdc_files()
            except Exception as e:
                st.warning(f"⚠️ Remote server unavailable, using local files. Error: {str(e)}")
                return self._scan_local_mdc_files()
        
        # Default: use local directory
        return self._scan_local_mdc_files()
    
    def _scan_local_mdc_files(self) -> List[Dict[str, str]]:
        """Scan local directory for available MDC files"""
        mdc_files = []
        if not self.mdc_directory.exists():
            return mdc_files
            
        for file in self.mdc_directory.glob("*.mdc"):
            with open(file, 'r') as f:
                content = f.read()
                description = self._extract_description(content)
                mdc_files.append({
                    "name": file.name,
                    "path": str(file),
                    "description": description,
                    "source": "local"
                })
        return mdc_files
    
    def _fetch_remote_mdc_files(self) -> List[Dict[str, str]]:
        """Fetch MDC files from remote server with caching"""
        # Check cache first
        if self._is_cache_valid():
            return self._load_from_cache()
        
        # Fetch from remote
        mdc_files = []
        
        # Option 1: Fetch list endpoint (if server provides a list API)
        list_url = f"{self.remote_url}/list" if not self.remote_url.endswith('/list') else self.remote_url
        
        try:
            response = requests.get(list_url, timeout=10)
            response.raise_for_status()
            
            # Expecting JSON response: [{"name": "file.mdc", "url": "...", "description": "..."}]
            remote_files = response.json()
            
            for file_info in remote_files:
                # Download the actual MDC content
                content = self._download_mdc_content(file_info.get('url') or file_info.get('name'))
                
                # Cache locally
                local_path = self._cache_remote_file(file_info['name'], content)
                
                mdc_files.append({
                    "name": file_info['name'],
                    "path": local_path,
                    "description": file_info.get('description') or self._extract_description(content),
                    "source": "remote",
                    "remote_url": file_info.get('url')
                })
            
            # Save to cache
            self._save_to_cache(mdc_files)
            
        except requests.exceptions.RequestException as e:
            # If list endpoint fails, try direct file access (Option 2)
            st.info("📡 Trying alternative remote access method...")
            mdc_files = self._fetch_remote_files_direct()
        
        return mdc_files
    
    def _download_mdc_content(self, file_url: str) -> str:
        """Download MDC file content from URL"""
        if not file_url.startswith('http'):
            file_url = f"{self.remote_url.rstrip('/')}/{file_url}"
        
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def _cache_remote_file(self, filename: str, content: str) -> str:
        """Cache remote MDC file locally"""
        cache_dir = Path(".mdc_remote_cache")
        cache_dir.mkdir(exist_ok=True)
        
        local_path = cache_dir / filename
        with open(local_path, 'w') as f:
            f.write(content)
        
        return str(local_path)
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_file.exists():
            return False
        
        cache_data = self._load_cache_metadata()
        if not cache_data:
            return False
        
        cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
        return datetime.now() - cache_time < timedelta(minutes=self.cache_duration)
    
    def _load_from_cache(self) -> List[Dict[str, str]]:
        """Load MDC files from cache"""
        cache_data = self._load_cache_metadata()
        return cache_data.get('files', [])
    
    def _save_to_cache(self, mdc_files: List[Dict[str, str]]):
        """Save MDC files list to cache"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'files': mdc_files
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)
    
    def _load_cache_metadata(self) -> Dict:
        """Load cache metadata"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _fetch_remote_files_direct(self) -> List[Dict[str, str]]:
        """Fallback: Try to fetch known MDC files directly"""
        # This is a fallback if the server doesn't have a list endpoint
        # You can configure expected filenames in environment
        mdc_files = []
        expected_files = os.getenv("MDC_EXPECTED_FILES", "").split(',')
        
        for filename in expected_files:
            if not filename.strip():
                continue
                
            try:
                content = self._download_mdc_content(filename.strip())
                local_path = self._cache_remote_file(filename.strip(), content)
                
                mdc_files.append({
                    "name": filename.strip(),
                    "path": local_path,
                    "description": self._extract_description(content),
                    "source": "remote"
                })
            except:
                continue
        
        return mdc_files
    
    def refresh_remote_files(self):
        """Force refresh from remote server"""
        if self.cache_file.exists():
            self.cache_file.unlink()
        self.last_fetch = None
    
    def _extract_description(self, content: str) -> str:
        """Extract description from MDC file content"""
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if 'description' in line.lower() or line.startswith('#'):
                return line.strip('# ').strip()
        return "No description available"
    
    def execute_mdc_file(self, mdc_path: str, context: Dict = None) -> Dict:
        """Execute an MDC file with Playwright MCP"""
        try:
            # Read MDC file
            with open(mdc_path, 'r') as f:
                mdc_content = f.read()
            
            # Prepare execution command
            # This assumes you have a Node.js script that can execute MDC with MCP
            cmd = [
                "node",
                "mdc_executor.js",
                mdc_path
            ]
            
            # Add context if provided
            if context:
                cmd.extend(["--context", json.dumps(context)])
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "mdc_file": mdc_path
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout (5 minutes)",
                "mdc_file": mdc_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mdc_file": mdc_path
            }


class PromptProcessor:
    """Process user prompts and match to appropriate MDC files"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Check authentication type
        api_type = os.getenv("OPENAI_API_TYPE", "").lower()
        
        if api_type == "azure_ad":
            # Azure AD (Service Principal) Authentication
            try:
                from azure.identity import ClientSecretCredential
                from openai import AzureOpenAI
                
                # Get Azure AD credentials
                tenant_id = os.getenv("AZURE_TENANT_ID")
                client_id = os.getenv("AZURE_CLIENT_ID")
                client_secret = os.getenv("AZURE_CLIENT_SECRET")
                
                if not all([tenant_id, client_id, client_secret]):
                    st.error("Missing Azure AD credentials. Check AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
                    self.client = None
                    self.is_azure = False
                    self.api_key = None
                    return
                
                # Create Azure AD credential
                credential = ClientSecretCredential(
                    tenant_id=tenant_id.strip("'\""),
                    client_id=client_id.strip("'\""),
                    client_secret=client_secret.strip("'\"")
                )
                
                # Get token for Azure OpenAI
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                
                # Initialize Azure OpenAI client with token
                self.client = AzureOpenAI(
                    api_key=token.token,
                    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.getenv("OPENAI_API_BASE")
                )
                self.is_azure = True
                self.api_key = "azure_ad_token"
                self.credential = credential
                
            except Exception as e:
                st.error(f"Azure AD authentication failed: {str(e)}")
                self.client = None
                self.is_azure = False
                self.api_key = None
                
        elif api_type == "azure":
            # Azure OpenAI with API Key
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.getenv("OPENAI_API_BASE")
                )
                self.is_azure = True
            else:
                self.client = None
                self.is_azure = False
        else:
            # Standard OpenAI
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                self.is_azure = False
            else:
                self.client = None
                self.is_azure = False
    
    def match_prompt_to_mdc(self, prompt: str, available_mdc: List[Dict]) -> Dict:
        """Match user prompt to the most appropriate MDC file"""
        
        if not self.client:
            # Simple keyword matching fallback
            return self._simple_match(prompt, available_mdc)
        
        # Use OpenAI to intelligently match prompt to MDC file
        mdc_descriptions = "\n".join([
            f"{i+1}. {mdc['name']}: {mdc['description']}"
            for i, mdc in enumerate(available_mdc)
        ])
        
        system_prompt = f"""You are an automation assistant. Match user requests to available MDC automation files.

Available MDC files:
{mdc_descriptions}

Respond with JSON containing:
- "mdc_index": index of best matching MDC file (0-based)
- "confidence": confidence score 0-1
- "reason": brief explanation
- "parameters": any extracted parameters from the prompt

Example response:
{{"mdc_index": 0, "confidence": 0.95, "reason": "Keywords match automation purpose", "parameters": {{}}}}
"""
        
        try:
            # Use deployment name for Azure, model name for standard OpenAI
            if self.is_azure:
                model_or_deployment = os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4")
            else:
                model_or_deployment = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            response = self.client.chat.completions.create(
                model=model_or_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1024,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            
            if result.get("mdc_index") is not None:
                return {
                    "mdc_file": available_mdc[result["mdc_index"]],
                    "confidence": result.get("confidence", 0.5),
                    "reason": result.get("reason", ""),
                    "parameters": result.get("parameters", {})
                }
        except Exception as e:
            st.warning(f"AI matching failed, using fallback: {str(e)}")
        
        return self._simple_match(prompt, available_mdc)
    
    def _simple_match(self, prompt: str, available_mdc: List[Dict]) -> Dict:
        """Simple keyword-based matching fallback"""
        prompt_lower = prompt.lower()
        
        best_match = None
        best_score = 0
        
        for mdc in available_mdc:
            score = 0
            mdc_text = f"{mdc['name']} {mdc['description']}".lower()
            
            # Count keyword matches
            words = prompt_lower.split()
            for word in words:
                if len(word) > 3 and word in mdc_text:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = mdc
        
        return {
            "mdc_file": best_match or available_mdc[0],
            "confidence": min(best_score / 5, 1.0),
            "reason": f"Keyword matching (score: {best_score})",
            "parameters": {}
        }


def init_session_state():
    """Initialize session state variables"""
    if 'execution_history' not in st.session_state:
        st.session_state.execution_history = []
    if 'mdc_executor' not in st.session_state:
        # Default to local directory, remote is optional
        st.session_state.mdc_executor = MDCExecutor()
    if 'prompt_processor' not in st.session_state:
        st.session_state.prompt_processor = PromptProcessor()


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎭 MDC Automation Executor</div>', 
                unsafe_allow_html=True)
    st.markdown("Execute browser automation tasks with natural language prompts")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check for pre-configured credentials
        api_type = os.getenv("OPENAI_API_TYPE", "").lower()
        
        # Check if credentials are configured
        has_credentials = False
        if api_type == "azure_ad":
            # Check Azure AD credentials
            has_credentials = all([
                os.getenv("AZURE_TENANT_ID"),
                os.getenv("AZURE_CLIENT_ID"),
                os.getenv("AZURE_CLIENT_SECRET")
            ])
        else:
            # Check API key
            has_credentials = bool(os.getenv("OPENAI_API_KEY"))
        
        if has_credentials:
            # Credentials are pre-configured - no input needed!
            st.success("🟢 AI Model: Connected")
            
            # Show appropriate authentication info
            if api_type == "azure_ad":
                deployment = os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4")
                endpoint = os.getenv("OPENAI_API_BASE", "not-set")
                tenant_id = os.getenv("AZURE_TENANT_ID", "")[:8]
                st.caption(f"Using Azure OpenAI (Azure AD)")
                st.caption(f"Deployment: {deployment}")
                st.caption(f"Endpoint: {endpoint[:40]}...")
                st.caption(f"Tenant: {tenant_id}...")
            elif api_type == "azure":
                deployment = os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4")
                endpoint = os.getenv("OPENAI_API_BASE", "not-set")
                st.caption(f"Using Azure OpenAI (API Key)")
                st.caption(f"Deployment: {deployment}")
                st.caption(f"Endpoint: {endpoint[:40]}...")
            else:
                model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                st.caption(f"Using OpenAI {model_name}")
            
            # Initialize processor if not already done
            if 'prompt_processor' not in st.session_state:
                st.session_state.prompt_processor = PromptProcessor()
        else:
            # Fallback: Allow manual API key input (for local development)
            st.warning("⚠️ No API key configured")
            
            with st.expander("🔧 Manual Configuration (Optional)", expanded=False):
                st.caption("For testing only - administrators should configure API keys in deployment settings")
                
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key for intelligent prompt matching"
                )
                
                if api_key:
                    # Optional: Model selection
                    model = st.selectbox(
                        "Model",
                        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                        help="Select OpenAI model to use"
                    )
                    
                    os.environ["OPENAI_API_KEY"] = api_key
                    os.environ["OPENAI_MODEL"] = model
                    st.session_state.prompt_processor = PromptProcessor(api_key)
                    st.rerun()  # Refresh to show connected status
        
        # MDC Directory Configuration
        mdc_dir = st.text_input(
            "MDC Files Directory",
            value=str(Path.cwd() / "mdc_files"),
            help="Path to directory containing MDC files"
        )
        st.session_state.mdc_executor.mdc_directory = Path(mdc_dir)
        st.session_state.mdc_executor.remote_url = None
        
        # Optional: Remote server (advanced)
        with st.expander("🌐 Advanced: Use Remote Server (Optional)", expanded=False):
            st.caption("Load MDC files from a remote server instead of local directory")
            
            remote_url = st.text_input(
                "Remote Server URL",
                value=os.getenv("MDC_REMOTE_URL", ""),
                placeholder="https://your-server.com/mdc-files",
                help="URL to your MDC files server (API endpoint or base URL)"
            )
            
            if remote_url:
                use_remote = st.checkbox("Enable Remote Server", value=False)
                
                if use_remote:
                    st.session_state.mdc_executor.remote_url = remote_url
                    os.environ["MDC_REMOTE_URL"] = remote_url
                    
                    # Refresh button
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("🔄 Refresh from Server"):
                            st.session_state.mdc_executor.refresh_remote_files()
                            st.success("Refreshed from server!")
                            st.rerun()
                    
                    with col2:
                        cache_info = st.session_state.mdc_executor._load_cache_metadata()
                        if cache_info:
                            cache_time = cache_info.get('timestamp', 'Unknown')
                            st.caption(f"🕒 Cached: {cache_time[:16] if cache_time != 'Unknown' else 'Never'}")
                else:
                    st.session_state.mdc_executor.remote_url = None
        
        st.divider()
        
        # Available MDC files
        st.header("📁 Available Automations")
        
        with st.spinner("Loading MDC files..."):
            available_mdc = st.session_state.mdc_executor.get_available_mdc_files()
        
        if available_mdc:
            # Show source indicator
            sources = set(mdc.get('source', 'local') for mdc in available_mdc)
            if 'remote' in sources:
                st.success(f"🌐 {len(available_mdc)} file(s) from remote server")
            else:
                st.info(f"💻 {len(available_mdc)} file(s) from local directory")
            
            for mdc in available_mdc:
                source_icon = "🌐" if mdc.get('source') == 'remote' else "💻"
                with st.expander(f"{source_icon} {mdc['name']}"):
                    st.write(mdc['description'])
                    st.caption(f"Source: {mdc.get('source', 'local').title()}")
                    if mdc.get('remote_url'):
                        st.caption(f"URL: {mdc['remote_url']}")
                    st.code(mdc['path'], language=None)
        else:
            st.warning("No MDC files found. Check your configuration.")
        
        st.divider()
        
        # Execution History
        st.header("📊 History")
        if st.session_state.execution_history:
            st.metric("Total Executions", len(st.session_state.execution_history))
            if st.button("Clear History"):
                st.session_state.execution_history = []
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Enter Your Automation Prompt")
        
        # Prompt input
        user_prompt = st.text_area(
            "What would you like to automate?",
            height=150,
            placeholder="Example: Validate links on the German documentation page for product XYZ",
            help="Describe your automation task in natural language"
        )
        
        # Example prompts
        st.markdown("**💡 Example prompts:**")
        examples = [
            "Validate email links in Draftr content",
            "Check AEM page for broken links",
            "Validate localization links for Japanese content",
            "Extract and validate links from TermWeb"
        ]
        
        example_cols = st.columns(2)
        for idx, example in enumerate(examples):
            with example_cols[idx % 2]:
                if st.button(example, key=f"example_{idx}"):
                    user_prompt = example
                    st.rerun()
        
        st.divider()
        
        # Execution button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            execute_btn = st.button("▶️ Execute", type="primary", use_container_width=True)
        
        with col_btn2:
            analyze_btn = st.button("🔍 Analyze Only", use_container_width=True)
        
        # Execute automation
        if execute_btn and user_prompt:
            with st.spinner("🔄 Processing your request..."):
                # Get available MDC files
                available_mdc = st.session_state.mdc_executor.get_available_mdc_files()
                
                if not available_mdc:
                    st.error("No MDC files found. Please add MDC files to the directory.")
                else:
                    # Match prompt to MDC file
                    match_result = st.session_state.prompt_processor.match_prompt_to_mdc(
                        user_prompt, 
                        available_mdc
                    )
                    
                    st.info(f"🎯 Selected: **{match_result['mdc_file']['name']}**\n\n"
                           f"Confidence: {match_result['confidence']:.0%}\n\n"
                           f"Reason: {match_result['reason']}")
                    
                    # Execute the MDC file
                    with st.spinner("⚙️ Executing automation..."):
                        result = st.session_state.mdc_executor.execute_mdc_file(
                            match_result['mdc_file']['path'],
                            context=match_result['parameters']
                        )
                        
                        # Store in history
                        st.session_state.execution_history.append({
                            "timestamp": time.time(),
                            "prompt": user_prompt,
                            "mdc_file": match_result['mdc_file']['name'],
                            "result": result
                        })
                        
                        # Display results
                        if result['success']:
                            st.success("✅ Automation completed successfully!")
                            st.subheader("📋 Output")
                            st.code(result['output'], language='text')
                        else:
                            st.error("❌ Automation failed")
                            st.subheader("🐛 Error Details")
                            st.code(result['error'], language='text')
        
        # Analyze only (don't execute)
        elif analyze_btn and user_prompt:
            with st.spinner("🔍 Analyzing your request..."):
                available_mdc = st.session_state.mdc_executor.get_available_mdc_files()
                
                if available_mdc:
                    match_result = st.session_state.prompt_processor.match_prompt_to_mdc(
                        user_prompt, 
                        available_mdc
                    )
                    
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown(f"""
                    **🎯 Matched MDC File:** {match_result['mdc_file']['name']}
                    
                    **📊 Confidence:** {match_result['confidence']:.0%}
                    
                    **💡 Reason:** {match_result['reason']}
                    
                    **📁 File Path:** `{match_result['mdc_file']['path']}`
                    
                    **📝 Description:** {match_result['mdc_file']['description']}
                    """)
                    
                    if match_result['parameters']:
                        st.markdown("**⚙️ Extracted Parameters:**")
                        st.json(match_result['parameters'])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.header("📊 Execution Status")
        
        # Real-time status
        status_container = st.container()
        
        with status_container:
            if st.session_state.execution_history:
                latest = st.session_state.execution_history[-1]
                
                st.metric(
                    "Last Execution",
                    "Success" if latest['result']['success'] else "Failed",
                    delta=None
                )
                
                st.write(f"**Prompt:** {latest['prompt'][:50]}...")
                st.write(f"**MDC File:** {latest['mdc_file']}")
                st.write(f"**Time:** {time.strftime('%H:%M:%S', time.localtime(latest['timestamp']))}")
            else:
                st.info("No executions yet. Enter a prompt to get started!")
        
        st.divider()
        
        # System status
        st.subheader("🔧 System Status")
        
        # Check API credentials
        api_type = os.getenv("OPENAI_API_TYPE", "").lower()
        if api_type == "azure_ad":
            has_creds = all([os.getenv("AZURE_TENANT_ID"), os.getenv("AZURE_CLIENT_ID"), os.getenv("AZURE_CLIENT_SECRET")])
        else:
            has_creds = bool(os.getenv("OPENAI_API_KEY"))
        
        api_status = "🟢 AI Connected" if has_creds else "🟡 Fallback Mode"
        st.write(f"**AI Service:** {api_status}")
        
        # Check MCP server
        mcp_status = "🟢 Ready" if os.getenv("MCP_SERVER_URL") else "🟢 Local"
        st.write(f"**MCP Server:** {mcp_status}")
        
        # MDC files count
        mdc_count = len(st.session_state.mdc_executor.get_available_mdc_files())
        st.write(f"**MDC Files:** {mdc_count}")
    
    # Recent execution history
    if st.session_state.execution_history:
        st.divider()
        st.header("📜 Recent Executions")
        
        # Show last 5 executions
        for idx, execution in enumerate(reversed(st.session_state.execution_history[-5:])):
            with st.expander(
                f"{'✅' if execution['result']['success'] else '❌'} "
                f"{execution['prompt'][:50]}... - "
                f"{time.strftime('%H:%M:%S', time.localtime(execution['timestamp']))}"
            ):
                st.write(f"**MDC File:** {execution['mdc_file']}")
                st.write(f"**Prompt:** {execution['prompt']}")
                
                if execution['result']['success']:
                    st.code(execution['result']['output'][:500], language='text')
                else:
                    st.error(execution['result']['error'][:500])


if __name__ == "__main__":
    main()


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
def setup_virtual_display():
    """
    Setup virtual display for browser automation on Streamlit Cloud.
    This is lightweight and safe to run at import time.
    """
    # Check if running on Streamlit Cloud
    is_cloud = os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud' or os.path.exists('/mount/src')
    
    # Setup virtual display for browser automation (Streamlit Cloud has no X server)
    if is_cloud:
        # Set DISPLAY environment variable for all subprocesses
        os.environ['DISPLAY'] = ':99'
        
        # Start Xvfb in background if not already running
        try:
            # Check if Xvfb is already running
            check_xvfb = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, timeout=5)
            if check_xvfb.returncode != 0:
                # Start Xvfb in background
                subprocess.Popen(
                    ['Xvfb', ':99', '-screen', '0', '1920x1080x24', '-nolisten', 'tcp'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(1)  # Give Xvfb time to start
        except Exception:
            pass  # Xvfb might already be running or not needed

def check_dependencies():
    """
    Quick check if dependencies are installed. Non-blocking.
    Returns status dict.
    """
    node_modules_path = Path(__file__).parent / 'node_modules'
    mcp_sdk_path = node_modules_path / '@modelcontextprotocol' / 'sdk'
    playwright_marker = Path(__file__).parent / '.playwright_installed'
    
    return {
        'npm_packages': mcp_sdk_path.exists(),
        'playwright': playwright_marker.exists(),
        'display': os.getenv('DISPLAY') is not None
    }

def install_dependencies_if_needed():
    """
    Install npm packages and Playwright browsers if not present.
    This should be called lazily, not at import time.
    Returns dict with success status, logs, and details.
    """
    deps = check_dependencies()
    
    if deps['npm_packages'] and deps['playwright']:
        return {
            'success': True,
            'message': 'Dependencies already installed',
            'details': {
                'npm_packages': 'Already installed',
                'playwright': 'Already installed'
            },
            'logs': []
        }
    
    # Path to node_modules
    node_modules_path = Path(__file__).parent / 'node_modules'
    mcp_sdk_path = node_modules_path / '@modelcontextprotocol' / 'sdk'
    playwright_marker = Path(__file__).parent / '.playwright_installed'
    
    logs = []
    details = {}
    
    # Install npm packages if needed
    if not mcp_sdk_path.exists():
        logs.append("📦 Installing npm packages...")
        logs.append(f"   Working directory: {Path(__file__).parent}")
        logs.append(f"   Command: npm install --production --prefer-offline")
        logs.append(f"   Started at: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                ['npm', 'install', '--production', '--prefer-offline'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            elapsed = time.time() - start_time
            
            logs.append(f"   Completed in {elapsed:.1f} seconds")
            logs.append(f"   Return code: {result.returncode}")
            
            # Show npm output (abbreviated)
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                logs.append(f"   Output: {stdout_lines[-1] if stdout_lines else 'none'}")  # Last line
            
            if result.returncode == 0:
                # Verify installation
                if mcp_sdk_path.exists():
                    logs.append("✅ npm packages installed successfully")
                    # Count installed packages and calculate size
                    try:
                        pkg_count = len(list(node_modules_path.iterdir())) if node_modules_path.exists() else 0
                        # Calculate total size
                        total_size = sum(f.stat().st_size for f in node_modules_path.rglob('*') if f.is_file())
                        size_mb = total_size / (1024 * 1024)
                        details['npm_packages'] = f'Installed ({pkg_count} packages, {size_mb:.1f} MB)'
                        logs.append(f"   Installed {pkg_count} packages ({size_mb:.1f} MB)")
                    except Exception as e:
                        details['npm_packages'] = 'Installed'
                        logs.append(f"   Package count error: {str(e)}")
                    
                    # Verify specific key packages
                    key_packages = ['@modelcontextprotocol/sdk', '@executeautomation/playwright-mcp-server']
                    for pkg in key_packages:
                        pkg_path = node_modules_path / pkg.replace('/', os.sep)
                        if pkg_path.exists():
                            logs.append(f"   ✅ {pkg} verified")
                        else:
                            logs.append(f"   ⚠️  {pkg} not found")
                else:
                    logs.append("❌ npm packages installation failed (MCP SDK not found)")
                    logs.append(f"   Expected path: {mcp_sdk_path}")
                    return {'success': False, 'message': 'npm installation incomplete', 'details': details, 'logs': logs}
            else:
                logs.append(f"❌ npm install failed with return code {result.returncode}")
                if result.stderr:
                    logs.append(f"   Error: {result.stderr[:300]}")
                return {'success': False, 'message': 'npm install failed', 'details': details, 'logs': logs}
        except subprocess.TimeoutExpired:
            logs.append("❌ npm install timed out after 5 minutes")
            return {'success': False, 'message': 'npm install timeout', 'details': details, 'logs': logs}
        except Exception as e:
            logs.append(f"❌ npm install error: {str(e)}")
            return {'success': False, 'message': str(e), 'details': details, 'logs': logs}
    else:
        logs.append("✅ npm packages already installed")
        # Show what's already there
        try:
            pkg_count = len(list(node_modules_path.iterdir())) if node_modules_path.exists() else 0
            logs.append(f"   Found {pkg_count} existing packages")
        except:
            pass
        details['npm_packages'] = 'Already installed'
    
    # Install Playwright browsers if needed
    if not playwright_marker.exists():
        logs.append("🎭 Installing Playwright Chrome browser...")
        
        # Install browsers for playwright-core (used by MCP server)
        # MCP server looks in: node_modules/playwright-core/.local-browsers/
        # CRITICAL: Set PLAYWRIGHT_BROWSERS_PATH=0 to force LOCAL installation
        
        logs.append(f"   Started at: {datetime.now().strftime('%H:%M:%S')}")
        logs.append(f"   Target: node_modules/playwright-core/.local-browsers/")
        
        # Prepare environment with LOCAL browser installation flag
        install_env = os.environ.copy()
        install_env['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # Force local installation
        logs.append(f"   PLAYWRIGHT_BROWSERS_PATH=0 (forces local install)")
        
        install_commands = [
            {
                'cmd': ['node', 'node_modules/playwright-core/cli.js', 'install', 'chrome'],
                'desc': 'playwright-core CLI (local mode)',
                'env': install_env
            },
            {
                'cmd': ['npx', 'playwright-core', 'install', 'chrome'],
                'desc': 'playwright-core via npx (local mode)',
                'env': install_env
            }
        ]
        
        all_successful = False
        
        for install_cmd in install_commands:
            logs.append(f"   Installing: {install_cmd['desc']}")
            logs.append(f"   Command: {' '.join(install_cmd['cmd'][:4])}...")
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    install_cmd['cmd'],
                    cwd=Path(__file__).parent,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    env=install_cmd.get('env', os.environ.copy())  # Use custom env if provided
                )
                elapsed = time.time() - start_time
                
                logs.append(f"   Completed in {elapsed:.1f} seconds")
                logs.append(f"   Return code: {result.returncode}")
                
                if result.returncode == 0:
                    logs.append(f"   ✅ {install_cmd['desc']} installed successfully")
                    all_successful = True
                else:
                    logs.append(f"   ⚠️  {install_cmd['desc']} returned {result.returncode}")
                    if result.stderr:
                        logs.append(f"   {result.stderr[:100]}")
            except Exception as e:
                logs.append(f"   ⚠️  {install_cmd['desc']} error: {str(e)[:50]}")
                continue
        
        # After trying all methods, verify browser binary exists
        # Chrome uses the system Chrome installation via channel
        # Check for marker file instead of specific browser path
        logs.append(f"   Verifying Chrome browser installation...")
        
        if all_successful:
            logs.append(f"   ✅ Chrome browser installed successfully!")
            playwright_marker.touch()
            details['playwright'] = 'Chrome installed and verified'
        else:
            logs.append("   ❌ Browser installation failed")
            logs.append("   ⚠️  All installation methods failed")
            playwright_marker.touch()  # Mark as attempted to avoid retry loops
            details['playwright'] = 'Installation failed - try Force Reinstall'
    else:
        logs.append("✅ Playwright already installed")
        logs.append(f"   Marker file exists: {playwright_marker}")
        details['playwright'] = 'Already installed'
    
    # Final verification
    final_deps = check_dependencies()
    if final_deps['npm_packages'] and final_deps['playwright']:
        logs.append("✅ All dependencies verified and ready!")
        return {
            'success': True,
            'message': 'All dependencies installed successfully',
            'details': details,
            'logs': logs
        }
    else:
        logs.append("⚠️  Installation completed but verification failed")
        return {
            'success': False,
            'message': 'Installation incomplete',
            'details': details,
            'logs': logs
        }

# Setup virtual display at import time (fast, non-blocking)
setup_virtual_display()

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
            # Use xvfb-run to wrap the command on Streamlit Cloud
            is_cloud = os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud' or os.path.exists('/mount/src')
            
            if is_cloud:
                # Wrap with xvfb-run to provide X server
                cmd = [
                    "xvfb-run",
                    "--auto-servernum",
                    "--server-args=-screen 0 1920x1080x24",
                    "node",
                    "mdc_executor.js",
                    mdc_path
                ]
            else:
                # Local execution without xvfb-run
                cmd = [
                    "node",
                    "mdc_executor.js",
                    mdc_path
                ]
            
            # Load authentication from secrets (IDSDK token or cookies)
            if not context:
                context = {}
            
            auth_method = None
            
            # Check for authentication in secrets
            try:
                print("🔍 Checking for authentication credentials...")
                print(f"   hasattr(st, 'secrets'): {hasattr(st, 'secrets')}")
                if hasattr(st, 'secrets'):
                    print(f"   Available secrets: {list(st.secrets.keys())}")
                
                # Method 1: IDSDK OAuth Token (PREFERRED)
                if hasattr(st, 'secrets') and 'AUTODESK_ACCESS_TOKEN' in st.secrets:
                    print("🔐 Loading Autodesk OAuth token from secrets...")
                    token = st.secrets['AUTODESK_ACCESS_TOKEN']
                    
                    # Check if token is expired
                    token_expires_at = st.secrets.get('AUTODESK_TOKEN_EXPIRES_AT', 0)
                    import time
                    if token_expires_at and time.time() < token_expires_at:
                        context['autodesk_token'] = token
                        auth_method = 'IDSDK OAuth Token'
                        expires_in = int(token_expires_at - time.time())
                        print(f"✅ Loaded OAuth token (expires in {expires_in} seconds)")
                    else:
                        print("⚠️  OAuth token expired!")
                        print("   Run: python3 autodesk_idsdk_login.py")
                
                # Method 2: Session Cookies (FALLBACK)
                if not auth_method and hasattr(st, 'secrets') and 'DRAFTR_COOKIES' in st.secrets:
                    print("🔐 Loading authentication cookies from secrets...")
                    cookies_json = st.secrets['DRAFTR_COOKIES']
                    cookies = json.loads(cookies_json)
                    context['cookies'] = cookies
                    auth_method = 'Session Cookies'
                    print(f"✅ Loaded {len(cookies)} cookies for authentication")
                
                # No authentication found
                if not auth_method:
                    print("❌ No authentication found in secrets!")
                    print("⚠️  Automation will run WITHOUT authentication")
                    print()
                    print("📋 To add authentication:")
                    print("   Option 1 (RECOMMENDED): IDSDK OAuth Token")
                    print("      Run: python3 autodesk_idsdk_login.py")
                    print("      Then copy token to secrets")
                    print()
                    print("   Option 2 (FALLBACK): Session Cookies")
                    print("      Run: node capture-cookies.js")
                    print("      Then add DRAFTR_COOKIES to secrets")
                    
            except Exception as e:
                print(f"⚠️  Could not load authentication from secrets: {e}")
                print("⚠️  Continuing without authentication...")
            
            # Add context if provided
            if context:
                cmd.extend(["--context", json.dumps(context)])
            
            # Prepare environment with DISPLAY variable and headless config
            env = os.environ.copy()
            
            # Ensure DISPLAY is set for browser automation
            if 'DISPLAY' not in env or not env['DISPLAY']:
                env['DISPLAY'] = ':99'
                print(f"🔧 Setting DISPLAY={env['DISPLAY']} for subprocess")
            
            # Force Playwright to run in headless mode (critical for cloud)
            env['PLAYWRIGHT_HEADLESS'] = '1'
            env['BROWSER_HEADLESS'] = 'true'
            env['HEADLESS'] = 'true'
            
            # Additional Playwright browser args for stability
            env['PLAYWRIGHT_CHROMIUM_NO_SANDBOX'] = '1'
            
            print(f"🚀 Executing: {' '.join(cmd)}")
            print(f"📂 Working directory: {Path(__file__).parent}")
            print(f"📺 DISPLAY={env.get('DISPLAY', 'NOT SET')}")
            print(f"🎭 HEADLESS={env.get('PLAYWRIGHT_HEADLESS', 'NOT SET')}")
            
            # Check if Node.js is available
            node_check = subprocess.run(['which', 'node'], capture_output=True, text=True)
            print(f"🟢 Node.js path: {node_check.stdout.strip()}")
            
            # Check if mdc_executor.js exists
            executor_path = Path(__file__).parent / 'mdc_executor.js'
            print(f"🟢 Executor exists: {executor_path.exists()}")
            
            # Execute with explicit environment
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent,  # Ensure correct working directory
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env  # Pass environment with DISPLAY
            )
            elapsed = time.time() - start_time
            
            print(f"⏱️  Execution completed in {elapsed:.2f} seconds")
            print(f"📤 Return code: {result.returncode}")
            print(f"📝 Stdout length: {len(result.stdout)} chars")
            print(f"📝 Stderr length: {len(result.stderr)} chars")
            
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
        
        system_prompt = f"""You are an automation assistant. Match user requests to available MDC automation files and extract variables.

Available MDC files:
{mdc_descriptions}

Respond with JSON containing:
- "mdc_index": index of best matching MDC file (0-based)
- "confidence": confidence score 0-1
- "reason": brief explanation
- "variables": extracted variables from the prompt (e.g., asset_id, new_url, link_text)

For Draftr automation prompts, extract these variables:
- "asset_id": Draftr asset ID (from URL like draftr/asset/3934720)
- "new_url": Target URL to update link to (from patterns like to "url" or to <url>)
- "link_text": Text to identify specific link (from patterns like link in "text")
- "old_url": Old URL pattern to replace (from patterns like replace all "url")
- "old_domain": Old domain to replace (from patterns like domain "/en/")
- "new_domain": New domain to use (from patterns like to "/uk/")
- "operation": Type of operation (change_specific, replace_all, replace_domain)

Supported prompt formats:
1. run mdc on https://webpub.autodesk.com/draftr/asset/123456 and change link in "text" to "newurl.com"
2. run mdc on URL https://webpub.autodesk.com/draftr/asset/123456 to replace all "oldurl.com" links to "newurl.com"
3. run mdc on URL https://webpub.autodesk.com/draftr/asset/123456 to replace all domain "/en/" links to "/uk/"

Example responses:
{{"mdc_index": 0, "confidence": 0.95, "reason": "Draftr link update", "variables": {{"asset_id": "3934720", "new_url": "www.autodesk.com/uk/support", "link_text": "Get in touch", "operation": "change_specific"}}}}
{{"mdc_index": 0, "confidence": 0.90, "reason": "Draftr bulk replace", "variables": {{"asset_id": "123456", "old_url": "oldsite.com", "new_url": "newsite.com", "operation": "replace_all"}}}}
{{"mdc_index": 0, "confidence": 0.88, "reason": "Draftr domain replace", "variables": {{"asset_id": "789012", "old_domain": "/en/", "new_domain": "/uk/", "operation": "replace_domain"}}}}
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
                # Extract variables, support both 'variables' and 'parameters' keys for backward compatibility
                variables = result.get("variables", result.get("parameters", {}))
                
                # If no variables extracted by AI, try regex fallback
                if not variables:
                    variables = self._extract_variables_fallback(prompt)
                
                return {
                    "mdc_file": available_mdc[result["mdc_index"]],
                    "confidence": result.get("confidence", 0.5),
                    "reason": result.get("reason", ""),
                    "parameters": {"variables": variables} if variables else {}
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
        
        # Extract variables using regex fallback
        variables = self._extract_variables_fallback(prompt)
        
        return {
            "mdc_file": best_match or available_mdc[0],
            "confidence": min(best_score / 5, 1.0),
            "reason": f"Keyword matching (score: {best_score})",
            "parameters": {"variables": variables} if variables else {}
        }
    
    def _extract_variables_fallback(self, prompt: str) -> Dict:
        """Extract variables from prompt using regex patterns (fallback method)
        
        Supports these prompt formats:
        1. run mdc on https://webpub.autodesk.com/draftr/asset/<assetID> and change link in "<text>" to "<New Link>"
        2. run mdc on URL https://webpub.autodesk.com/draftr/asset/<assetID> to replace all "<Links>" links to "<new links>"
        3. run mdc on URL https://webpub.autodesk.com/draftr/asset/<assetID> to replace all domain "<domain>" links to "<new domain>"
        """
        import re
        variables = {}
        
        # Extract asset ID - supports multiple formats
        asset_patterns = [
            r'asset[/:](\d+)',  # "asset/123456" or "asset:123456"
            r'asset[=\s]+(\d+)',  # "asset=123456" or "asset 123456"
            r'draftr/asset/(\d+)',  # Full URL "draftr/asset/123456"
            r'on\s+(\d{6,8})',  # "on 123456"
        ]
        
        for pattern in asset_patterns:
            asset_match = re.search(pattern, prompt, re.IGNORECASE)
            if asset_match:
                variables['asset_id'] = asset_match.group(1)
                break
        
        # Extract "new link" URL - the target/destination URL
        # Look for patterns like: to "url", to "<url>", links to "url"
        new_url_patterns = [
            r'to\s+"([^"]+)"',  # to "url"
            r'to\s+<([^>]+)>',  # to <url>
            r'to\s+["\']([^"\']+)["\']',  # to 'url' or to "url"
            r'links?\s+to\s+"([^"]+)"',  # links to "url"
            r'links?\s+to\s+<([^>]+)>',  # links to <url>
            r'to\s+((?:https?://)?[a-z0-9.-]+\.[a-z]{2,}(?:/[\w./-]*)*)',  # to www.example.com/path
        ]
        
        for pattern in new_url_patterns:
            url_match = re.search(pattern, prompt, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                # Normalize URL (remove protocol if present)
                url = re.sub(r'^https?://', '', url)
                variables['new_url'] = url
                break
        
        # Extract "link text" - text to identify which link to change
        # Formats: link in "text", change link in "<text>", "<text>"
        link_text_patterns = [
            r'link\s+in\s+"([^"]+)"',  # link in "text"
            r'link\s+in\s+<([^>]+)>',  # link in <text>
            r'change\s+link\s+in\s+"([^"]+)"',  # change link in "text"
            r'in\s+"([^"]+)"\s+(?:to|link)',  # in "text" to/link
        ]
        
        for pattern in link_text_patterns:
            text_match = re.search(pattern, prompt, re.IGNORECASE)
            if text_match:
                variables['link_text'] = text_match.group(1)
                break
        
        # Extract "links to replace" - old URL pattern to find and replace
        # Formats: replace all "url", replace all domain "domain"
        old_url_patterns = [
            r'replace\s+all\s+"([^"]+)"\s+links',  # replace all "url" links
            r'replace\s+all\s+<([^>]+)>\s+links',  # replace all <url> links
            r'replace\s+all\s+domain\s+"([^"]+)"',  # replace all domain "domain"
            r'replace\s+all\s+domain\s+<([^>]+)>',  # replace all domain <domain>
        ]
        
        for pattern in old_url_patterns:
            old_match = re.search(pattern, prompt, re.IGNORECASE)
            if old_match:
                variables['old_url'] = old_match.group(1)
                break
        
        # Extract domain pattern (like "/en/", "/uk/", etc.)
        domain_match = re.search(r'domain\s+"([^"]+)"', prompt, re.IGNORECASE)
        if domain_match:
            variables['old_domain'] = domain_match.group(1)
            
        # Extract new domain if replacing domains
        new_domain_match = re.search(r'to\s+"([^"]+)".*domain', prompt, re.IGNORECASE)
        if new_domain_match:
            variables['new_domain'] = new_domain_match.group(1)
        
        # Detect operation type
        if 'replace all' in prompt.lower():
            variables['operation'] = 'replace_all'
        elif 'change link in' in prompt.lower():
            variables['operation'] = 'change_specific'
        elif 'domain' in prompt.lower():
            variables['operation'] = 'replace_domain'
        
        return variables


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
            # Check authentication status BEFORE execution
            auth_status = st.empty()
            auth_found = False
            
            try:
                import time
                
                # Check for IDSDK OAuth Token (PREFERRED)
                if hasattr(st, 'secrets') and 'AUTODESK_ACCESS_TOKEN' in st.secrets:
                    token = st.secrets['AUTODESK_ACCESS_TOKEN']
                    token_expires_at = st.secrets.get('AUTODESK_TOKEN_EXPIRES_AT', 0)
                    
                    if token_expires_at and time.time() < token_expires_at:
                        expires_in = int(token_expires_at - time.time())
                        expires_min = expires_in // 60
                        auth_status.success(f"🔐 Authentication: IDSDK OAuth Token (expires in {expires_min} minutes)")
                        auth_found = True
                    else:
                        auth_status.error("❌ Authentication: OAuth token EXPIRED!")
                        st.warning("⚠️ Token expired. Please re-authenticate.")
                        st.info("💡 Run: `python3 autodesk_idsdk_login.py`")
                
                # Check for Session Cookies (FALLBACK)
                elif hasattr(st, 'secrets') and 'DRAFTR_COOKIES' in st.secrets:
                    cookies_json = st.secrets['DRAFTR_COOKIES']
                    cookies = json.loads(cookies_json)
                    auth_status.warning(f"🍪 Authentication: {len(cookies)} session cookies (consider upgrading to IDSDK)")
                    auth_found = True
                
                # No authentication
                if not auth_found:
                    auth_status.error("❌ Authentication: NOT CONFIGURED!")
                    st.warning("⚠️ The automation will run without authentication. Draftr requires login!")
                    with st.expander("📋 Setup Authentication (Choose One)"):
                        st.markdown("""
                        **Option 1: IDSDK OAuth Token (RECOMMENDED)**
                        - More secure (OAuth 2.0)
                        - Auto-refreshing
                        - SSO/2FA support
                        ```bash
                        python3 autodesk_idsdk_login.py
                        # Copy output to secrets
                        ```
                        
                        **Option 2: Session Cookies (FALLBACK)**
                        - Less secure
                        - Manual recapture needed
                        ```bash
                        node capture-cookies.js
                        # Add DRAFTR_COOKIES to secrets
                        ```
                        """)
                        
            except Exception as e:
                auth_status.error(f"❌ Authentication: Error - {str(e)}")
            
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
                        
                        # Debug: Show raw result
                        with st.expander("🔍 Debug: Raw Result"):
                            st.json(result)
                        
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
                            
                            # Show output (stdout)
                            if result.get('output'):
                                st.subheader("📋 Execution Log")
                                st.code(result['output'], language='text')
                            
                            # Show any warnings/errors (stderr) even on success
                            if result.get('error'):
                                with st.expander("⚠️ Warnings & Debug Info"):
                                    st.code(result['error'], language='text')
                        else:
                            st.error("❌ Automation failed")
                            
                            # Show error details (stderr)
                            if result.get('error'):
                                st.subheader("🐛 Error Details")
                                st.code(result['error'], language='text')
                            
                            # Show any output (stdout) even on failure
                            if result.get('output'):
                                with st.expander("📋 Execution Log"):
                                    st.code(result['output'], language='text')
        
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
        
        # Check dependencies
        deps = check_dependencies()
        
        # Check API credentials
        api_type = os.getenv("OPENAI_API_TYPE", "").lower()
        if api_type == "azure_ad":
            has_creds = all([os.getenv("AZURE_TENANT_ID"), os.getenv("AZURE_CLIENT_ID"), os.getenv("AZURE_CLIENT_SECRET")])
        else:
            has_creds = bool(os.getenv("OPENAI_API_KEY"))
        
        api_status = "🟢 AI Connected" if has_creds else "🟡 Fallback Mode"
        st.write(f"**AI Service:** {api_status}")
        
        # NPM/Playwright status
        npm_status = "🟢 Installed" if deps['npm_packages'] else "🟡 Missing"
        playwright_status = "🟢 Ready" if deps['playwright'] else "🟡 Missing"
        st.write(f"**NPM Packages:** {npm_status}")
        st.write(f"**Playwright:** {playwright_status}")
        
        # Add verification details in expander
        with st.expander("🔍 Verify Installation Details"):
            node_modules_path = Path(__file__).parent / 'node_modules'
            mcp_sdk_path = node_modules_path / '@modelcontextprotocol' / 'sdk'
            playwright_marker = Path(__file__).parent / '.playwright_installed'
            
            st.markdown("**File Checks:**")
            st.text(f"{'✅' if node_modules_path.exists() else '❌'} node_modules/ directory")
            st.text(f"{'✅' if mcp_sdk_path.exists() else '❌'} MCP SDK installed")
            st.text(f"{'✅' if playwright_marker.exists() else '❌'} .playwright_installed marker")
            
            if node_modules_path.exists():
                try:
                    pkg_count = len([d for d in node_modules_path.iterdir() if d.is_dir()])
                    st.text(f"📦 {pkg_count} npm packages found")
                except:
                    pass
            
            st.markdown("**Paths:**")
            st.code(f"MCP SDK: {mcp_sdk_path}", language=None)
            st.code(f"Playwright: {playwright_marker}", language=None)
        
        # Show setup button if dependencies missing OR force reinstall option
        col_inst1, col_inst2 = st.columns([2, 1])
        
        with col_inst1:
            if not deps['npm_packages'] or not deps['playwright']:
                if st.button("🔧 Install Dependencies", type="primary", use_container_width=True):
                    with st.spinner("Installing dependencies... This may take 3-5 minutes..."):
                        result = install_dependencies_if_needed()
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        
                        # Show installation details
                        if result['details']:
                            with st.expander("📋 Installation Details", expanded=True):
                                for component, status in result['details'].items():
                                    st.write(f"**{component.replace('_', ' ').title()}:** {status}")
                        
                        # Show installation logs
                        if result['logs']:
                            with st.expander("📜 Installation Log"):
                                for log_line in result['logs']:
                                    st.text(log_line)
                        
                        # Verify and show updated status
                        st.info("🔄 Refreshing app to update status...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                        
                        # Show what failed
                        if result['logs']:
                            with st.expander("📜 Error Details", expanded=True):
                                for log_line in result['logs']:
                                    st.text(log_line)
                        
                        st.warning("💡 Try refreshing the page or check system requirements.")
        
        with col_inst2:
            # Force reinstall option (delete marker file)
            if deps['playwright']:
                if st.button("🔄 Force Reinstall", use_container_width=True):
                    playwright_marker = Path(__file__).parent / '.playwright_installed'
                    if playwright_marker.exists():
                        playwright_marker.unlink()
                        st.success("✅ Marker deleted. Click 'Install Dependencies' to reinstall.")
                        st.rerun()
        
        # Check browser configuration
        with st.expander("🔍 Browser Configuration Check"):
            st.info("Using Chrome via channel (system Chrome installation)")
            st.text("Browser: Google Chrome")
            st.text("Channel: chrome")
            st.text("Mode: Headless")
            
            # Check if playwright marker exists
            playwright_marker = Path(__file__).parent / '.playwright_installed'
            if playwright_marker.exists():
                st.success("✅ Playwright Chrome configured!")
            else:
                st.error("❌ Playwright not installed")
                st.warning("Click 'Install Dependencies' or 'Force Reinstall' above.")
        
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


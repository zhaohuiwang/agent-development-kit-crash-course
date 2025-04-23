from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from tools import get_cpu_info, get_disk_info, get_memory_info

load_dotenv()

# Pattern: Parallel Fan-Out/Gather and Synthesize

# --- Constants ---
APP_NAME = "system_monitor_app"
USER_ID = "aiwithbrandon"
SESSION_ID = "system_info_session_01"
GEMINI_MODEL = "gemini-2.0-flash"

# --- 1. Define Parallel Sub-Agents for System Information Gathering ---

# CPU Information Agent
cpu_info_agent = LlmAgent(
    name="CpuInfoAgent",
    model=GEMINI_MODEL,
    instruction="""You are a CPU Information Agent.
    
    When asked for system information, you should:
    1. Use the 'get_cpu_info' tool to gather CPU data
    2. Analyze the returned dictionary data
    3. Format this information into a concise, clear section of a system report
    
    The tool will return a dictionary with:
    - result: Core CPU information
    - stats: Key statistical data about CPU usage
    - additional_info: Context about the data collection
    
    Format your response as a well-structured report section with:
    - CPU core information (physical vs logical)
    - CPU usage statistics
    - Any performance concerns (high usage > 80%)
    
    IMPORTANT: You MUST call the get_cpu_info tool. Do not make up information.
    """,
    description="Gathers and analyzes CPU information",
    tools=[get_cpu_info],
    output_key="cpu_info",
)

# Memory Information Agent
memory_info_agent = LlmAgent(
    name="MemoryInfoAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Memory Information Agent.
    
    When asked for system information, you should:
    1. Use the 'get_memory_info' tool to gather memory data
    2. Analyze the returned dictionary data
    3. Format this information into a concise, clear section of a system report
    
    The tool will return a dictionary with:
    - result: Core memory information
    - stats: Key statistical data about memory usage
    - additional_info: Context about the data collection
    
    Format your response as a well-structured report section with:
    - Total and available memory
    - Memory usage statistics
    - Swap memory information
    - Any performance concerns (high usage > 80%)
    
    IMPORTANT: You MUST call the get_memory_info tool. Do not make up information.
    """,
    description="Gathers and analyzes memory information",
    tools=[get_memory_info],
    output_key="memory_info",
)

# Disk Information Agent
disk_info_agent = LlmAgent(
    name="DiskInfoAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Disk Information Agent.
    
    When asked for system information, you should:
    1. Use the 'get_disk_info' tool to gather disk data
    2. Analyze the returned dictionary data
    3. Format this information into a concise, clear section of a system report
    
    The tool will return a dictionary with:
    - result: Core disk information including partitions
    - stats: Key statistical data about storage usage
    - additional_info: Context about the data collection
    
    Format your response as a well-structured report section with:
    - Partition information
    - Storage capacity and usage
    - Any storage concerns (high usage > 85%)
    
    IMPORTANT: You MUST call the get_disk_info tool. Do not make up information.
    """,
    description="Gathers and analyzes disk information",
    tools=[get_disk_info],
    output_key="disk_info",
)

# --- 2. Create Parallel Agent to gather information concurrently ---
system_info_gatherer = ParallelAgent(
    name="SystemInfoGatherer",
    sub_agents=[cpu_info_agent, memory_info_agent, disk_info_agent],
)

# --- 3. Define Synthesizer Agent to combine all information ---
system_report_synthesizer = LlmAgent(
    name="SystemReportSynthesizer",
    model=GEMINI_MODEL,
    instruction="""You are a System Report Synthesizer.
    
    Your task is to create a comprehensive system health report by combining information from:
    - CPU information (from state key 'cpu_info')
    - Memory information (from state key 'memory_info')
    - Disk information (from state key 'disk_info')
    
    Create a well-formatted report with:
    1. An executive summary at the top with overall system health status
    2. Sections for each component with their respective information
    3. Recommendations based on any concerning metrics
    
    Use markdown formatting to make the report readable and professional.
    Highlight any concerning values and provide practical recommendations.
    """,
    description="Synthesizes all system information into a comprehensive report",
)

# --- 4. Create Sequential Pipeline to gather info in parallel, then synthesize ---
system_monitor_pipeline = SequentialAgent(
    name="SystemMonitorPipeline",
    sub_agents=[system_info_gatherer, system_report_synthesizer],
)

# --- 5. Setup Session and Runner ---
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=system_monitor_pipeline, app_name=APP_NAME, session_service=session_service
)

# --- 6. Process System Information Request ---
print("Starting system monitoring...")
user_query = "Please provide a comprehensive health report of my system. Analyze CPU, memory, and disk usage, and give me recommendations."

content = types.Content(role="user", parts=[types.Part(text=user_query)])
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

# Process and display results
for event in events:
    if event.is_final_response() and event.content and event.content.parts:
        final_response = event.content.parts[0].text
        print("\n=== SYSTEM HEALTH REPORT ===")
        print(final_response)
        print("================================\n")

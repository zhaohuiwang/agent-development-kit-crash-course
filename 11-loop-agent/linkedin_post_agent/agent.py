"""
LinkedIn Post Generator Root Agent

This module defines the root agent for the LinkedIn post generation application.
It uses a loop agent for iterative refinement of LinkedIn posts.
"""

from google.adk.agents import LoopAgent

from .subagents.post_generator import post_generator
from .subagents.post_reviewer import post_reviewer

# Create the LinkedIn Post Loop Agent
linkedin_post_loop = LoopAgent(
    name="LinkedInPostRefinementLoop",
    max_iterations=10,
    sub_agents=[
        post_generator,
        post_reviewer,
    ],
    description="Iteratively generates and refines a LinkedIn post until quality requirements are met",
)

# Define the root agent for ADK web compatibility
root_agent = linkedin_post_loop

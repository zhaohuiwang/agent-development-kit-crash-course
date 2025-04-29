# LinkedIn Post Generator Loop Agent

This example demonstrates the use of a Loop Agent pattern in the Agent Development Kit (ADK) to iteratively generate and refine a LinkedIn post.

## Overview

The LinkedIn Post Generator uses a loop pattern to continuously refine content until quality requirements are met. It demonstrates:

1. **Iterative Content Generation**: Using a loop to repeatedly refine content
2. **Automatic Quality Checking**: Validating content against specific criteria
3. **Feedback-Driven Refinement**: Improving content based on specific feedback
4. **Loop Exit Tool**: Using a tool to terminate the loop when quality requirements are met

## Architecture

The system is composed of the following components:

### Main Loop Agent

`LinkedInPostRefinementLoop` - A LoopAgent that orchestrates the iterative post refinement process by running two sub-agents in sequence for up to 10 iterations.

### Sub-Agents

1. **Post Generator** (`LinkedInPostGenerator`) - Generates or refines LinkedIn posts based on feedback
2. **Post Reviewer** (`PostReviewer`) - Reviews posts for quality and provides feedback or exits the loop when quality requirements are met

### Tools

1. **Character Counter** - Validates post length against requirements
2. **Exit Loop** - Terminates the loop when all quality criteria are satisfied

## Loop Control with Exit Tool

A key design pattern in this example is the use of an `exit_loop` tool to control when the loop terminates. The tool works by:

1. Being called by the Post Reviewer agent when it determines the post meets all quality criteria
2. Setting `tool_context.actions.escalate = True`, which signals to the LoopAgent that it should stop iterating
3. Providing a clean way to separate the review logic from the loop control logic

This approach is recommended in the ADK documentation as one of the effective ways to manage loop termination. Rather than relying solely on the `max_iterations` parameter (which serves as a safety limit), we implement intelligent termination when quality goals are achieved.

The alternative approaches would be:
- Using a separate agent to return a "STOP" signal (as we originally implemented with status_checker)
- Relying entirely on the max_iterations parameter
- Implementing external logic to make stop decisions

The tool-based approach we've chosen provides a cleaner, more direct method for controlling the loop flow.

## Usage

To run this example:

```bash
cd 11-loop-agent
adk web
```

Then in the web interface, enter a prompt like:
"Generate a LinkedIn post about what I've learned from @aiwithbrandon's Agent Development Kit tutorial."

The system will:
1. Generate an initial LinkedIn post
2. Review the post for quality and compliance with requirements
3. If the post needs improvement, provide feedback and regenerate
4. Continue this process until a satisfactory post is created or max iterations reached
5. Return the final post

## Example Input

```
Generate a LinkedIn post about what I've learned from @aiwithbrandon's Agent Development Kit tutorial.
```

## Loop Termination

The loop terminates in one of two ways:
1. When the post meets all quality requirements (via the exit_loop tool)
2. After reaching the maximum number of iterations (10)

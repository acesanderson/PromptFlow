"""
Defining the PromptFlow object + base prompts.

The PromptFlow chain:
- takes a natural language description of a desired workflow
- converts it to a ProcessDescription (a more detailed, structured description)
- converts the ProcessDescription to a PromptFlow object (a finite state machine)

The story
- You are a colleague who needs a process mapped out.
- a Workflow Analyst receives uour natural language description of a workflow
- the PromptFlow Architect designs a PromptFlow object
"""

# Import the necessary libraries
# ----------------------------------------

from pydantic import BaseModel
from typing import List
import json

# Create an example process for the chain. This is from Sophie.
# ----------------------------------------

natural_language_description = """
I want to generate 100 text-based courses.

**Here is how the average course will be structured:**
- **Total Chapters**: 4
- **Sections per Chapter**: 3-4 sections
- **Words per Section**: ~1500 words
- **Total Sections**: ~12-15 sections across the entire course
- **Total Word Count**: 18,000 - 22,500 words per course
This structure ensures each course is thorough yet broken down into manageable segments that facilitate comprehension and retention, aligned with typical learning and attention spans.

Their library will address the following audiences:
- people managers
- people who want to start (or pivot to) a new career.
- people who want to improve in their current career.

Sophie Inc.'s business model will be to sell to large companies, so they will focus on a mix of business and technology skills. Their library will have the following segments:
- Leadership and Management (examples: becoming a manager, organizational leadership, strategic planning): 20 courses
- Professional Development (examples: interpersonal communication, negotiation, executive presence): 15 courses
- Business Functions (examples: Marketing, Sales, Finance): 15 courses
- Business software (examples: Excel, SAP, Salesforce): 10 courses
- Software development (examples: Java development, web development. machine learning) 20 courses
- IT administration (examples: linux administration, database administration, network engineering) 20 courses
""".strip()

# Define our personas: workflow analyst, and promptflow architect.
# ----------------------------------------

persona_workflow_analyst = """

You are a Workflow Analyst at a large company, and your primary responsibility is to analyze and understand business processes or challenges and create a structured processDescription object that captures all the essential information about the workflow.
You will receive a detailed description of a business process or problem as plain text. Your task is to carefully read through the description, identify the key components, and extract the necessary information to populate the processDescription object.
The processDescription object should include the following properties:

processDescription: A concise summary of the overall process or challenge.
keyObjectives: A list of the main objectives or goals of the process.
participantsAndRoles: A list of the individuals or roles involved in the process and their responsibilities.
decisionPoints: A list of critical decision points within the process where choices or approvals are required.
challengesOrIssues: A list of the main challenges, bottlenecks, or issues encountered during the process.
desiredOutcomes: A list of the desired outcomes or results expected upon completing the process.
additionalInformation: Any additional relevant information that helps in understanding the process better.

Your output should strictly adhere to the following JSON schema:
{{processDescription_schema}}

Ensure that all required properties are populated based on the information provided in the input description. If any required information is missing or unclear, make reasonable assumptions or inferences based on the context, but avoid introducing unsupported claims.
"""

persona_promptflow_architect = """
You are a systems architect at a large company, and your full time job is to convert detailed descriptions of workflows into PromptFlow objects.

A PromptFlow is a finite state machine, rendered in JSON. A PromptFlow, when given to a machine, can be rendered into the following:
- a dialogue flow for customer service chatbots
- manufacturing instructions for a factory
- a software development pipeline
- a data analysis pipeline (i.e. data cleaning, transformation, and analysis)

You are given a detailed description of a business process.

Based on your analysis, you translate the workflow into a PromptFlow object. PromptFlow utilizes a finite state machine (FSM) structure, represented in JSON format.

Each state in the FSM corresponds to a specific stage in the workflow. You define transitions between states based on decision points and potential outcomes.

Your answers should always be a structured PromptFlow json object, with no extra text or ornaments.

Here's the schema for a PromptFlow object.

{{PromptFlow_schema}}
"""

# define our prompts: processDescription and PromptFlow
# ----------------------------------------

process_description_prompt = """
Create processDescription object

A colleague has come to you with this description of what they want modeled:

==========
{{natural_language_description}}
==========

As always, please strictly follow your instructions to generate a processDescription json object. Please ensure that your response adheres to the processDescription JSON schema.
"""

promptflow_prompt = """

You've received a request to generate a PromptFlow object. Here's the description you've been given:

{{processDescription}}

As always, please strictly follow your instructions to generate a PromptFlow json object. Please ensure that your response adheres to the PromptFlow json schema.
"""

# Now, our schemas for the processDescription and PromptFlow objects.
# ----------------------------------------

PromptFlow_schema = """
{
  "workflowName": "Name of the workflow",
  "initialState": "Starting point of the workflow",
  "statesDescription": [
	{
	  "state": "State 1",
	  "description": "Description of State 1"
	},
	{
	  "state": "State 2",
	  "description": "Description of State 2"
	}
  ],
  "transitions": [
	{
	  "currentState": "State 1",
	  "event": "Event triggering transition from State 1 to State 2",
	  "nextState": "State 2"
	},
	{
	  "currentState": "State 2",
	  "event": "Event triggering transition from State 2 to Final State",
	  "nextState": "Final State"
	}
  ],
  "finalState": "Ending point or final state of the workflow"
}
"""

processDiscussion_schema = """
{
  "type": "object",
  "properties": {
	"processDescription": {
	  "type": "string",
	  "description": "A detailed narrative of the overall process or challenge."
	},
	"keyObjectives": {
	  "type": "array",
	  "items": {
		"type": "string"
	  },
	  "description": "The main objectives or goals of the process."
	},
	"participantsAndRoles": {
	  "type": "array",
	  "items": {
		"type": "string"
	  },
	  "description": "The individuals involved in the process and their roles."
	},
	"decisionPoints": {
	  "type": "array",
	  "items": {
		"type": "string"
	  },
	  "description": "Critical decision points within the process."
	},
	"challengesOrIssues": {
	  "type": "array",
	  "items": {
		"type": "string"
	  },
	  "description": "The main challenges or issues encountered during the process."
	},
	"desiredOutcomes": {
	  "type": "array",
	  "items": {
		"type": "string"
	  },
	  "description": "The desired outcomes upon completing the process."
	},
	"additionalInformation": {
	  "type": "string",
	  "description": "Any additional information that might help in understanding the process better."
	}
  },
  "required": [
	"processDescription",
	"keyObjectives",
	"participantsAndRoles",
	"decisionPoints",
	"challengesOrIssues",
	"desiredOutcomes"
  ]
}
"""

# Define Pydantic models for the processDescription and PromptFlow objects.
# ----------------------------------------

class ProcessDescription(BaseModel):
	"""Model for the ProcessDescription object."""
	processDescription: str
	keyObjectives: List[str]
	participantsAndRoles: List[str]
	decisionPoints: List[str]
	challengesOrIssues: List[str]
	desiredOutcomes: List[str]
	additionalInformation: str = None  # Optional field, not included in 'required'

class StateDescription(BaseModel):
	"""Model for the StateDescription object."""
	state: str
	description: str

class Transition(BaseModel):
	"""Model for the Transition object."""
	currentState: str
	event: str
	nextState: str

class PromptFlow(BaseModel):
	"""Model for the PromptFlow object."""
	workflowName: str
	initialState: str
	statesDescription: List[StateDescription]
	transitions: List[Transition]
	finalState: str

# Our functions
# ----------------------------------------

def convert_json_to_promptflow(json_data: dict) -> PromptFlow:
	"""Converts a JSON object to a PromptFlow object."""
	return PromptFlow(**json_data)

def generate_mermaid_diagram(prompt_flow: PromptFlow) -> str:
	"""
	Generates a Mermaid diagram string for a given PromptFlow object.

	Args:
	prompt_flow (PromptFlow): The PromptFlow object to visualize.

	Returns:
	str: A string containing the Mermaid diagram.
	"""
	# Start the Mermaid diagram
	diagram = "graph TD\n"
	# Add states with descriptions as nodes
	for state in prompt_flow.statesDescription:
		# Each state node in Mermaid can have a text label which might include a description
		diagram += f'    {state.state}("{state.state}: {state.description}")\n'
	# Define transitions
	for transition in prompt_flow.transitions:
		# Each transition in Mermaid is represented as an edge between nodes
		line = f'    {transition.currentState} -->|{transition.event}| {transition.nextState}'
		diagram += line + '\n'
	# Optionally, add a special style for the initial and final states
	diagram += f'    style {prompt_flow.initialState} fill:#f9f,stroke:#333,stroke-width:4px\n'
	diagram += f'    style {prompt_flow.finalState} fill:#ccf,stroke:#f66,stroke-width:2px\n'
	return diagram

# Our Chain
# ----------------------------------------

example_prompt_flow = """
{
  "workflowName": "Conversational AI",
  "initialState": "human_input",
  "statesDescription": [
	{
	  "state": "human_input",
	  "description": "Initial state where the user provides input and has command options."
	},
	{
	  "state": "machine_evaluates_human_input",
	  "description": "The machine evaluates the human input and decides the next action."
	},
	{
	  "state": "machine_queries_database",
	  "description": "The machine queries the database for the requested information."
	},
	{
	  "state": "machine_receives_database_query",
	  "description": "The machine receives the database query result and responds to the human."
	}
  ],
  "transitions": [
	{
	  "currentState": "human_input",
	  "event": "User provides input",
	  "nextState": "machine_evaluates_human_input"
	},
	{
	  "currentState": "machine_evaluates_human_input",
	  "event": "Action: Search_Courses",
	  "nextState": "machine_queries_database"
	},
	{
	  "currentState": "machine_evaluates_human_input",
	  "event": "Action: Respond_To_Human",
	  "nextState": "human_input"
	},
	{
	  "currentState": "machine_evaluates_human_input",
	  "event": "Action: No_Action",
	  "nextState": "human_input"
	},
	{
	  "currentState": "machine_queries_database",
	  "event": "Database query initiated",
	  "nextState": "machine_receives_database_query"
	},
	{
	  "currentState": "machine_receives_database_query",
	  "event": "Database query result received",
	  "nextState": "human_input"
	}
  ],
  "finalState": "process_complete"
}
"""

if __name__ == "__main__":
	# Convert the example JSON to a PromptFlow object
	prompt_flow = convert_json_to_promptflow(json.loads(example_prompt_flow))
	# Generate a Mermaid diagram from the PromptFlow object
	mermaid_diagram = generate_mermaid_diagram(prompt_flow)
	# Print the Mermaid diagram
	print(mermaid_diagram)

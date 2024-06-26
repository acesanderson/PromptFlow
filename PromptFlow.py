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

from Chain import Prompt, Chain, Model, Parser
from pydantic import BaseModel
from typing import List, Union				# Union allows for multiple possible types
import json

# Anthropic excels at these sorts of tasks, and Claude Sonnet 3.5 is the strongest model released as of 6/23.
preferred_model = "claude" 

complex_mermaid_example = """
graph TD
    ProjectInitiation("Project Initiation: Set up project teams, define goals, and establish timelines")
    StakeholderReview("Stakeholder Review: Get approval on project scope and objectives")
    CoursePlanning("Course Planning: Define course categories, topics, and audience segments")
    ContentCreation("Content Creation: Write and structure course material")
    ExpertReview("Expert Review: Subject matter experts review content")
    EditingQA("Editing and Quality Assurance")
    FinalReview("Final Review: Project managers conduct final review")
    SalesPreparation("Sales Preparation: Brief sales team")
    CourseFinalization("Course Finalization: Prepare for delivery")
    ClientFeedback("Client Feedback: Gather and analyze client responses")
    RevisionPlanning("Revision Planning: Plan updates based on feedback")

    ProjectInitiation -->|Project setup complete| StakeholderReview
    StakeholderReview -->|Approved| CoursePlanning
    StakeholderReview -->|Revisions needed| ProjectInitiation
    CoursePlanning -->|Course outlines ready| ContentCreation
    ContentCreation -->|Initial draft complete| ExpertReview
    ExpertReview -->|Major changes needed| ContentCreation
    ExpertReview -->|Minor changes or approved| EditingQA
    EditingQA -->|Quality standards not met| ContentCreation
    EditingQA -->|Editing complete| FinalReview
    FinalReview -->|Changes required| EditingQA
    FinalReview -->|Approved| SalesPreparation
    SalesPreparation -->|Sales team briefed| CourseFinalization
    CourseFinalization -->|Courses launched| ClientFeedback
    ClientFeedback -->|Significant updates needed| RevisionPlanning
    ClientFeedback -->|Minor updates needed| EditingQA
    RevisionPlanning -->|Revision plan approved| CoursePlanning

    subgraph "Quality Control Loop"
        ExpertReview
        EditingQA
        FinalReview
    end

    subgraph "Collaboration Loop"
        ContentCreation
        ExpertReview
        EditingQA
    end

    subgraph "Continuous Improvement Loop"
        ClientFeedback
        RevisionPlanning
        CoursePlanning
    end

    style ProjectInitiation fill:#f9f,stroke:#333,stroke-width:4px
    style CourseFinalization fill:#ccf,stroke:#f66,stroke-width:2px
    style ClientFeedback fill:#ffc,stroke:#f66,stroke-width:2px
"""

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
""".strip()

persona_promptflow_architect = """
You are a systems architect at a large company, specializing in creating complex, non-linear PromptFlow objects from detailed workflow descriptions. Your goal is to design sophisticated finite state machines that accurately represent real-world processes, including their intricacies and iterative nature.

A PromptFlow is a finite state machine rendered in JSON, capable of representing various workflows such as:
- Dialogue flows for customer service chatbots
- Manufacturing instructions for a factory
- Software development pipelines
- Data analysis pipelines (i.e., data cleaning, transformation, and analysis)
- Recipes for cooking complex dishes
- Patient diagnosises and treatment plans in healthcare
- Order fulfillment processes
- Contract negotiation and approval
- Online course creation and delivery

Your task:
1. Analyze the given detailed description of a business process.
2. Translate the workflow into a PromptFlow object, utilizing a complex finite state machine (FSM) structure in JSON format.
3. Ensure the PromptFlow includes:
   - Multiple pathways and decision points
   - Feedback loops and iterative processes
   - Parallel states or concurrent processing where applicable
   - Quality assurance and review steps
   - Self-review and external review processes

Guidelines for creating complex PromptFlows:
- Include conditional branching based on various outcomes or decisions.
- Implement loops for repetitive tasks or refinement processes.
- Incorporate parallel states for simultaneous operations.
- Add review stages that can loop back to previous states for improvement.
- Consider error handling states and transitions.
- Implement "wait" states for processes that require external input or time delays.

Your response should be a structured PromptFlow JSON object without any additional text or explanations. Aim to create a sophisticated FSM that accurately represents the complexities of real-world processes.

Here's the enhanced schema for a PromptFlow object:

{
  "workflowName": "Name of the workflow",
  "initialState": "Starting point of the workflow",
  "statesDescription": [
    {
      "state": "State 1",
      "description": "Description of State 1",
      "type": "process/decision/review/parallel"
    },
    {
      "state": "State 2",
      "description": "Description of State 2",
      "type": "process/decision/review/parallel"
    }
  ],
  "transitions": [
    {
      "currentState": "State 1",
      "event": "Event triggering transition",
      "nextState": "State 2",
      "condition": "Optional condition for transition"
    },
    {
      "currentState": "State 2",
      "event": "Event triggering transition",
      "nextState": "State 1",
      "condition": "Optional condition for transition"
    }
  ],
  "parallelStates": [
    {
      "parentState": "Parallel Parent State",
      "childStates": ["Child State 1", "Child State 2"]
    }
  ],
  "finalState": "Ending point or final state of the workflow"
}

Remember to create PromptFlows that reflect the complexity and non-linear nature of real-world processes, including loops, parallel processing, and multiple decision points -- where it makes sense.

Most importantly, the complexity should serve a purpose, whether it's increasing safety, or improving quality, seeking consensus, etc.
""".strip()

# define our prompts: processDescription and PromptFlow
# ----------------------------------------

process_description_prompt = """
You've received a request to generate a processDescription object.

A colleague has come to you with this description of what they want modeled:

==========
{{natural_language_description}}
==========

As always, please strictly follow your instructions to generate a processDescription json object. Please ensure that your response adheres to the processDescription JSON schema.
""".strip()

promptflow_prompt = """
You've received a request to generate a PromptFlow object. Here's the process description you've been given:

{{processDescription}}

As always, please strictly follow your instructions to generate a PromptFlow json object. Please ensure that your response adheres to the PromptFlow json schema.
""".strip()

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

processDescription_schema = """
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

def pretty(structured_data: Union[str, PromptFlow, ProcessDescription, dict]) -> str:
	"""
	Takes structured data (string, PromptFlow object, or dictionary) and returns a pretty-printed string representation.
	By definition, these are equivalent types for PromptFlow.
	"""
	if isinstance(structured_data, str):
		structured_data = json.loads(structured_data)
		structured_data = json.dumps(structured_data, indent=2)
		return structured_data
	elif isinstance(structured_data, BaseModel):
		return json.dumps(structured_data.__dict__, indent=2)
	elif isinstance(structured_data, dict):
		return json.dumps(structured_data, indent=2)
	else:
		raise ValueError("Unsupported type for pretty printing. Supported types: str, PromptFlow, ProcessDescription, dict")

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

# Create Chains
# ----------------------------------------

def analyze_workflow_description(natural_language_description: str) -> ProcessDescription:
	"""Analyzes a natural language description of a workflow and generates a ProcessDescription object."""
	messages = Chain.create_messages(system_prompt = persona_workflow_analyst, input_variables = {'processDescription_schema': processDescription_schema})
	prompt = Prompt(process_description_prompt)
	model = Model(preferred_model)
	parser = Parser("json")
	chain = Chain(prompt, model, parser)
	response = chain.run(messages = messages, input_variables = natural_language_description)
	process_description_obj = ProcessDescription(**response.content)	
	return process_description_obj

def generate_promptflow(process_description: ProcessDescription) -> PromptFlow:
	"""Generates a PromptFlow object based on a ProcessDescription object."""
	messages = Chain.create_messages(system_prompt = persona_promptflow_architect, input_variables = {'PromptFlow_schema': PromptFlow_schema})
	prompt = Prompt(promptflow_prompt)
	model = Model(preferred_model)
	parser = Parser("json")
	chain = Chain(prompt, model, parser)
	process_description_string = json.dumps(process_description.__dict__)
	response = chain.run(messages = messages, input = process_description_string)
	promptflow_object = PromptFlow(**response.content)
	return promptflow_object

# Main function
# ----------------------------------------

def main():
	# Analyze the natural language description of the workflow
	print("Analyzing the natural language description of the workflow...")
	process_description = analyze_workflow_description(natural_language_description)
	# Generate a PromptFlow object based on the ProcessDescription
	print("Our architect is now generating a PromptFlow object...")
	promptflow_object = generate_promptflow(process_description)
	# Show results
	print("\n=====================================================")
	print("Results")
	print("=====================================================\n")
	try:
		print(pretty(promptflow_object))
	except Exception as e:
		print("Error printing the PromptFlow object.")
		print(e)
	print("\n=====================================================")
	print("Mermaid Diagram")
	print("=====================================================\n")
	print(generate_mermaid_diagram(promptflow_object))

if __name__ == "__main__":
	main()

# a completed result for testing purposes
# process_description = ProcessDescription(**{'processDescription': 'The process involves generating 100 text-based courses for a company called Sophie Inc. These courses will be structured consistently, with each course containing approximately 4 chapters, 12-15 sections, and a total word count of 18,000-22,500 words. The courses will cover various topics in business and technology, targeting different professional audiences.', 'keyObjectives': ['Generate 100 text-based courses', 'Maintain consistent course structure across all courses', 'Cover a range of business and technology topics', 'Target specific professional audiences', 'Create content suitable for sale to large companies'], 'participantsAndRoles': ['Content creators: Responsible for writing and structuring the course material', 'Subject matter experts: Provide expertise in specific business and technology areas', 'Editors: Review and refine the course content', 'Project managers: Oversee the course creation process and ensure consistency', 'Sales team: Sell the courses to large companies'], 'decisionPoints': ['Selection of specific topics within each course category', 'Allocation of courses across different segments (e.g., 20 for Leadership and Management)', 'Determining the exact number of sections per chapter (3-4)', 'Finalizing the word count for each section (~1500 words)', 'Choosing which large companies to target for sales'], 'challengesOrIssues': ['Maintaining consistency in quality and structure across 100 courses', 'Ensuring content relevance for different professional audiences', 'Balancing depth and breadth of topics within word count constraints', 'Keeping content up-to-date, especially for technology-related courses', 'Differentiating courses from existing online learning platforms'], 'desiredOutcomes': ['Create a comprehensive library of 100 high-quality, structured courses', 'Attract large companies as customers for the course library', 'Meet the learning needs of various professional audiences', 'Establish Sophie Inc. as a reputable provider of business and technology education', 'Generate revenue through course sales to large companies'], 'additionalInformation': "Sophie Inc.'s course library will be divided into six segments: Leadership and Management (20 courses), Professional Development (15 courses), Business Functions (15 courses), Business software (10 courses), Software development (20 courses), and IT administration (20 courses). The courses are designed to address the needs of people managers, career changers, and professionals seeking to improve in their current roles."})
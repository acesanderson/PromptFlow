"""
Experimenting with generating PromptFlow objects from the Publishing Philosophy that we generated in the Sophie Cannoli.
"""

from PromptFlow import request_prompt_flow, pretty
from pydantic import BaseModel
from Chain import Chain, Model, Prompt, Parser
from typing import List

natural_language_description = """
The company Sophie, Inc. creates text-based courses.
Their business model is to sell a subscription to a library of courses, and their target customer base is
large enterprises with upskilling needs.
The theory of value for their product is the following:
- large companies need to upskill their workforce to stay competitive
- basic to advanced training in business functions (like HR, Marketing, Sales, Finance, etc.) can improved
for the customers' bottom line as they adapt best practices.
- customers can retain their employees better if they provide training opportunities

The average Sophie, Inc. text-based course is 4 hours long, and purely text based.
The courses are aimed at foundational topics, like "Digital Marketing 101" or "Human Resources 101".

They will have three parts of their library:
- leadership and management courses
- soft skills courses (like Negotiation, Communication, Presentation Skills, etc.)
- business function courses
- technical skills courses (software development and IT)

They leverage SMEs to create the content, and have a team of instructional designers to create the course structure.
There is also a team of content writers, editors, QA specialists, and a managing editor.

We want a workflow that takes a course title as input and outputs a completed course.
""".strip()

"""
course_planning
SME_generation
- metaprompt
content_creation
- create TOC
- write the course
content_editing
- 
"""

# Prompts

course_planning_prompt = """
You are the managing editor for Sophie, Inc.
You will be having the team generate courses for the library.
First, take a look at the company objectives and the target customer base.

### Company objectives

The company Sophie, Inc. creates text-based courses.
Their business model is to sell a subscription to a library of courses, and their target customer base is
large enterprises with upskilling needs.
The theory of value for their product is the following:
- large companies need to upskill their workforce to stay competitive
- basic to advanced training in business functions (like HR, Marketing, Sales, Finance, etc.) can improved
for the customers' bottom line as they adapt best practices.
- customers can retain their employees better if they provide training opportunities

The average Sophie, Inc. text-based course is 4 hours long, and purely text based.
The courses are aimed at foundational topics, like "Digital Marketing 101" or "Human Resources 101".

They will have three parts of their library:
- leadership and management courses
- soft skills courses (like Negotiation, Communication, Presentation Skills, etc.)
- business function courses
- technical skills courses (software development and IT)

### Task

Please come up with a Course_List (a list of fifty-one courses) that you think would be valuable to the library.
For each Course, provide a title, a description of the audience, and the skills that should be covered.
""".strip()

SME_metaprompt = """
You are an expert prompt engineer specializing in educational content creation. Your task is to generate a system prompt for a subject matter expert (SME) who will be writing a course on the following topic:

Topic: {{topic}}
Course Title: {{title}}
Skills Covered: {{skills}}

Create a system prompt that achieves the following:

1. Define an ideal persona for the SME, including:
   - Relevant academic background
   - Years of experience in the field
   - Notable achievements or contributions
   - Teaching or mentoring experience

2. Outline best practices for course creation, including:
   - Structuring content for optimal learning
   - Engaging presentation techniques
   - Incorporating practical examples and case studies
   - Addressing diverse learning styles

3. Provide guidelines for ensuring course quality:
   - Accuracy and up-to-date information
   - Clarity and conciseness in explanations
   - Logical flow and progression of ideas
   - Appropriate depth and breadth of content

4. Suggest methods for incorporating the specified skills:
   - Integrating skill development throughout the course
   - Providing opportunities for practical application
   - Assessing skill acquisition

5. Emphasize the importance of:
   - Learner-centric approach
   - Inclusive and accessible content
   - Ethical considerations relevant to the field

Generate a comprehensive system prompt that incorporates these elements, tailored specifically to the given topic, title, and skills. The resulting prompt should guide the SME in creating a high-quality, engaging, and effective course.
""".strip()

class Course_Brief(BaseModel):
    title: str
    audience: str
    skills: str

class Course_Brief_List(BaseModel):
    course_briefs: List[Course_Brief]

def create_course_briefs() -> Course_Brief_List:
    """
    With no input, Managing Editor comes up with the catalog.
    """
    model = Model('gpt')
    prompt = Prompt(course_planning_prompt)
    parser = Parser(Course_Brief_List)
    chain = Chain(prompt, model, parser)
    response = chain.run()
    return response.content.course_briefs

if __name__ == "__main__":
    course_briefs = create_course_briefs()
    print(course_briefs)






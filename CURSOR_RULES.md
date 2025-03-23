# Cursor Rules for Agno Development

This document explains the Cursor rules enforced in this project to maintain consistent use of the Agno framework and proper documentation practices.

## Rules Overview

### 1. Agno Framework Required
- **Severity**: Error
- **Description**: All agent implementations must use the Agno framework
- **Pattern**: `(?!.*agno\.agent).*Agent\s*=.*`
- **Message**: Agent implementations must use the Agno framework. Import and use 'from agno.agent import Agent'.

This rule ensures that all agent implementations in the project use Agno's agent framework rather than implementing agents directly or using other frameworks.

### 2. Documentation Reference Required
- **Severity**: Warning
- **Description**: Reference to Agno documentation must be included in comments before implementing functionality
- **Pattern**: `(?!.*@see.*agno\.com).*def\s+.*\(.*\)\s*:`
- **Message**: Include a reference to Agno documentation before implementing any functionality. Use format: '@see: https://docs.agno.com/...'

This rule enforces documentation practices by requiring developers to reference the appropriate Agno documentation before implementing new functionality.

### 3. OpenAI Model Restriction
- **Severity**: Error  
- **Description**: Ensure OpenAI models are accessed through Agno's abstraction layer
- **Pattern**: `(?!.*agno\.models\.openai).*openai\..*completion.*create.*`
- **Message**: Direct usage of OpenAI API is not allowed. Use Agno's model abstraction: 'from agno.models.openai import OpenAIChat'

This rule prevents direct usage of the OpenAI API, ensuring that all interactions with OpenAI models go through Agno's abstraction layer.

### 4. Agent Configuration Standards
- **Severity**: Warning
- **Description**: All Agno agents must have proper description and configuration
- **Pattern**: `Agent\((?!.*description).*\)`
- **Message**: All Agno agents must include a description parameter that explains their purpose

This rule ensures that all Agno agents are properly documented with a description parameter that explains their purpose.

### 5. Execution Documentation
- **Severity**: Warning
- **Description**: Code that executes agent actions must reference documentation
- **Pattern**: `agent\.(?:get_response|run|print_response)\((?!.*#.*@doc).*\)`
- **Message**: Include a reference to Agno documentation in a comment before executing agent actions. Format: '# @doc: https://docs.agno.com/...'

This rule ensures that any code that executes agent actions includes a reference to the relevant Agno documentation.

### 6. No Version Constraints in Requirements
- **Severity**: Error
- **Description**: Ensure requirements.txt doesn't include version constraints
- **Pattern**: `^[^#].*[>=<~].*$`
- **Message**: Do not specify version constraints in requirements.txt to ensure using the latest package versions

This rule ensures that the requirements.txt file doesn't include version constraints, allowing the application to always use the latest package versions.

## Example Usage

### Correct Implementation:

```python
# @see: https://docs.agno.com/get-started/agents
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Proper agent initialization with description
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="This agent helps users with general inquiries about the Agno framework",
    markdown=True
)

# @doc: https://docs.agno.com/agents#run-method
response = agent.get_response("Tell me about Agno")
```

### Incorrect Implementation:

```python
import openai

# Missing Agno import and documentation reference
agent = CustomAgent(model="gpt-4")

# Direct OpenAI API usage instead of Agno abstraction
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Correct Requirements.txt:

```
# Core dependencies
fastapi
uvicorn[standard]
pydantic

# AI and NLP dependencies
openai
agno
```

### Incorrect Requirements.txt:

```
# Core dependencies
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.3.0
```

## Enforcement

These rules are enforced by the Cursor IDE and will generate warnings or errors when violated. The settings in `.cursor-rules.json` determine how these rules are applied:

- Rules run on file save
- Notifications are shown for rule violations
- Automatic fixes are not applied, requiring manual intervention

## Importance

Following these rules ensures:
1. Consistent use of the Agno framework across the project
2. Proper documentation and reference to official Agno resources
3. Abstraction of model providers through Agno's interface
4. Maintainable and well-documented code
5. Up-to-date dependencies by always using the latest package versions
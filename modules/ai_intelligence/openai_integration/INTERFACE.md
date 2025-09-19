# OpenAI Integration Module Interface

**Purpose**: This document defines the public API for the OpenAI Integration module within the ai_intelligence domain, ensuring compliance with WSP 11.

**Public API Definition**:
- **Function**: `run_openai_query(model: str, messages: list)`
  - **Parameter Specifications**: 
    - `model`: String, required. Specifies the OpenAI model to use (e.g., 'gpt-4').
    - `messages`: List of dictionaries, required. Contains the conversation history with roles and content.
  - **Return Value Documentation**: Returns a string response from the OpenAI API.
  - **Error Handling**: Raises an exception with details on API errors.
  - **Examples**: 
    ```javascript
    const response = await run_openai_query('gpt-4', [{ role: 'user', content: 'Say hello in pirate voice.' }]);
    console.log(response);
    ```

**Notes**:
- This interface will expand as the module progresses through development phases.


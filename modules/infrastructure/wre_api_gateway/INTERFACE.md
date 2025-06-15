# WRE API Gateway Interface

This document defines the OpenAPI 3.0 specification for the WRE API Gateway. This gateway serves as the secure bridge between the WRE's core logic and the Symbiotic Execution Layer (SEL), such as the Cursor IDE.

```yaml
openapi: 3.0.3
info:
  title: "WRE API Gateway"
  description: "The secure API bridge between the WRE's core and the Symbiotic Execution Layer (SEL)."
  version: "1.0.0"
servers:
  - url: "http://localhost:4141/v1"
    description: "Local WRE API Gateway"

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    Task:
      type: object
      required:
        - agent_id
        - action
        - payload
      properties:
        task_id:
          type: string
          format: uuid
          readOnly: true
        agent_id:
          type: string
          description: "The ID of the SEA or WRE module initiating the task."
          example: "CursorBotProxy"
        action:
          type: string
          description: "The specific action to be performed by the SEL."
          example: "scaffold_module"
        payload:
          type: object
          description: "Data required to perform the action."
          example:
            module_name: "rewards_engine"
            target_directory: "modules/gamification/"
            files:
              - "src/__init__.py"
              - "src/engine.py"
              - "tests/test_engine.py"
    Result:
      type: object
      required:
        - task_id
        - status
        - data
      properties:
        task_id:
          type: string
          format: uuid
        status:
          type: string
          enum: [success, failed]
        data:
          type: object
          description: "The output or result of the task execution."
    Event:
      type: object
      properties:
        event_type:
          type: string
          example: "sel.task.received"
        message:
          type: string
          example: "Task received and is being processed."
        timestamp:
          type: string
          format: date-time

security:
  - bearerAuth: []

paths:
  /tasks:
    post:
      summary: "Dispatch a new task to the SEL"
      description: "The WRE uses this endpoint to send a task to a proxied SEA."
      security:
        - bearerAuth: ["wre:dispatch"]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Task'
      responses:
        '202':
          description: "Task accepted for processing."
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

  /results:
    post:
      summary: "Submit a result from an SEA"
      description: "A proxied SEA uses this endpoint to return the result of a completed task."
      security:
        - bearerAuth: ["agent:submit"]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Result'
      responses:
        '200':
          description: "Result received and acknowledged."

  /events:
    get:
      summary: "Subscribe to an event stream"
      description: "The WRE can subscribe to this stream to receive real-time events from the SEL."
      security:
        - bearerAuth: ["wre:read"]
      responses:
        '200':
          description: "A stream of server-sent events."
          content:
            text/event-stream:
              schema:
                $ref: '#/components/schemas/Event'
``` 
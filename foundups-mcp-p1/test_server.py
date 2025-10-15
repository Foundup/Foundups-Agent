from fastmcp import FastMCP

app = FastMCP("Test MCP Server")

@app.tool()
def hello_world(name: str = "World") -> str:
    """A simple hello world tool for testing MCP integration."""
    return f"Hello, {name}!"

@app.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    pass

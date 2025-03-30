import math
import logging

logger = logging.getLogger(__name__)

def calculate_dynamic_delay(chat_size: int) -> float:
    """
    Calculate dynamic polling delay based on chat participant count using a parabolic curve.
    
    Args:
        chat_size: Number of active chat participants (1-400)
        
    Returns:
        float: Delay in seconds before next poll
    """
    # Cap chat size at 400
    n = min(max(chat_size, 1), 400)
    
    # Parabolic curve parameters:
    # delay = a * (n - b)^2 + c
    # where:
    # a = 0.000625 (controls curve steepness)
    # b = 200 (vertex x-coordinate)
    # c = 5 (minimum delay)
    
    a = 0.000625  # Controls curve steepness
    b = 200       # Vertex x-coordinate (middle of range)
    c = 5         # Minimum delay in seconds
    
    # Calculate delay using parabolic formula
    delay = a * (n - b)**2 + c
    
    # Ensure delay is between 5 and 100 seconds
    delay = max(5, min(100, delay))
    
    logger.debug(f"Calculated delay: {delay:.2f}s for {n} participants")
    return delay 
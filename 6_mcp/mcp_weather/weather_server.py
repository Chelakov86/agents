# Get weather information (temperature, humidity, pressure, wind speed, description) for a given location

from mcp.server.fastmcp import FastMCP
from weather import Weather

mcp = FastMCP("weather_server")

@mcp.tool()
async def get_temperature(location: str) -> str:
    """Get the temperature for a given location.
    
    Args:
        location: The location to get the temperature for
    """
    return Weather.get(location).temperature

@mcp.tool()
async def get_humidity(location: str) -> str:
    """Get the humidity for a given location.
    
    Args:
        location: The location to get the humidity for
    """
    return Weather.get(location).humidity

@mcp.tool()
async def get_pressure(location: str) -> str:
    """Get the pressure for a given location.
    
    Args:
        location: The location to get the pressure for
    """
    return Weather.get(location).pressure

@mcp.tool()
async def get_wind_speed(location: str) -> str:
    """Get the wind speed for a given location.
    
    Args:
        location: The location to get the wind speed for
    """
    return Weather.get(location).wind_speed

@mcp.tool()
async def get_description(location: str) -> str:
    """Get the description for a given location.
    
    Args:
        location: The location to get the description for
    """
    return Weather.get(location).description


if __name__ == "__main__":
    mcp.run(transport='stdio')




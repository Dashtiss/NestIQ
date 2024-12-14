import asyncio
from pyinsteon import async_connect, DeviceManager
from pyinsteon.address import Address
from typing import Dict, Optional
import logging

class InsteonController:
    def __init__(self, hub_address: str, hub_port: int, hub_user: str, hub_pass: str):
        self.hub_address: str = hub_address
        self.hub_port: int = hub_port
        self.hub_user: str = hub_user
        self.hub_pass: str = hub_pass
        self.connection: Optional[DeviceManager] = None  
        self.transport: Optional[DeviceManager] = None  
        self.devices: Dict[Address, any] = {}  
        
    async def connect(self) -> None:
        """Connect to the Insteon Hub."""
        try:
            self.transport = await async_connect(
                self.hub_address, self.hub_port, self.hub_user, self.hub_pass
            )
            if self.transport:
                self.connection = self.transport  
                self.devices = self.connection._devices
        except Exception as e:
            logging.error(f"Connection failed: {e}")

    async def list_devices(self) -> Dict[str, str]:
        """List all devices connected to the Insteon Hub.

        Returns:
            Dict[str, str]: A dictionary with device IDs as keys and device descriptions as values.
        """
        if not self.connection:
            raise ConnectionError("Not connected to the Insteon Hub.")
        if not self.connection._devices:
            raise ConnectionError("No devices available. Please check the connection.")
        if not self.devices:
            raise ConnectionError("No devices available. Please check the connection.")

        if not self.connection._devices:
            raise ConnectionError("No devices available. Please check the connection.")
        if not self.devices:
            raise ConnectionError("No devices available. Please check the connection.")

        return {str(key): value.description for key, value in self.devices.items()}

    async def control_device(self, device_id: str, command: str) -> None:
        """Control a device by sending a command.
        
        Args:
            device_id (str): The ID of the device (e.g., "12.34.56").
            command (str): The command to execute (e.g., "on", "off").
        
        Raises:
            ConnectionError: If not connected to the Insteon Hub.
            ValueError: If the device ID is not found or the command is invalid.
            RuntimeError: If the command fails to execute.
        """
        if not self.connection:
            raise ConnectionError("Not connected to the Insteon Hub.")

        device = self.devices.get(Address(device_id))
        if not device:
            raise ValueError(f"Device with ID {device_id} not found.")

        try:
            if command.lower() == "on":
                await device.async_on()
            elif command.lower() == "off":
                await device.async_off()
            else:
                raise ValueError("Unknown command. Use 'on' or 'off'.")
        except Exception as e:
            raise RuntimeError(f"Failed to control device {device_id}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the Insteon Hub."""
        if self.connection:
            await self.connection.async_close()
        else:
            raise ConnectionError("No active connection to disconnect.")

# Example usage
if __name__ == "__main__":
    async def main():
        controller = InsteonController(
            hub_address="192.168.x.x",
            hub_port=25105,
            hub_user="username",
            hub_pass="password"
        )

        try:
            await controller.connect()
            devices = await controller.list_devices()
            print("Discovered Devices:", devices)
            await controller.control_device("12.34.56", "on")
            await controller.control_device("12.34.56", "off")
        finally:
            await controller.disconnect()

    asyncio.run(main())

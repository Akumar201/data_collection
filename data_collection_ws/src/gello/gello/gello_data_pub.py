import asyncio
import json
import zenoh

class ZenohControlClient:
    def __init__(self, config_file):
        self.config_file = config_file
        self.session = None
        self.client_config = None

    async def load_config(self):
        """Load the Zenoh client configuration from a JSON file and convert it to a Zenoh Config object."""
        with open(self.config_file, "r") as f:
            config_str = f.read()
        # Convert the JSON string to a Zenoh configuration object.
        self.client_config = zenoh.Config.from_json5(config_str)
        print("Client configuration loaded.")

    async def start_session(self):
        """Start a Zenoh session using the loaded configuration."""
        # Remove the await since zenoh.open is synchronous.
        self.session = zenoh.open(self.client_config)
        print("Zenoh session started.")

    async def publish_control(self):
        """
        Publish control inputs at 60Hz (every ~16.67 ms).
        This channel is considered high priority.
        """
        topic = "control/inputs"
        while True:
            # Here you would gather your control input from the dummy robotic arm.
            # Replace "dummy_control_data" with actual control data.
            control_data = "dummy_control_data"
            self.session.put(topic, control_data)  # Call put() synchronously
            # Sleep to achieve a ~60Hz publishing rate.
            await asyncio.sleep(1 / 60)

    def _control_callback(self, sample):
        """Callback function for handling received control messages."""
        print("Received control:", sample.payload)

    async def run(self):
        """Main entry point to load configuration, start session, and run tasks."""
        await self.load_config()
        await self.start_session()
        # Start the control publisher as a separate task.
        control_task = asyncio.create_task(self.publish_control())
        # Gather tasks (expand with additional tasks as needed).
        await asyncio.gather(control_task)

if __name__ == "__main__":
    client = ZenohControlClient("/app/config/client_config.json")
    asyncio.run(client.run())

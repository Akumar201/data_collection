import asyncio
import json
import zenoh

class ZenohControlSubscriber:
    def __init__(self, config_file):
        self.config_file = config_file
        self.session = None
        self.client_config = None

    async def load_config(self):
        """Load the Zenoh client configuration from a JSON file and convert it to a Zenoh Config object."""
        with open(self.config_file, "r") as f:
            config_str = f.read()
        self.client_config = zenoh.Config.from_json5(config_str)
        print("Subscriber configuration loaded.")

    async def start_session(self):
        """Start a Zenoh session using the loaded configuration."""
        self.session = zenoh.open(self.client_config)
        print("Subscriber session started.")

    def _control_callback(self, sample):
        try:
            # Convert the ZBytes payload to a Python bytes object.
            payload_bytes = bytes(sample.payload)
            # Decode the bytes into a UTF-8 string.
            decoded_str = payload_bytes.decode("utf-8")
            print("Received message:", decoded_str)
        except Exception as e:
            print("Error decoding payload:", e)

    async def run(self):
        """Main entry point to load configuration, start session, and subscribe to a topic."""
        await self.load_config()
        await self.start_session()
        # Create a subscriber on the "control/inputs" topic.
        self.session.declare_subscriber("control/inputs", self._control_callback)
        
        # Keep the subscriber running indefinitely.
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    subscriber = ZenohControlSubscriber("/app/config/client_config.json")
    asyncio.run(subscriber.run())

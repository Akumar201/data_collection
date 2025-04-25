import rclpy
from rclpy.node import Node
import time
import subprocess

class TopicMonitor(Node):
    def __init__(self, topics):
        super().__init__('topic_monitor')
        self.topics = topics  # List of topic names to monitor
        self.missing_topics = []
        self.stopped_topics = []
    
    def check_topic_exists(self, topic_name):
        """Check if a topic exists and is publishing."""
        topic_list = self.get_topic_names_and_types()
        for name, _ in topic_list:
            if name == topic_name:
                return True
        return False
    
    def check_all_topics_exist(self):
        """Check if all topics exist."""
        missing = []
        for topic in self.topics:
            if not self.check_topic_exists(topic):
                missing.append(topic)
        
        if missing:
            self.missing_topics = missing
            return False
        return True

    def monitor_topics_health(self):
        """Monitor if all topics are publishing and check their health."""
        while True:
            # Get the list of currently active topics
            active_topics = set(topic for topic, _ in self.get_topic_names_and_types())
            
            # Check which topics have stopped publishing
            stopped = [topic for topic in self.topics if topic not in active_topics]
            if stopped:
                self.stopped_topics = stopped
                self.get_logger().warning(f"Topics stopped publishing: {', '.join(stopped)}")

                # Optionally, you can stop recording or alert the user if critical topics stop
                if len(stopped) > 0:
                    return False  # Stop recording if any topic stops publishing
            else:
                self.stopped_topics = []
                self.get_logger().info("All topics are still publishing.")

            time.sleep(5)  # Check health every 5 seconds

    def get_missing_topics(self):
        """Return the list of missing topics."""
        return self.missing_topics

    def get_stopped_topics(self):
        """Return the list of stopped topics."""
        return self.stopped_topics

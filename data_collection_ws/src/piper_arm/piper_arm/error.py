class CustomErrorMessages:
    """A helper class to generate custom error messages for various scenarios."""
    
    @staticmethod
    def home_timeout_error(timeout_sec: float) -> str:
        """
        Generate an error message for when the arm fails to reach home within the timeout.
        
        Args:
            timeout_sec (float): The timeout duration in seconds.
        
        Returns:
            str: The formatted error message.
        """
        return f"Home position timeout exceeded: {timeout_sec:.1f} seconds."

    @staticmethod
    def connection_failed_error(details: str = "") -> str:
        """
        Generate an error message for a connection failure.
        
        Args:
            details (str): Additional details about the failure.
            
        Returns:
            str: The formatted error message.
        """
        base_message = "Failed to connect to hardware interface."
        if details:
            base_message += f" Details: {details}"
        return base_message

    @staticmethod
    def invalid_joint_value_error(joint_name: str, value) -> str:
        """
        Generate an error message when a joint value is invalid.
        
        Args:
            joint_name (str): The name of the joint.
            value: The value that is invalid.
        
        Returns:
            str: The formatted error message.
        """
        return f"Error: {joint_name} value {value} is not a valid integer."

    @staticmethod
    def generic_error(error: Exception) -> str:
        """
        Generate a generic error message from an exception.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            str: The formatted error message.
        """
        return f"An error occurred: {str(error)}"

    @staticmethod
    def custom_error(message: str) -> str:
        """
        Generate a custom error message.
        
        Args:
            message (str): The custom message.
            
        Returns:
            str: The custom error message.
        """
        return message


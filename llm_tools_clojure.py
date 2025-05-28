import llm
import nrepl
import os
from typing import Optional


class ClojureREPL(llm.Toolbox):
    """A toolbox for interacting with a Clojure nREPL server."""

    _connection = None
    _session = None

    def _get_connection(self):
        """Establish connection to nREPL server if not already connected."""
        if self._connection is None:
            port = self._read_nrepl_port()
            self._connection = nrepl.connect(f"nrepl://localhost:{port}")
            # Create a session
            self._connection.write({"op": "clone"})
            response = self._connection.read()
            self._session = response.get("new-session")
        return self._connection

    def _read_nrepl_port(self) -> str:
        """Read the nREPL port from .nrepl-port file."""
        try:
            with open(".nrepl-port", "r") as f:
                port = f.read().strip().rstrip('%')
                return port
        except FileNotFoundError:
            raise Exception("No .nrepl-port file found. Make sure your Clojure REPL is running.")

    def eval_clojure(self, code: str) -> str:
        """
        Evaluate Clojure code in the nREPL session.

        Args:
            code: The Clojure code to evaluate

        Returns:
            The result of the evaluation or error message
        """
        try:
            conn = self._get_connection()

            # Send the evaluation request
            conn.write({
                "op": "eval",
                "code": code,
                "session": self._session
            })

            # Collect all responses until we get 'done' status
            results = []
            outputs = []
            errors = []

            while True:
                response = conn.read()

                # Collect different types of output
                if "value" in response:
                    results.append(response["value"])
                if "out" in response:
                    outputs.append(response["out"])
                if "err" in response:
                    errors.append(response["err"])

                # Check if evaluation is complete
                if "status" in response and "done" in response["status"]:
                    break

            # Format the response
            result_parts = []

            if outputs:
                result_parts.append("Output:\n" + "".join(outputs))

            if results:
                result_parts.append("Result: " + " ".join(results))

            if errors:
                result_parts.append("Errors:\n" + "".join(errors))

            if not result_parts:
                return "Evaluation completed with no output"

            return "\n".join(result_parts)

        except Exception as e:
            return f"Error evaluating Clojure code: {str(e)}"

    def get_namespace(self) -> str:
        """Get the current namespace of the REPL session."""
        try:
            conn = self._get_connection()
            conn.write({
                "op": "eval",
                "code": "*ns*",
                "session": self._session
            })

            response = conn.read()
            namespace = response.get("value", "unknown")

            # Read the 'done' status
            conn.read()

            return f"Current namespace: {namespace}"
        except Exception as e:
            return f"Error getting namespace: {str(e)}"

    def load_file(self, file_path: str) -> str:
        """
        Load a Clojure file into the REPL.

        Args:
            file_path: Path to the Clojure file to load

        Returns:
            Result of loading the file
        """
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                code = f.read()

            return self.eval_clojure(code)

        except Exception as e:
            return f"Error loading file {file_path}: {str(e)}"

    def require_namespace(self, namespace: str) -> str:
        """
        Require a namespace in the REPL.

        Args:
            namespace: The namespace to require

        Returns:
            Result of requiring the namespace
        """
        code = f"(require '{namespace})"
        return self.eval_clojure(code)

    def close_connection(self) -> str:
        """Close the nREPL connection."""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                self._session = None
                return "nREPL connection closed"
            else:
                return "No active connection to close"
        except Exception as e:
            return f"Error closing connection: {str(e)}"


# Alternative functional approach using hookimpl
def eval_clojure_simple(code: str) -> str:
    """
    Simple function to evaluate Clojure code via nREPL.

    Args:
        code: The Clojure code to evaluate

    Returns:
        The result of the evaluation
    """
    try:
        # Read port from .nrepl-port file
        with open(".nrepl-port", "r") as f:
            port = f.read().strip().rstrip('%')

        # Connect and evaluate
        conn = nrepl.connect(f"nrepl://localhost:{port}")
        conn.write({"op": "eval", "code": code})

        # Read response
        response = conn.read()
        result = response.get("value", "No result")

        # Read 'done' status
        conn.read()
        conn.close()

        return result

    except Exception as e:
        return f"Error: {str(e)}"


@llm.hookimpl
def register_tools(register):
    """Register the Clojure evaluation tools."""
    register(ClojureREPL)
    register(eval_clojure_simple)

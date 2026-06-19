import sys
import json

def main():
    try:
        # Read from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            sys.exit(0)

        data = json.loads(input_data)

        # Extract command line
        arguments = data.get("arguments", {})
        command_line = arguments.get("CommandLine", "")

        # Check for destructive commands
        destructive_patterns = ["rm -rf", "rm -r", "del /f", "rd /s"]
        for pattern in destructive_patterns:
            if pattern in command_line.lower():
                print(f"Validation Error: Destructive command detected ('{pattern}'). Execution blocked.", file=sys.stderr)
                sys.exit(1)

        sys.exit(0)
    except Exception as e:
        print(f"Validator error: {e}", file=sys.stderr)
        # Fail secure: block if parsing fails
        sys.exit(1)

if __name__ == "__main__":
    main()

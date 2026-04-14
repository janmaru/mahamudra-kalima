"""Sample Claude Code session for testing."""

{"id": "msg_001", "created_at": "2025-04-14T10:00:00Z", "model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 500, "output_tokens": 200}, "content": [{"type": "tool_use", "name": "read_file", "input": {}}], "user_message": "What does this function do?"}
{"id": "msg_002", "created_at": "2025-04-14T10:05:00Z", "model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 1200, "output_tokens": 800}, "content": [{"type": "tool_use", "name": "write_file", "input": {}}], "user_message": "Add type hints to the parser function"}
{"id": "msg_003", "created_at": "2025-04-14T10:10:00Z", "model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 2000, "output_tokens": 1500}, "content": [{"type": "tool_use", "name": "execute_command", "input": {}}], "user_message": "Run the test suite"}
{"id": "msg_004", "created_at": "2025-04-14T10:15:00Z", "model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 800, "output_tokens": 500}, "content": [{"type": "tool_use", "name": "write_file", "input": {}}], "user_message": "Fix the type error on line 42"}
{"id": "msg_005", "created_at": "2025-04-13T14:30:00Z", "model": "claude-3-5-opus-20250514", "usage": {"input_tokens": 3000, "output_tokens": 2000}, "content": [{"type": "tool_use", "name": "read_file", "input": {}}], "user_message": "Explain the API design"}

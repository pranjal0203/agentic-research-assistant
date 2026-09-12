import json
import subprocess
from unittest.mock import MagicMock, patch

from services.mcp_client import MCPClient


@patch("subprocess.Popen")
def test_mcp_client_connection(mock_popen):
    """
    Verify client connection handshake RPC triggers correctly.
    """
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    # Set up stdout response payload mock
    init_res = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "serverInfo": {"name": "test-server", "version": "1.0"},
        },
    }
    mock_process.stdout.readline.return_value = json.dumps(init_res) + "\n"

    client = MCPClient("test", "node", ["index.js"])
    success = client.connect()

    assert success is True
    mock_popen.assert_called_once_with(
        ["node", "index.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )


@patch("subprocess.Popen")
def test_mcp_client_list_tools(mock_popen):
    """
    Verify client list_tools RPC retrieves tool configurations correctly.
    """
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    # Connection init mock
    init_res = {"jsonrpc": "2.0", "id": 1, "result": {}}
    # List tools mock response
    tools_res = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "tools": [
                {
                    "name": "view_file",
                    "description": "Read file contents",
                    "inputSchema": {},
                }
            ]
        },
    }
    mock_process.stdout.readline.side_effect = [
        json.dumps(init_res) + "\n",
        json.dumps(tools_res) + "\n",
    ]

    client = MCPClient("test", "node", ["index.js"])
    client.connect()
    tools = client.list_tools()

    assert len(tools) == 1
    assert tools[0]["name"] == "view_file"

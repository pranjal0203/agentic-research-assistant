"""
Model Context Protocol (MCP) Client Service.

Enables connection to local MCP servers over stdio, dynamic tool discovery,
and wrapping discovered resources/tools as CrewAI-compatible tool objects.
"""

import json
import os
import subprocess
from typing import Any

from crewai.tools import tool

# Central configurations file for local servers
CONFIG_PATH = os.path.join("config", "mcp_servers.json")


class MCPClient:
    """
    Standard stdio-based client for Model Context Protocol (MCP) servers.
    """

    def __init__(self, server_name: str, command: str, args: list[str]) -> None:
        self.server_name = server_name
        self.command = command
        self.args = args
        self.process = None
        self.request_id = 0

    def connect(self) -> bool:
        """
        Spawn the MCP server process and perform the initialize handshake.
        """
        try:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            # Perform initialize RPC handshake
            init_response = self._send_request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "intelligent-agentic-research-assistant",
                        "version": "3.0.0",
                    },
                },
            )
            if init_response and "error" not in init_response:
                # Send initialized notification
                self._send_notification("notifications/initialized")
                return True
            return False
        except Exception:  # noqa: BLE001
            return False

    def list_tools(self) -> list[dict]:
        """
        Discovers tools exposed by the MCP server.
        """
        if not self.process:
            return []
        response = self._send_request("tools/list")
        if response and "result" in response:
            return response["result"].get("tools", [])
        return []

    def call_tool(self, name: str, arguments: dict) -> str:
        """
        Invoke an MCP server tool over JSON-RPC.
        """
        if not self.process:
            return "Error: MCP Server not connected."

        response = self._send_request(
            "tools/call",
            {"name": name, "arguments": arguments},
        )

        if not response:
            return "Error: Empty response from MCP Server."

        if "error" in response:
            return f"Error executing MCP Tool: {response['error']}"

        result = response.get("result", {})
        content_items = result.get("content", [])
        text_outputs = [
            item.get("text", "") for item in content_items if item.get("type") == "text"
        ]
        return "\n".join(text_outputs) if text_outputs else str(result)

    def disconnect(self) -> None:
        """
        Shutdown the subprocess server.
        """
        if self.process:
            self.process.terminate()
            self.process = None

    def _send_request(self, method: str, params: dict | None = None) -> dict | None:
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None
        self.request_id += 1
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        try:
            self.process.stdin.write(json.dumps(payload) + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
            return json.loads(line) if line else None
        except Exception:  # noqa: BLE001
            return None

    def _send_notification(self, method: str, params: dict | None = None) -> None:
        if not self.process or not self.process.stdin:
            return
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            payload["params"] = params
        try:
            self.process.stdin.write(json.dumps(payload) + "\n")
            self.process.stdin.flush()
        except Exception:  # noqa: BLE001, S110
            pass


def load_mcp_tools() -> list:
    """
    Query config/mcp_servers.json, connect to active servers,
    and return dynamic CrewAI-compatible tool wrappers.
    """
    if not os.path.exists(CONFIG_PATH):
        return []

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:  # noqa: BLE001
        return []

    mcp_tools = []
    servers = config.get("mcpServers", {})

    for name, cfg in servers.items():
        command = cfg.get("command")
        args = cfg.get("args", [])

        if not command:
            continue

        client = MCPClient(name, command, args)
        if client.connect():
            tools = client.list_tools()
            for t_cfg in tools:
                t_name = t_cfg.get("name")
                t_desc = t_cfg.get("description", "Exposed MCP Server Tool")

                # Wrap the tool in a dynamic crewai.tools decorator structure
                def make_wrapper(cli, name_str, desc_str):
                    @tool(name_str)
                    def mcp_tool_wrapper(query: str) -> str:
                        # Convert input string queries into JSON args if needed
                        # Or pass directly as query arguments to match server expectations
                        try:
                            args_payload = json.loads(query)
                        except Exception:  # noqa: BLE001
                            args_payload = {"path": query}  # Default parameter guess
                        return cli.call_tool(name_str, args_payload)

                    mcp_tool_wrapper.description = desc_str
                    return mcp_tool_wrapper

                mcp_tools.append(make_wrapper(client, t_name, t_desc))

    return mcp_tools

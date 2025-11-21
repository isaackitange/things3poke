#!/usr/bin/env python3
"""
Things 3 MCP Server (Email-based)
Works from any hosted server - laptop can be off!
"""

import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Optional

# Configuration from environment variables
THINGS_EMAIL = "add-to-things-wqfcr1hf2k2vp3su8h4z2@things.email"
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

class ThingsEmailMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "add_todo",
                "description": "Add a new task to Things 3 inbox",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes or details (optional)"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "add_todo_with_heading",
                "description": "Add a task with a specific heading (project/area)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "heading": {
                            "type": "string",
                            "description": "The project or area name"
                        },
                        "title": {
                            "type": "string",
                            "description": "The task title"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes (optional)"
                        }
                    },
                    "required": ["heading", "title"]
                }
            },
            {
                "name": "add_checklist",
                "description": "Add a task with a checklist of subtasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The main task title"
                        },
                        "checklist_items": {
                            "type": "array",
                            "description": "List of checklist items",
                            "items": {"type": "string"}
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes (optional)"
                        }
                    },
                    "required": ["title", "checklist_items"]
                }
            }
        ]
    
    def _send_email(self, subject: str, body: str) -> dict:
        """Send email to Things using SMTP"""
        try:
            # Check if SMTP is configured
            if not SMTP_USER or not SMTP_PASSWORD:
                return {
                    "success": False,
                    "error": "SMTP not configured. Set SMTP_USER and SMTP_PASSWORD environment variables."
                }
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = THINGS_EMAIL
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email with proper connection cleanup
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            try:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                text = msg.as_string()
                server.sendmail(SMTP_USER, THINGS_EMAIL, text)
                
                return {
                    "success": True,
                    "message": f"Task '{subject}' sent to Things inbox"
                }
            finally:
                server.quit()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def add_todo(self, title: str, notes: str = "") -> dict:
        """Add a simple task to Things"""
        body = notes if notes else ""
        return self._send_email(subject=title, body=body)
    
    def add_todo_with_heading(self, heading: str, title: str, notes: str = "") -> dict:
        """Add a task under a specific heading (project/area)"""
        # Format: "Heading: Task title" in subject
        subject = f"{heading}: {title}"
        body = notes if notes else ""
        return self._send_email(subject=subject, body=body)
    
    def add_checklist(self, title: str, checklist_items: list, notes: str = "") -> dict:
        """Add a task with checklist items"""
        # Build body with checklist
        body_lines = []
        if notes:
            body_lines.append(notes)
            body_lines.append("")
        
        for item in checklist_items:
            body_lines.append(f"- {item}")
        
        body = "\n".join(body_lines)
        return self._send_email(subject=title, body=body)
    
    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Handle a tool call from the MCP client"""
        if tool_name == "add_todo":
            return self.add_todo(**arguments)
        elif tool_name == "add_todo_with_heading":
            return self.add_todo_with_heading(**arguments)
        elif tool_name == "add_checklist":
            return self.add_checklist(**arguments)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

def main():
    """MCP Server main loop - handles JSON-RPC requests"""
    server = ThingsEmailMCPServer()
    
    # Listen for requests on stdin
    import sys
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line)
            request_id = request.get("id")
            
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "things-email-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": server.tools}
                }
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = server.handle_tool_call(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "Method not found"}
                }
            
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)}
            }), flush=True)

if __name__ == "__main__":
    main()

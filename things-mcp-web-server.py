#!/usr/bin/env python3
"""
Things 3 MCP Server (Email-based) - Web Server Version
Works with Railway and Poke over HTTP
"""

import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional

# Configuration from environment variables
THINGS_EMAIL = "add-to-things-wqfcr1hf2k2vp3su8h4z2@things.email"
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
PORT = int(os.getenv('PORT', '8080'))

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
            
            # Send email
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
        subject = f"{heading}: {title}"
        body = notes if notes else ""
        return self._send_email(subject=subject, body=body)
    
    def add_checklist(self, title: str, checklist_items: list, notes: str = "") -> dict:
        """Add a task with checklist items"""
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

# Global server instance
mcp_server = ThingsEmailMCPServer()

class MCPHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "service": "Things 3 MCP Server",
                "version": "1.0.0"
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle MCP requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
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
                    "result": {"tools": mcp_server.tools}
                }
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = mcp_server.handle_tool_call(tool_name, arguments)
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"{self.address_string()} - {format % args}")

def main():
    """Start the HTTP server"""
    print(f"Starting Things MCP Server on port {PORT}...")
    print(f"SMTP configured: {bool(SMTP_USER and SMTP_PASSWORD)}")
    
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MCPHTTPHandler)
    
    print(f"Server running on http://0.0.0.0:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()

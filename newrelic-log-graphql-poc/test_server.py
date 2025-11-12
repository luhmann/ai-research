#!/usr/bin/env python3
"""
Simple test GraphQL server for local testing
This receives mutations from the log tailer
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime


class GraphQLHandler(BaseHTTPRequestHandler):
    """Simple GraphQL request handler"""

    received_mutations = []

    def do_POST(self):
        """Handle POST requests"""
        if self.path != '/graphql':
            self.send_error(404)
            return

        # Read request body
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            mutation = data.get('query', '')
            variables = data.get('variables', {})

            # Log received mutation
            timestamp = datetime.now().isoformat()
            self.received_mutations.append({
                'timestamp': timestamp,
                'mutation': mutation,
                'variables': variables
            })

            print(f"\n[{timestamp}] Received mutation:")
            print(f"  Variables: {json.dumps(variables, indent=2)}")

            # Send success response
            response = {
                'data': {
                    'createEvent': {
                        'id': f'event_{len(self.received_mutations)}',
                        'success': True
                    }
                }
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Error processing request: {e}")
            error_response = {
                'errors': [{'message': str(e)}]
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=4000):
    """Run the test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, GraphQLHandler)

    print(f"Starting test GraphQL server on http://localhost:{port}/graphql")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        print(f"Total mutations received: {len(GraphQLHandler.received_mutations)}")


if __name__ == '__main__':
    run_server()

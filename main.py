import cgi
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class App(BaseHTTPRequestHandler):
    endpoints = {'get': {}, "post": {}, 'patch': {}, 'put': {}, 'delete': {}}

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        temp = str(content).strip('b\'')
        self.end_headers()
        return temp

    def parse_POST(self):
        content_type, pdict = cgi.parse_header(self.headers['content-type'])
        if content_type == 'multipart/form-data':
            post_vars = {}
            cg = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
            for key in cg.keys():
                post_vars[key] = cg[key].value
            return post_vars

    @classmethod
    def get(cls, endpoint):
        def decorator(handler_func):
            cls.endpoints['get'][endpoint] = handler_func
            return handler_func

        return decorator

    @classmethod
    def post(cls, endpoint):
        def decorator(handler_func):
            cls.endpoints['post'][endpoint] = handler_func
            return handler_func

        return decorator

    def do_GET(self):
        endpoint = self.path
        if endpoint in self.endpoints['get']:
            handler_func = self.endpoints['get'][endpoint]
            response = handler_func()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_error(404, 'Endpoint not found')

    def do_POST(self):
        endpoint = self.path
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        if endpoint in self.endpoints['post']:
            post_vars = self.parse_POST()
            handler_func = self.endpoints['post'][endpoint]
            response = handler_func(post_vars)
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, 'Endpoint not found')


@App.get('/path')
def my_func():
    return {'message': f'Hello, !'}


@App.post('/path')
def my_func(payload):
    return payload


def run(server_class=HTTPServer, handler_class=App, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()

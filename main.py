from flask import Flask, jsonify
import json
import re
import requests

app = Flask(__name__)

mock_file = open('assets/atlassiancom-jira.json')
data = json.load(mock_file)

SUCCESS_STATUS_CODE = (200, 201)
FAKER_PARSER_URL = 'http://localhost:5050'
FAKER_PARSER_SPECIAL_SEPARATOR = '*'


@app.route('/<arg>')
def home(**kwargs):
    print(kwargs)
    return 'Hello'


def endpoint_to_flask_format(endpoint: str) -> str:
    endpoint_components = endpoint.split('/')
    final_endpoint = ''

    for comp in endpoint_components:
        if comp.startswith(':'):
            comp = re.sub(r'(?<!^)(?=[A-Z])', '_', comp[1:]).lower()  # to camel_case
            comp = '<%s>' % comp

        final_endpoint += '/%s' % comp

    return final_endpoint


def route_factory(endpoint: str, name: str, method: str, body: str):
    def route_func(**kwargs):
        local_body = body
        content = {}
        try:
            fakers = re.findall("{{faker '.*?'}}", local_body)
            for faker in fakers:
                # weird way to extract faker argument, maybe refactor this
                arg = faker[faker.find('\'') + 1:faker.find('\'', faker.find('\'') + 1)]
                faker_response = requests.get(
                    url=FAKER_PARSER_URL,
                    params='q=%s' % arg.replace('.', FAKER_PARSER_SPECIAL_SEPARATOR)
                )
                local_body = local_body.replace(faker, faker_response.text, 1)
            content = json.loads(local_body)
        except Exception:
            pass

        return jsonify(content), 200

    route_func.__name__ = name
    app.add_url_rule(endpoint, name, route_func, methods=[method])

    return route_func


if __name__ == '__main__':
    routes = data['routes']
    for route in routes:
        route_endpoint = endpoint_to_flask_format(route.get('endpoint', ''))
        route_method = route.get('method')
        route_name = route.get('documentation', '').replace(' ', '_').lower()
        route_responses = iter(route.get('responses', []))
        route_success_response = ''
        while True:
            resp = next(route_responses, None)
            if not resp:
                break
            if resp.get('statusCode') in SUCCESS_STATUS_CODE:
                route_success_response = resp.get('body', '')
                break

        route_factory(route_endpoint, route_name, route_method, route_success_response)

    app.run(debug=True)

URLs = {
    'base': 'http://sphinx-kubernetes.intracom-telecom.com/SMPlatform/manager/rst',
    'sm': [
        {'method': 'GET', 'url': '/getServices'},
        {'method': 'GET', 'url': '/ServiceInfo', 'params': ['reqservicename']},
        {'method': 'POST', 'url': '/Authentication', 'body': {}},
        {'method': 'GET', 'url': '/Authorization'},
        {'method': 'POST', 'url': '/SaveServiceAllMetadata/', 'ticket': ''},
        {'method': 'GET', 'url': '/ReadServiceAllMetadata/', 'ticket': ''},
    ],
    'kafka': [
        {'method': 'GET', 'url': '/getKafkaTopics'},
        {'method': 'POST', 'url': '/KafkaAuthentication'},
        {'method': 'POST', 'url': '/getKafkaToken'},
        {'method': 'GET', 'url': '/getJWKSet'},
    ],
    'sso': [
        {'method': 'POST', 'url': '/CreateEndUser/', 'ticket': ''},
        {'method': 'POST', 'url': '/CreateEndUsers/', 'ticket': ''},
        {'method': 'GET', 'url': '/DeleteEndUser/', 'ticket': ''},
        {'method': 'POST', 'url': '/EditEndUser/', 'ticket': ''},
        {'method': 'GET', 'url': '/GetEndUsers/', 'ticket': ''},
        {'method': 'POST', 'url': '/SetEndUserState/', 'ticket': ''},
        {'method': 'POST', 'url': '/ReadEndUserState/', 'ticket': ''},
    ]
}
models = [
    {'user': {'username': '', 'password': '', 'email': '', 'name': ''}},
    {'EditUser': {'username': '', 'password': '', 'email': '', 'name': '', 'oldusername': ''}},
    {'ApiResultError': {'errorcode': '', 'description': ''}},
    {'getServices': {'servicecode': '', 'AAA': '', 'host': '', 'port': '', 'path': '', 'method': ''}},
    {'metadata': {'componentkey': '', 'swagger': '', 'deployment_file': '', 'metadata': ''}},
    {'returnmetadata': {'swagger': '', 'deployment_file': '', 'metadata': '', 'component_name': ''}},
    {'login': {'username': '', 'password': ''}},
    {'userdata': {'id': '', 'username': '', 'password': '', 'name': '', 'email': '', 'sessionExp': '', 'status': ''}},
    {'service': {'ip': '', 'body_parameters': '', 'servicecode': '', 'method': '', 'port': '', 'roles': '', 'name': '', 'parameters': [{'opt': '', 'name': '', 'type': ''}], 'contenttype': ''}},
]

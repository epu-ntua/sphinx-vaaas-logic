class Settings:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']

    def get_db_config(self):
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }


class RabbitMQ:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']

    def get_config(self):
        return {
            'url': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password
        }

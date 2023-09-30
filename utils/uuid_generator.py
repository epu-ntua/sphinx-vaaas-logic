import uuid


def generate_uuid():
    return str(uuid.uuid4())  # TODO check influxDb for possible duplicates

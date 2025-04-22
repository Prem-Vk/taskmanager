from uuid import UUID

def validate_uuid(uuid_to_test, version=4):
    """
    Validate a UUID string.
    :param uuid_to_test: UUID string to validate
    :param version: Version of the UUID (default is 4)
    :return: True if valid, False otherwise
    """
    try:
        val = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(val) == uuid_to_test

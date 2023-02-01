def import_application_configuration(provider: str, app_id: str):
    module = __import__(
        'cumulonimbus.applications.{}.{}.application_configuration'.format(provider, app_id), fromlist=["ApplicationConfiguration"])
    application_configuration = getattr(module, "ApplicationConfiguration")
    return application_configuration


def get_application_configuration(provider: str, app_id: str):
    """
        Returns the configuration implementation for a vulnerable application id.
        :param provider: AWS / Azure
        :param app_id: The vulnerable application id (e.g.: ec2_ssrf)
    """
    application_configuration = import_application_configuration(
        provider, app_id)
    return application_configuration()

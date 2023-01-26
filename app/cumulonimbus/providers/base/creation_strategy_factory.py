_strategies = {
    'aws': 'AWSCreationStrategy',
    'azure': 'AzureCreationStrategy'
}


def import_creation_strategy(provider):
    strategy_class = _strategies[provider]
    module = __import__(
        'cumulonimbus.providers.{}.creation_strategy'.format(provider), fromlist=[strategy_class])
    creation_strategy = getattr(module, strategy_class)
    return creation_strategy


def get_creation_strategy(provider: str):
    """
        Returns a creation strategy implementation for a provider.
        :param provider: The creation strategy 
    """
    creation_strategy = import_creation_strategy(provider)
    return creation_strategy()

from deprecated.sphinx import versionadded


@versionadded(
    version="2.3.1",
    reason="Added to avoid display of unrelevant warning to the end user",
)
class SepalWarning(Warning):
    """
    A custom warning class that will be the only one to be displayed in the Alert in voila.
    The other normal warning such as lib DeprecationWarning will be displayed in the notebook but hidden to the end user
    """

    pass

import os
from pathlib import Path


def set_credentials():
    """
    Set the credentials of the earthengine account based on the "EARTHENGINE_TOKEN"
    Environment variable
    """

    # get the credentials
    ee_token = os.environ["EARTHENGINE_TOKEN"]
    credential = f'{{"refresh_token":"{ee_token}"}}'

    # write them in the appropriate file
    credential_folder_path = Path.home() / ".config" / "earthengine"
    credential_folder_path.mkdir(parents=True, exist_ok=True)
    credential_file_path = credential_folder_path / "credentials"
    with credential_file_path.open("w") as f:
        f.write(credential)

    return

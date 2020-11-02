import pydicom


def get_in_stack_position_number(path: str):
    """
    Get stack position from the number
    :param path:
    :return:
    """

    dcm = pydicom.dcmread(path, force=True)
    return dcm.InStackPositionNumber

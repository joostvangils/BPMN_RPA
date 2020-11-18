import pyautogui


def screenshot(path: str) -> str:
    """
    Make a screenshot and save it to file as PNG

    :param path: The full path of the location and filename (including the PNG extension) to save the screenshot
    :returns: The pathname of the screenshot file
    """
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(path)
    return path


def run_python_code(code):
    """
    Dynamically run Python code
    :param code: The code to run
    :return: OK, or exception when an error occurs
    """
    try:
        ret = exec(code)
        return ret
    except Exception as ex:
        return ex


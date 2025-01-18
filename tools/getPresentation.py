import winreg
from pathlib import Path

import psutil
import win32com.client
import win32gui

from walnut.utilities import get_special_folder, ignore_exceptions


def get_default_download_path():
    try:
        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return Path(location)
    except Exception:
        return Path.home() / "Downloads"


def get_powerpoint_process():
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] and "POWERPNT.EXE" in process.info["name"]:
            return process
    return None


def get_powerpoint_file_types(paths):
    pptFiles = []
    for path in paths:
        try:
            if Path(path).suffix in (".ppt", ".pptx"):
                pptFiles.append(path)
        except Exception:
            pass
    return pptFiles


def get_files_accessed_by_process(process):
    try:
        openFiles = []
        for file in process.open_files():
            openFiles.append(file.path)
        return openFiles
    except Exception:
        return []


def get_ppt_accessed_by_powerpoint():
    powerpointProcess = get_powerpoint_process()
    filesAccessed = get_files_accessed_by_process(powerpointProcess)
    return get_powerpoint_file_types(filesAccessed)


def get_protected_view_title():
    def enum_windows_callback(hwnd, titles):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Protected View" in title:
                titles.append(title)

    powerpointTitles = []
    win32gui.EnumWindows(enum_windows_callback, powerpointTitles)
    return powerpointTitles


def paths_from_powerpoint_titles(titles):
    paths = []
    for title in titles:
        path = title.replace("-  Protected View - PowerPoint", "").strip()
        if path.endswith((".ppt", ".pptx")):
            paths.append(path)
    return paths


def find_ppt_path_from_file_name(fileNames):
    pptPaths = []
    notFound = []
    filesAccessed = get_ppt_accessed_by_powerpoint()
    downloadDirectory = get_default_download_path()
    desktopDirectory = get_special_folder("desktop")
    for name in fileNames:
        pathDownload = downloadDirectory / name
        pathDesktop = desktopDirectory / name
        if pathDownload.exists() and pathDownload.is_file():
            pptPaths.append(str(pathDownload))
        elif pathDesktop.exists() and pathDesktop.is_file():
            pptPaths.append(str(pathDesktop))
        else:
            notFound.append(name)
    for ppt, name in zip(filesAccessed, fileNames):
        if name in notFound:
            pptPaths.append(ppt)
    return pptPaths


def check_active_presentation():
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    if powerpoint.SlideShowWindows.Count > 0:
        slideshow = powerpoint.SlideShowWindows(1)
        presentation = slideshow.Presentation
        return presentation.FullName if presentation.Path else None
    elif powerpoint.Presentations.Count > 0:
        activePresentation = powerpoint.ActivePresentation
        return activePresentation.FullName if activePresentation.Path else None
    else:
        protectedViewTitle = paths_from_powerpoint_titles(get_protected_view_title())
        return find_ppt_path_from_file_name(protectedViewTitle)


@ignore_exceptions
def get_presentation():
    powerpointProcess = get_powerpoint_process()
    if not powerpointProcess:
        return []
    path = check_active_presentation()
    if path is None:
        return []
    if isinstance(path, list):
        return list(map(Path, path))
    else:
        path = Path(str(path))
        if path.exists() and path.is_file():
            return [path]
    return []
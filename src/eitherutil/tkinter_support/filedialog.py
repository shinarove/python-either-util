from typing import Optional, Iterable, List, Tuple
from pathlib import Path
from tkinter import Tk, filedialog

from eitherutil import Either, Success, io

def askopenfilename(
        *, 
        title: Optional[str] = None, 
        initialdir: Optional[str | Path] = None, 
        filetypes: Optional[Iterable[Tuple[str, str | List[str] | Tuple[str, ...]]]] = None
    ) -> Either[str, Optional[Path]]:
    """Opens a filedialog to ask for a filename. Wraps the API 'tkinter.filedialog.askopenfilename'.

    Args:
        title (str): Optional title of the filedialog.
        initialdir (str | Path): Optional directory path where the filedialog should be opened to.
        filetypes (Iterable[Tuple[str, str | List[str] | Tuple[str, ...]]]):
            Iterable of tuples containing each the file category title and a string, list or tuple
            containing the allowed extensions for the category. (E.g. [("Image File"), "*.jpg, *.jpeg"])
    Returns:
        Either[str, Path | None]: Failure with error message or Success with the selected Path or
            None when the operation was canceled by the user.
    """
    if initialdir is not None:
        res = io.validate_dir_path(initialdir)
        if res.is_failure():
            return res

    root = Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(
        title=title,
        initialdir=initialdir,
        filetypes=filetypes
    )
    root.destroy()

    if not image_path:
        return Success(None)
    return Success(Path(image_path))
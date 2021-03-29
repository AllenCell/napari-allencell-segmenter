import napari_aicssegmentation
from pathlib import Path

PAGE_WIDTH = 440
PAGE_CONTENT_WIDTH = PAGE_WIDTH - 40
WORKFLOW_BUTTON_HEIGHT = 200

class Style:
    STYLES_DIR = Path(napari_aicssegmentation.__file__).parent / "style"
    cache = dict()

    @classmethod
    def get_stylesheet(cls, name: str) -> str:
        if name is None:
            raise ValueError("Stylesheet name can't be None")
        if not name.endswith(".qss"):
            raise ValueError("Stylesheet must be a qss file (.qss)")

        if name not in cls.cache:
            cls.cache[name] = cls._load_from_file(name)

        return cls.cache[name]                

    @classmethod
    def _load_from_file(cls, name: str) -> str:
        path = cls.STYLES_DIR / name
        with open(path, "r") as handle:
            return handle.read()
    



class FileObject():
    def __init__(self, parent_wo: int, file_id: str, file_ext: str):
        self.wo = parent_wo
        self.file_id = file_id
        self.file_ext = file_ext

    def __repr__(self):
        return (f"ID: {self.file_id}"
                f"EXT: {self.file_ext}")
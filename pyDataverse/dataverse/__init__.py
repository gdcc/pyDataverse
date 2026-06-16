from .collection import Collection
from .contentbase import ContentBase
from .dataset import Dataset
from .dataverse import Author, Contact, Dataverse, Subject
from .file import File

ContentBase.model_rebuild()
Collection.model_rebuild()
Dataset.model_rebuild()
File.model_rebuild()

__all__ = [
    "Dataverse",
    "Author",
    "Contact",
    "Subject",
    "Dataset",
    "File",
]

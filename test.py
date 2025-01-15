from pyDataverse.api import NativeApi
from rich import print

api = NativeApi("https://demo.dataverse.org", "6c0e784a-38cc-42a4-8017-7ec09c3785ff")

dataset = api.get_dataset(identifier="doi:10.70122/FK2/BYBCAB")
print(dataset.json())

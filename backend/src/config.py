import datetime
import os

FolderYear = datetime.datetime.now().strftime("%Y")
FolderDate = datetime.datetime.now().strftime("%m-%d")
LogFileName = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

LOG_FILE_PATH = f".log/{FolderYear}/{FolderDate}/{LogFileName}"
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

FILE_PATH = os.path.join(os.getcwd(), "data/pdf")

I140_PATH = os.path.join(FILE_PATH, "I-140.pdf")
OUTPUT_PDF_PATH = os.path.join(FILE_PATH, "filled_foorm.pdf")
I140_JSON_PATH = os.path.join(FILE_PATH, "I-140_fields.json")

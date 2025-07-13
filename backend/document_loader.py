
import fitz  # PyMuPDF
import openpyxl


def load_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def load_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    text = ""
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value:
                    text += str(cell.value) + " "
    return text


def extract_text(file_path, extension):
    if extension == '.txt':
        return load_txt(file_path)
    elif extension == '.pdf':
        return load_pdf(file_path)
    elif extension in ['.xls', '.xlsx']:
        return load_excel(file_path)
    else:
        raise ValueError("Unsupported file type")
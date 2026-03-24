import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text = []
        for p in tree.iterfind('.//w:p', namespace):
            p_text = []
            for t in p.iterfind('.//w:t', namespace):
                p_text.append(t.text)
            if p_text:
                text.append(''.join(p_text))
        return '\n'.join(text)
    except Exception as e:
        return f"Error: {str(e)}"

with open(r"c:\Users\user\Desktop\DIC4\extracted_docx.txt", "w", encoding="utf-8") as f:
    f.write(extract_text_from_docx(r"c:\Users\user\Desktop\DIC4\4112056025 資工三 林鈺紳DIC3.docx"))

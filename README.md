# DocxParser
Parsing docx files with python-docx and pandoc

### EXAMPLES
```python
# using python-docx
docx = Docx(filepath)
title = docx.get_body_title()
# using pandoc
doc = Pandoc(filepath)
title = doc.get_body_title()
```

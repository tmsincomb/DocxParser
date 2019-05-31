from glob import glob
from subprocess import check_output, CalledProcessError
from typing import Union, Dict, List
from pathlib import Path
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


class PathTools:

    def filepaths(self, folder: Union[Path, str]) -> list:
        ''' folder is a text that follows glob syntax '''
        return [self.filepath(f) for f in glob(folder)]

    def filepath(self, filepath: Union[Path, str]) -> str:
        path = Path(filepath)
        if path.is_file():
            path = str(path.absolute())
            return path
        print(f'WARNING ::: {filepath} is not a file')


class TextTools:

    def remove_unicode(self, string: str) -> str:
        '''
        Removes unicode by converting the string into native bytes and then into
        ascii to force unicode out because it can't be converted.

        Args: string (str): string containing unicode
        Returns: string without unicode
        '''
        # we dont want to remove space unicode
        string = string.replace('\xa0', ' ')
        # convert to bytes to get the unicde to show up properly
        byte_string = bytes(string, 'utf-8')
        # removes unicode and ignores errors from the unicode
        byte_str_without_unicode = byte_string.decode("ascii", "ignore")

    def count_head_spaces(self, string: str) -> int:
        ''' Number of spaces before a entity other than a space '''
        return len(string) - len(string.lstrip(' '))

    def count_tail_spaces(self, string: str) -> int:
        ''' Number of spaces after a entity other than a space '''
        return len(string) - len(string.rstrip(' '))


class Pandoc(PathTools, TextTools):

    content: str
    infile: Path

    def __init__(self, infile=None):
        self.infile = infile
        self.content = self.load(infile) if infile else None

    def shell(self, string: str) -> str:
        '''
        Notes: check_output is the only one to behave like a real shell
        Args: string (str): shell script
        Returns: whatever the shell script was intended to return; else 0
        '''
        try:
            return check_output(string, shell=True).decode('UTF-8')
        except CalledProcessError:
            # TODO: check why this failed
            raise

    def load(self, filepath: Union[Path, str]) -> None:
        '''
        Notes: Init content and soup instances
        Args: filepath (Path, str): complete file path to docx file
        '''
        filepath = self.filepath(filepath)
        suffix = Path(filepath).suffix[1:]
        filepath = filepath.replace(' ', '\ ')
        content = self.shell(f'pandoc -f {suffix} -t markdown --wrap=none {filepath}')
        return content


class Docx(Pandoc):

    content: str
    infile: Path

    def __init__(self, infile=None):
        self.infile = infile
        self.content = self.strip_meta(self.load(infile)) if infile else None

    def strip_meta(self, content: str) -> str:
        '''
        Sometimes we don't need the noise such as bold "**" in the strings
        Args: content (str): complete pages of file seperated with newlines
        Returns: The same content minus the noise
        '''
        new_content = []
        values_to_replace = ['*', '[', ']', '{.underline}']
        for line in content.splitlines():
            if not line or line == '**':
                new_content.append(line)
                continue
            for value_to_replace in values_to_replace:
                line = line.replace(value_to_replace, '')
            new_content.append(line)
        return '\n'.join(new_content)

    def get_body_title(self):
        for line in self.content.splitlines():
            if line.strip():
                return line

def example():

    for filepath in PathTools().filepaths('./projects/SCG/data/**'):
        docx = Docx(filepath)
        print(f'python-docx ::: {docx.get_body_title()}')
        # print(docx.content)
        # doc = Pandoc(filepath)
        # print(f'pandoc      ::: {doc.get_body_title()}')


if __name__ == '__main__':
    example()

import os
import re
from unidecode import unidecode

remove_chars = str.maketrans(dict.fromkeys('.[]():'))
extra_types = ['behindthescenes', 'deleted', 'featurette', 'interview', 'scene', 'short', 'trailer', 'other']
split_names = ['cd', 'disk', 'disc', 'dvd','part', 'pt']

class Video():
    def __init__(self, row):
        "Initialize a video from a data row"
        self.id = row[0]
        self.title = unidecode(row[1].translate(remove_chars))
        self.year = row[2].split('-')[0]
        self.files = [row[3]]
        self.root_path = row[4]
        
    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())

    def x_standardized_names(self) -> list[str]:
        return list(map(lambda x: f'{self.root_path}\{self.get_name(x)}', self.files))

    def standardized_names(self) -> list[str]:
        return list(map(lambda x: (self.get_folder_name(), self.get_file_name(x)), self.files))

    def get_standard_name(self) -> str:
        return f"{self.title} ({self.year})"

    def get_folder_name(self) -> str:
        return self.get_standard_name()
    
    def get_file_name(self, file: str) -> str:
        file = os.path.basename(file).lower()
        file, ext = os.path.splitext(file)
        
        if (len(self.files) > 1):
            if '-' in file:                    
                token = file.split('-')[-1].strip()
                if token in extra_types:
                    return f"{file}{ext}"
                elif any(t in token for t in split_names):
                    if (i := re.findall('\d+', token)):
                        return f"{self.get_standard_name()} - part {i[0]}{ext}"
                    else:
                        return f"{self.get_standard_name()} - {token}{ext}"

            return f"{self.get_standard_name()}{ext}"    
            #return f"{file}{ext}"
        else:
            return f"{self.get_standard_name()}{ext}"
"""
    def get_folder_name(self, file: str) -> str:
        file = os.path.basename(file).lower()
        file, ext = os.path.splitext(file)
        
        if (len(self.files) > 1):
            if '-' in file:                    
                token = file.split('-')[-1].strip()
                if token in extra_types:
                    return f"{self.title} ({self.year})/{file}{ext}"
                elif any(t in token for t in split_names):
                    if (i := re.findall('\d+', token)):
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - part {i[0]}{ext}"
                    else:
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - {token}{ext}"
                
            return f"{self.title} ({self.year})/{file}{ext}"
        else:
            return f"{self.title} ({self.year})/{self.title} ({self.year}){ext}"

        return template
    
    def get_good_name(self, file: str) -> str:
        file = os.path.basename(file).lower()
        file, ext = os.path.splitext(file)
        
        if (len(self.files) > 1):
            if '-' in file:                    
                token = file.split('-')[-1].strip()
                if token in extra_types:
                    return f"{self.title} ({self.year})/{file}{ext}"
                elif any(t in token for t in split_names):
                    if (i := re.findall('\d+', token)):
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - part {i[0]}{ext}"
                    else:
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - {token}{ext}"
                
            return f"{self.title} ({self.year})/{file}{ext}"
        else:
            return f"{self.title} ({self.year})/{self.title} ({self.year}){ext}"

        return template


    def get_name(self, file: str) -> str:
        file = os.path.basename(file).lower()
        file, ext = os.path.splitext(file)
        
        if (len(self.files) > 1):
            if '-' in file:                    
                token = file.split('-')[-1].strip()
                if token in extra_types:
                    return f"{self.title} ({self.year})/{file}{ext}"
                elif any(t in token for t in split_names):
                    if (i := re.findall('\d+', token)):
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - part {i[0]}{ext}"
                    else:
                        return f"{self.title} ({self.year})/{self.title} ({self.year}) - {token}{ext}"
                
            return f"{self.title} ({self.year})/{file}{ext}"
        else:
            return f"{self.title} ({self.year})/{self.title} ({self.year}){ext}"

        return template
"""
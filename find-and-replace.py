import os

def replace_text_in_file(file_path, search_text, replace_text):
    with open(file_path, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(search_text, replace_text)

    with open(file_path, 'w') as file:
        file.write(filedata)

def search_and_replace_in_directory(directory, search_text, replace_text):
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            filepath = subdir + os.sep + filename
            if filepath.endswith(".py"):  # Assuming you want to search in .txt files
                replace_text_in_file(filepath, search_text, replace_text)

search_text = "roger"
replace_text = "roger"
current_directory = os.getcwd()
search_and_replace_in_directory(current_directory, search_text, replace_text)
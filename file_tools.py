import os

def clean_file_open(filepath, readOrWrite, writingContent=None, extraWarn=None, truncate=None):
    if type(readOrWrite) != str:
        print("for argument 2 'readOrWrite' enter r or w as a STRING")
    if extraWarn != None:
        if type(extraWarn) != str:
            print("for OPTIONAL argument 4 `extraWarn` enter your warning as a STRING")
    else:
        extraWarn  = ""
    if readOrWrite == "w":
        if writingContent == None:
            print("you must provide writingContent argument if using w as 2nd argument")
        else:
            try:
                f = open(filepath, "w")
                f.write(str(writingContent))
                if truncate == True:
                    f.truncate()
                f.close()
            except:
                print("cant write ", writingContent, "to:", filePath, "\n", extraWarn)
    elif readOrWrite == "r":
        if os.path.isfile(filepath) == True:
            f = open(filepath, "r")
            content = f.read()
            f.close()
            return content
        else:
            print(filepath, "cannot be found!\n", extraWarn)
    else:
        print("unknown argument", readOrWrite , "\nfor argument 2 'readOrWrite' enter r or w as a string")
        
def wait_for_file(path, tries=None):
    if tries == None:
        while True:
            if os.path.isfile(path):
                return
            else:
                time.sleep(1)
                continue
    else:
        if type(tries) != type(int):
            print("tries must be an int type")
        i = 0
        while i < tries:
            if os.path.isfile(path):
                return
            else:
                time.sleep(1)
                i = i + 1
                continue

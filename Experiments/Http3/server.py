import os
from subprocess import Popen
from typing import Dict, Tuple


def main():
    """
    create files in data/ folder
    create html files for each experiment
    start nginx with data/ mounted
    """

    default = HtmlFileBuilder("default")
    default.addWebObject('10MB')
    default.build()

    startServer()


def startServer():
    command = "docker run -p 1001:443/udp --volume `pwd`/data:/data:ro -t saahil/quic"
    cmd = Popen(command, shell=True)
    cmd.wait()


class HtmlFileBuilder(object):
    """
    build file with webobjects attached
    """

    objects: Dict[str, Tuple[str, int]] = {}
    htmlFile = ""
    experimentName = "test"

    def __init__(self, experimentName):
        self.experimentName = experimentName

    def addWebObject(self, fileSize: str, count=1, name=False):
        """
        add web object to html file that we are building
        """
        if (not name):
            name = fileSize
        self.objects[name] = (fileSize, count)
        return self

    def createHtmlFile(self, name, fileSize: str):
        filename = f"{name}.html"
        Popen(f"truncate -s {fileSize} ./data/{filename}", shell=True)
        return filename

    def buildFile(self):
        self.htmlFile += "<html><body>"
        for(name, (fileSize, count)) in self.objects.items():
            filename = self.createHtmlFile(name, fileSize)
            for _ in range(count):
                self.htmlFile += f"<object data=\"{filename}\"/>"
        self.htmlFile += "</body></html>"

    def writeFile(self):
        with open('./data/' + self.experimentName + ".html", 'w') as experimentFile:
            experimentFile.write(self.htmlFile)

    def build(self):
        self.buildFile()
        self.writeFile()


if __name__ == "__main__":
    main()

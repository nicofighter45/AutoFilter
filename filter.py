import time
import subprocess

FILTERS = {
    "SEQUENCES POUR UN OF": [["Produit"], ["SN", "S/N", "Texte 2"], ["Nom"]],
    "ACCEPTANCE TEST REPORT": [["Equipment denomination"], ["Equipment revision"], ["Presentation"]]
    }

REMOVE_AT_THE_END = [":", " ", "`", "'", "\\v", "—"]


class Filter:

    def __init__(self, text):
        self._not_detected = []
        self._text = text
        self._name = ""

    def get_name_of_file(self, input_file):
        for document_key in FILTERS.keys():
            if self._text[:50].find(document_key) == -1:
                continue
            for field_keys in FILTERS[document_key]:
                self._get_from_strings(field_keys, field_keys[0])
                self._name += "-"
            break
        else:
            print("no key detected", input_file)
            #subprocess.run(["start", "acrord32", input_file], shell=True)
            #input("Press enter to continue")
            return ""

        if len(self._not_detected) != 0:
            print("not detected", self._not_detected)
            #subprocess.run(["start", "acrord32", input_file], shell=True)
            #input("Press enter to continue")
            return ""

        self._name = self._name[:-1]
        for remove in REMOVE_AT_THE_END:
            self._name = self._name.replace(remove, "")
        if "--" in self._name or self._name[0] == "-" or self._name[-1] == "-":
            print("missing detect", self._name)
            return ""
        print("Successfully filtered", self._name)
        return self._name + ".pdf"

    def _get_from_strings(self, keys, id):
        hasnt_been_called = True
        for i in range(1, 3):
            for k in range(len(keys)):
                key = keys[k]
                try:
                    value = self._text.split(key)[i][:30].split("\n")[0]
                    if len(value) <= 4:
                        value = self._text.split(key)[i][:30].split("\n")[1]
                    if len(value) <= 4 or (k == 1 and not value.replace("à", "").replace(" ", "").isdigit()):
                        continue
                    self._name += value
                    hasnt_been_called = False
                    break              
                except (Exception, IndexError) as e:
                    continue
        if hasnt_been_called:
            self._not_detected.append(id)

import time
import subprocess

FILTERS = {
    "SEQUENCES POUR UN OF": [["Produit"], ["SN", "S/N", "Texte 2"], ["Nom"]],
    "ACCEPTANCE TEST REPORT": [[], ["Equipment revision"], ["Presentation"]]
    }

REMOVE_AT_THE_END = [":", " ", "`", "'", "\\v"]


class Filter:

    def __init__(self, text):
        self._not_detected = []
        self._text = text
        self._name = ""

    def get_name_of_file(self, input_file):
        for document_key in FILTERS.keys():
            if document_key not in self._text:
                print("no key detected")
                #subprocess.run(["start", "acrord32", input_file], shell=True)
                return ""
            for field_keys in FILTERS[document_key]:
                self._get_from_strings(field_keys, field_keys[0])
                self._name += "-"

        if len(self._not_detected) != 0:
            return ""

        self._name = self._name[:-1]
        for remove in REMOVE_AT_THE_END:
            self._name = self._name.replace(remove, "")
        if "--" in self._name or self._name[0] == "-" or self._name[-1] == "-":
            return ""
        return self._name + ".pdf"

    def _get_from_strings(self, keys, id):
        hasnt_been_called = True
        for i in range(1, 3):
            for key in keys:
                try:
                    value = self._text.split(key)[i][:20].split("\n")[0]
                    if len(value) <= 4:
                        value = self._text.split(key)[i][:20].split("\n")[1]
                    if len(value) <= 4:
                        continue
                    self._name += value
                    hasnt_been_called = False
                    break              
                except (Exception, IndexError) as e:
                    continue
        if hasnt_been_called:
            self._not_detected.append(id)

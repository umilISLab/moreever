# TODO: make this dynamic, depending on subdirectories of stories/
# Logic assumes that these have unique first letters

countries = ["Germany", "Italy", "Portugal"]

code2country = {
    "I": "Italy",
    "G": "Germany",
    "P": "Portugal",
    "it": "Italy",
    "de": "Germany",
    "pt": "Portugal",
}

country2idx = {"all": 0, "G": 1, "I": 2, "P": 3}

idx2country = {0: "all", 1: "G", 2: "I", 3: "P"}

initial2code = {"I": "it", "G": "de", "P": "pt"}

from util import get_dirs

corpora = get_dirs()

# TODO: Drop
# code2country = {"it": "Italy", "de": "Germany", "pt": "Portugal"}
# country2code = {"Italy": "it", "Germany": "de", "Portugal": "pt"}
code2country = {c: c for c in corpora}
country2code = {c: c for c in corpora}

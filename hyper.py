from template import list_link_templ, span_templ


def enrich_value(stemmer: str, vocab: str, word: str, stem: str, found=True) -> str:
    title = stem if found else f"{stem} (not found)"
    styled = (
        span_templ.format(
            id=stem + "-tag",
            type=f"{stemmer} {stem}",  # if i == 0 else stemmer,
            title=title,
            content=stem,
        )
        + word[len(stem) :]
    )
    linked = (
        list_link_templ.format(
            id=stem + "-link",
            url=f"/{stemmer}/{vocab}/values/{stem}.html",
            type=f"{stemmer}",
            title=title,
            content=styled,
        )
        if found
        else styled
    )
    return linked

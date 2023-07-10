import roman

"""The data used to scrape the fairy tale corpora from public domain sources.
"""

refs = [
    {
        "name": "Germany",
        "url": "http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/5/3/1/5314/5314-h/5314-h.htm",
        "locator": "//a[@name='%s']/../..",
        "title_locator": "//a[@name='%s']/../text()",
        #             "title_locator": "//a[@name='%s']/following-sibling::text()",
        #         "url": "https://www.gutenberg.org/cache/epub/5314/pg5314-images.html",
        #         "locator": "//a[@id='%s']/../..",
        #             "chapters" : [(f"chap{i:02d}",) for i in [1, 3, 6, 12, 15, 21, 26, 31, 40, 43, 44, 46, 47, 50, 52, 53, 55, 65, 110, 130]]
        "chapters": [(f"chap{i:02d}",) for i in range(1, 201)],
    },
    {
        "name": "Italy",
        "url": "http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/2/3/6/3/23634/23634-h/23634-h.htm",
        #         "url": "https://www.gutenberg.org/files/23634/23634-h/23634-h.htm",
        # "url": "https://ia803102.us.archive.org/23/items/italianpopularta23634gut/23634-h/23634-h.htm",
        "locator": '//*[self::h3 or self::h4][starts-with(text(),"%s")]/following-sibling::*[following::hr[following::*[self::h3 or self::h4][starts-with(text(),"%s")]]]',
        #           //*[self::h3 or self::h4][starts-with(text(),"I.")]/following-sibling::*[following::hr[following::*[self::h3 or self::h4][starts-with(text(),"II.")]]]
        "title_locator": '//*[self::h3 or self::h4][starts-with(text(),"%s")]/text()',
        #         "locator": '//*[self::h3 or self::h4][starts-with(text(),"%s")]/following-sibling::*[following::*[self::h3 or self::h4][starts-with(text(),"%s")]]',
        "chapters": [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.") for i in range(1, 19)
        ]
        # XIX is the last one in the chapter and its ending is not captured well
        + [(f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.") for i in range(20, 36)]
        # LXIX. is mistaken for LIX. as a consequence, the first one is missing and the second one is doubled
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(37, roman.fromRoman("XLVIII"))
        ]
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("L"), roman.fromRoman("LVIII"))
        ]
        # LVIII is not closed well for a reason I have not investigated
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("LIX"), roman.fromRoman("LXXI"))
        ]
        # LXXI is the last one in the chapter and its ending is not captured well
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("LXXII"), roman.fromRoman("LXXIII"))
        ]
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("LXXIV"), roman.fromRoman("LXXXVIII"))
        ]
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("XCI"), roman.fromRoman("CV"))
        ]
        # CV is followed by CVII, and not CVI
        + [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.")
            for i in range(roman.fromRoman("CVI"), roman.fromRoman("CIX"))
        ]
        #         "chapters": [
        #             ("I.", "II."),
        #             ("II.", "III."), # inserted
        #             ("III.", "IV."), # inserted
        #             ("IV.", "V."),
        #             ("V.", "VI."), # inserted
        #             ("VI.", "VII."), # inserted
        #             ("VII.", "VIII."),
        #             ("VIII.", "IX."), # inserted
        #             ("IX.", "X."), # inserted
        #             ("X.", "XI."), # inserted
        #             ("XI.", "XII."), # inserted
        #             ("XII.", "XIII."), # inserted
        #             ("XIII.", "XIV."), # inserted
        #             ("XIV.", "XV."), # inserted
        #             ("XV.", "XVI."),
        #             ("XVI.", "XVII."),
        #             ("XVIII.", "XIX."),
        #             ("XXI.", "XXII."),
        #             ("XXII.", "XXIII."),
        #             ("XXIII.", "XXIV."),
        #             ("XXXIII.", "XXXV."),
        #             ("XLI.", "XLII."),  # has a note inside that needs to be cleaned
        #             ("XLVII.", "XLVIII."),  # text features three variants and (sub)titles
        #             ("L.", "LI."),  # has a note inside that needs to be cleaned
        #             ("LXII.", "LXIII."),  # error # no line separator, but note
        #             ("LXIII.", "LXIV."),  # error # no line separator
        #             ("LXIV.", "LXV."),  # two separators
        #             ("LXXVI.", "LXXVII."),
        #             ("LXXVIII.", "LXXIX."),
        #             ("LXXIX.", "LXXX."),  # has a note inside that needs to be cleaned
        #             ("LXXXI.", "LXXXII."),  # has a note inside that needs to be cleaned
        #             ("LXXXII.", "LXXXIII."),
        #         ]
    },
    {
        "name": "Portugal",
        "url": "https://en.wikisource.org/wiki/Portuguese_Folk-Tales",
        "locator": '//div[@class="prp-pages-output"]//*[starts-with(text(),"%s")]/ancestor::div[1]/following-sibling::*[following::div//*[starts-with(text(),"%s")]]',
        "title_locator": '//div[@class="prp-pages-output"]//*[starts-with(text(),"%s")]//text()',
        "chapters": [
            (f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.") for i in range(1, 17)
        ]
        + [("XVII.", "XVIII—"), ("XVIII—", "XIX.")]
        + [(f"{roman.toRoman(i)}.", f"{roman.toRoman(i+1)}.") for i in range(19, 30)]
        #                 "chapters" : [
        #                     ("I.", "II."),
        #                     ("III.", "IV."),
        #                     ("V.", "VI."),
        #                     ("VI.", "VII."),
        #                     ("IX.", "X."),
        #                     ("X.", "XI."),
        #                     ("XII.", "XIII."),
        #                     ("XIII.", "XIV."),
        #                     ("XIV.", "XV."),
        #                     ("XV.", "XVI."),
        #                     ("XVI.", "XVII."),
        #                     ("XVII.", "XVIII—"),
        #                     ("XVIII—", "XIX."),
        #                     ("XX.", "XXI."),
        #                     ("XXI.", "XXII."),
        #                     ("XXII.", "XXIII."),
        #                     ("XXIII.", "XXVI."),
        #                     ("XXVI.", "XXVII."),
        #                     ("XXVII.", "XXVIII."),
        #                     ("XXIX.", "XXX.")]
    },
]

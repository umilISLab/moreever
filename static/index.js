let init = () => {
    var vocab = document.getElementById("vocab-select");
    var stemmer = document.getElementById("stemmer-select");
    var corpus = document.getElementById("corpus-select");
    var list = document.getElementById("list");
    var fulltext = document.getElementById("fulltext");
    var values = document.getElementById("values");

    let tryUpdate = async (iPossiblyBogusURL) => {
        const response = await fetch(iPossiblyBogusURL);
        
        if (response.status == 200) {
            fulltext.src = iPossiblyBogusURL;
        } else {
            console.log("Unable to find: " + iPossiblyBogusURL)
        }
    }

    let update = () => {
        values.src = stemmer.value + "/" + vocab.value + "/values.html";
        if (corpus.value == "all") {
            list.src = stemmer.value + "/" + vocab.value + "/index.html";
        } else {
            list.src = stemmer.value + "/" + vocab.value + "/" + corpus.value + "/index.html";
        }
        let text_corpus = corpus.value;
        if (text_corpus == "all") {
            const prefix = fulltext.src.substr(0,fulltext.src.lastIndexOf("/"));
            text_corpus = prefix.substr(prefix.lastIndexOf("/")+1);
        }
        // console.log(text_corpus);
        // console.log(prefix);
        // console.log(stemmer.value + "/" + text_corpus + fulltext.src.substr(fulltext.src.lastIndexOf("/")));
        tryUpdate(stemmer.value + "/" + vocab.value + "/" + text_corpus + fulltext.src.substr(fulltext.src.lastIndexOf("/")));
    }

    if (window.location.hash) {
        console.log("Route is " + window.location.hash);
        const url = window.location.hash.replace("/index.html#", "").replace("#", "");
        console.log("URL is " + url);
        tryUpdate(url);
    }

    vocab.addEventListener('change', update);
    stemmer.addEventListener('change', update);
    corpus.addEventListener('change', update);
}


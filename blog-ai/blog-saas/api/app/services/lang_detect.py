"""
Detección simple de idioma basada en palabras clave.
Sin dependencias externas — usa heurísticas de palabras frecuentes.
"""

LANG_MARKERS = {
    "Spanish": ["el","la","los","las","de","en","que","es","por","con","una","un","del","se","no","al","su","más","pero","como","para","este","esta","son","fue","hay","muy"],
    "French": ["le","la","les","de","et","est","en","que","un","une","des","du","pas","je","il","elle","nous","vous","ils","dans","sur","avec","pour","qui","ce","se"],
    "German": ["der","die","das","und","ist","in","von","zu","den","nicht","mit","dem","für","auf","im","ich","sie","er","es","wir","an","bei","nach","auch"],
    "Portuguese": ["de","a","o","que","e","do","da","em","um","para","com","uma","os","no","se","na","por","mais","as","dos","das","mas","ao","ele","das"],
    "Italian": ["di","il","la","e","che","in","un","una","del","per","non","con","si","su","sono","da","ho","hai","è","ma","come","questo","questa","al"],
    "Chinese": ["的","了","在","是","我","有","和","就","不","人","都","一","个","上","也","很","到","说","要","去","你","会","着","没有"],
    "Japanese": ["の","に","は","を","た","が","で","て","と","し","れ","さ","ある","いる","から","など","よ","ね","です","ます"],
    "Arabic": ["في","من","على","إلى","عن","هذا","أن","لا","ما","كان","هو","التي","الذي","بعد","كل","قد","أو"],
}

def detect_language(text: str) -> str:
    if not text:
        return "English"
    
    words = text.lower().split()
    if not words:
        return "English"

    scores = {}
    for lang, markers in LANG_MARKERS.items():
        marker_set = set(markers)
        score = sum(1 for w in words if w.strip(".,;:!?\"'()[]{}") in marker_set)
        scores[lang] = score / max(len(words), 1)

    best_lang = max(scores, key=lambda k: scores[k])
    best_score = scores[best_lang]

    # Si el score es muy bajo, asumir inglés
    if best_score < 0.05:
        return "English"

    return best_lang

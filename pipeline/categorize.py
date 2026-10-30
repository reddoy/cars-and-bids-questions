"""Sort a question into one of the archive's categories using keyword rules.

The rules are checked in order and the first match wins, so a question like
"What's your favorite Porsche?" counts as personal rather than a ranking. The
order was picked to agree best with the hand-checked categories in the
original archive.
"""

import re

CATEGORIES = [
    "Personal Questions",
    "Money & Value",
    "Car Brands",
    "Rankings & Comparisons",
    "Future & Predictions",
    "General",
]

HOSTS = r"doug|filippo|nick|matt|zack|kennan|dan|emily|jaclyn"

RULES = [
    ("Money & Value", r"\$|\bprices?\b|\bcosts?\b|\bworth\b|\bvalues?\b|\bmoney\b|\bbudget|\bafford|\bcheap|\bexpensive|\binvest|\bdepreciat|\bfinanc|\bpaid\b|\bmillion|\bauctions?\b|\d+k\b|\bdeals?\b|\bmarket\b|\bappreciat|\bbuy(ing)?\b|\bbought\b|\bsell(ing)?\b|\bsold\b|\bpurchas|\bgarage\b|\blease|\bdaily\b"),
    ("Personal Questions", rf"\byou\b|\byour\b|\byou'?(d|ve|re|ll)\b|\b({HOSTS})('?s)?\b|\bthe pod\b|\bcars & bids\b|\bcars and bids\b"),
    ("Rankings & Comparisons", r"\brank|\btop \d|\bbest\b|\bworst\b|\bfavou?rite|\bvs\.?\b|\bversus|\bbetter\b|\bcompare|\bwould you rather|\bgreatest|\bmost\b|\bleast\b"),
    ("Car Brands", r"""\b(acura|alfa|aston|audi|bentley|bmw|bugatti|buick|cadillac|chevy|chevrolet|chrysler|citroen|corvettes?|dodge|ferraris?|fiat|ford|genesis|gmc|honda|hummer|hyundai|infiniti|jaguar|jeeps?|kia|koenigsegg|lambos?|lamborghini|lancia|land rover|lexus|lincoln|lotus|lucid|maserati|mazda|mclarens?|mercedes|benz|amg|minis?|mitsubishi|nissan|pagani|peugeot|pontiac|porsches?|ram|rivians?|rolls|saab|saleen|scout|subaru|suzuki|teslas?|toyota|volkswagen|vw|volvo|polestar|datsun|delorean|miatas?|mustangs?|camaros?|supras?|civics?|wrx|sequoias?|land cruisers?|4runners?|tacomas?|broncos?|wranglers?|urus|cayennes?|caymans?|stinger|celestiq|g.?wagons?|model [3sxyq]|cybertruck|[a-z]?\d{2,3}[a-z]?\d?)\b"""),
    ("Future & Predictions", r"\bfuture|\bpredict|\bwill\b|\bnext\b|\bgoing to\b|\bin \d+ years|\b20[3-9]\d\b|\bupcoming"),
    ("Car Brands", r"\bcars?\b|\bvehicles?\b|\bengines?\b|\bv\d+\b|\bmanuals?\b|\bsuvs?\b|\btrucks?\b|\bwagons?\b|\bsupercars?\b|\bsports ?cars?\b|\benthusiast|\bevs?\b|\bhybrids?\b|\bturbo|\bdriv(e|ing|er)s?\b|\bautomotive|\bppf\b|\btires?\b|\bsedans?\b|\bcoupes?\b"),
]


def categorize(question: str) -> str:
    text = question.lower()
    for category, pattern in RULES:
        if re.search(pattern, text):
            return category
    return "General"

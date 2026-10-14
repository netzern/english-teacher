"""Adds the graded levels (basic and up), the placement test and new phrases to content.json.

Run:  python tools/content_levels.py
Idempotent: lessons with the same id are replaced, new ones appended.
Speakable text lives only in "he"/"en"/"heF"/"heM" fields (see gen_audio.py).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content.json"


def H(t): return {"he": t}
def E(t): return {"en": t}


def W(id, en, he, emoji=None, show=None):
    w = {"id": id, "en": en, "he": he}
    if emoji: w["emoji"] = emoji
    if show: w["show"] = show
    return w


def X(en, tr): return {"en": en, "tr": tr}


def pick(word): return {"type": "pick", "word": word}
def listen(word): return {"type": "listen", "word": word}


def fill(q, opts, a, tr, hint=None):
    assert "___" in q and a in opts, (q, a)
    ex = {"type": "fill", "q": q, "opts": opts, "a": a, "full": E(q.replace("___", a)), "tr": tr}
    if hint: ex["hint"] = hint
    return ex


def order(full, tr):
    return {"type": "order", "words": full.rstrip(".?!").split(), "full": E(full), "tr": tr}


LEVELS = [
    {"id": "tiny", "title": "קטנטנים", "options": 2, "age": "3–5"},
    {"id": "starter", "title": "מתחילים", "options": 4, "age": "6–8"},
    {"id": "basic", "title": "בסיס", "options": 4, "age": "8–10"},
    {"id": "explorer", "title": "מתקדמים", "options": 4, "age": "9–11"},
    {"id": "reader", "title": "קוראים", "options": 4, "age": "10–12"},
]

PHRASES = {
    "grammarTime": H("ועכשיו, פינת הדקדוק!"),
    "examplesIntro": H("בואו נשמע כמה דוגמאות"),
    "exercisesIntro": H("עכשיו מתרגלים!"),
    "fillIt": H("השלימו את המשפט"),
    "orderIt": H("סדרו את המילים למשפט"),
    "listenPick": H("תקשיבו ותבחרו את המילה הנכונה"),
    "sayExamples": H("ועכשיו תגידו את המשפטים בקול"),
    "levelUp": H("וואו! סיימתם את כל השיעורים ברמה הזאת. בקשו מאמא או מאבא לעלות רמה!"),
    "talkInvite": H("רוצים לדבר איתי באמת? לחצו על המיקרופון!"),
    "placementIntro": H("בואו נראה כמה אנגלית אתם כבר יודעים! תענו מה שאתם יודעים, וזה בסדר לטעות."),
    "placementDone": H("כל הכבוד! סיימנו. עכשיו ההורים יבחרו את הרמה המתאימה."),
}

BASIC = [
    {"id": "b-tobe", "title": "I am, you are", "icon": "🙋", "intro": H("היום נלמד לדבר על עצמנו ועל אחרים!"),
     "words": [W("I", "I", "אני", "🙋"), W("you", "you", "אתה", "👉"), W("he", "he", "הוא", "👦"), W("she", "she", "היא", "👧"),
               W("it", "it", "זה", "🐶"), W("we", "we", "אנחנו", "👫"), W("they", "they", "הם", "👨‍👩‍👧"),
               W("happy", "happy", "שמח", "😀"), W("sad", "sad", "עצוב", "😢"), W("tired", "tired", "עייף", "😴"),
               W("hungry", "hungry", "רעב", "😋"), W("hot", "hot", "חם", "🥵"), W("cold", "cold", "קר", "🥶"), W("funny", "funny", "מצחיק", "🤪")],
     "grammar": {"title": "am / is / are", "explain": [
         H("באנגלית, בין המילה אני לבין איך אני מרגיש, שמים מילה קטנה."), E("I am happy."),
         H("אחרי אני, תמיד בא"), E("am."),
         H("אחרי הוא, היא, וזה, בא"), E("is."),
         H("ואחרי אתה, אנחנו, והם, בא"), E("are.")],
         "examples": [X("I am happy.", "אני שמח"), X("She is tired.", "היא עייפה"), X("We are hungry.", "אנחנו רעבים"),
                      X("You are funny.", "אתה מצחיק"), X("It is cold.", "קר")]},
     "exercises": [pick("happy"), fill("I ___ happy.", ["am", "is", "are"], "am", "אני שמח"), listen("she"),
                   fill("She ___ tired.", ["am", "is", "are"], "is", "היא עייפה"), order("We are hungry.", "אנחנו רעבים"),
                   fill("They ___ cold.", ["am", "is", "are"], "are", "קר להם"), pick("cold"),
                   fill("He ___ funny.", ["am", "is", "are"], "is", "הוא מצחיק"), listen("we"),
                   order("It is hot.", "חם"), fill("You ___ sad.", ["am", "is", "are"], "are", "אתה עצוב"), listen("tired")]},

    {"id": "b-aan", "title": "a / an ורבים", "icon": "🍎", "intro": H("היום נלמד איך אומרים אחד, ואיך אומרים הרבה!"),
     "words": [W("apple", "apple", "תפוח", "🍎"), W("egg", "egg", "ביצה", "🥚"), W("orange", "orange", "תפוז", "🍊"),
               W("umbrella", "umbrella", "מטרייה", "☂️"), W("elephant", "elephant", "פיל", "🐘"), W("owl", "owl", "ינשוף", "🦉"),
               W("ant", "ant", "נמלה", "🐜"), W("book", "book", "ספר", "📖"), W("cat", "cat", "חתול", "🐱"), W("dog", "dog", "כלב", "🐶"),
               W("ball", "ball", "כדור", "⚽"), W("car", "car", "מכונית", "🚗"), W("banana", "banana", "בננה", "🍌")],
     "grammar": {"title": "a / an / -s", "explain": [
         H("כשיש דבר אחד, שמים לפניו מילה קטנה."), E("a cat. a ball."),
         H("אבל כשהמילה מתחילה בצליל פתוח, כמו אָ, אֶ, אִי, אוֹ, אוּ, אומרים"), E("an apple. an egg."),
         H("וכשיש הרבה, מוסיפים בסוף המילה את הצליל ס."), E("one cat, two cats.")],
         "examples": [X("a dog", "כלב אחד"), X("an apple", "תפוח אחד"), X("an elephant", "פיל אחד"),
                      X("two cats", "שני חתולים"), X("three books", "שלושה ספרים")]},
     "exercises": [fill("___ apple", ["a", "an"], "an", "תפוח"), fill("___ ball", ["a", "an"], "a", "כדור"), pick("umbrella"),
                   fill("___ elephant", ["a", "an"], "an", "פיל"), fill("two ___", ["cat", "cats"], "cats", "שני חתולים"),
                   listen("owl"), fill("___ dog", ["a", "an"], "a", "כלב"), order("It is an orange.", "זה תפוז"),
                   fill("three ___", ["book", "books"], "books", "שלושה ספרים"), fill("___ umbrella", ["a", "an"], "an", "מטרייה"),
                   listen("elephant"), fill("five ___", ["banana", "bananas"], "bananas", "חמש בננות")]},

    {"id": "b-this", "title": "this / that", "icon": "👇", "intro": H("היום נלמד איך מראים על דברים!"),
     "words": [W("this", "this", "זה, קרוב", "👇"), W("that", "that", "זה, רחוק", "☝️"), W("these", "these", "אלה, קרובים", "👇👇"),
               W("those", "those", "אלה, רחוקים", "☝️☝️"), W("pen", "pen", "עט", "🖊️"), W("bag", "bag", "תיק", "🎒"),
               W("chair", "chair", "כיסא", "🪑"), W("door", "door", "דלת", "🚪"), W("window", "window", "חלון", "🪟"),
               W("flower", "flower", "פרח", "🌸"), W("star", "star", "כוכב", "⭐"), W("shoe", "shoe", "נעל", "👟"), W("box", "box", "קופסה", "📦")],
     "grammar": {"title": "this / that / these / those", "explain": [
         H("כשמשהו קרוב אליי, אומרים"), E("this."),
         H("וכשהוא רחוק, אומרים"), E("that."),
         H("כשיש הרבה דברים קרובים, אומרים"), E("these."),
         H("וכשיש הרבה דברים רחוקים, אומרים"), E("those.")],
         "examples": [X("This is a pen.", "זה עט, קרוב"), X("That is a star.", "זה כוכב, רחוק"),
                      X("These are shoes.", "אלה נעליים, קרובות"), X("Those are flowers.", "אלה פרחים, רחוקים")]},
     "exercises": [fill("___ is a pen.", ["This", "That"], "This", "זה עט", "קרוב 👇"),
                   fill("___ is a star.", ["This", "That"], "That", "זה כוכב", "רחוק ☝️"), pick("chair"),
                   fill("___ are shoes.", ["These", "Those"], "These", "אלה נעליים", "הרבה, קרוב 👇"),
                   fill("___ are flowers.", ["These", "Those"], "Those", "אלה פרחים", "הרבה, רחוק ☝️"), listen("door"),
                   fill("These ___ books.", ["is", "are"], "are", "אלה ספרים"), fill("This ___ a box.", ["is", "are"], "is", "זאת קופסה"),
                   order("That is a window.", "זה חלון"), listen("window"), order("These are chairs.", "אלה כיסאות"), pick("bag")]},

    {"id": "b-have", "title": "have / has", "icon": "🐰", "intro": H("היום נלמד להגיד מה יש לנו!"),
     "words": [W("pet", "pet", "חיית מחמד", "🐾"), W("rabbit", "rabbit", "ארנב", "🐰"), W("hamster", "hamster", "אוגר", "🐹"),
               W("parrot", "parrot", "תוכי", "🦜"), W("turtle", "turtle", "צב", "🐢"), W("bike", "bike", "אופניים", "🚲"),
               W("kite", "kite", "עפיפון", "🪁"), W("doll", "doll", "בובה", "🪆"), W("robot", "robot", "רובוט", "🤖"),
               W("sister", "sister", "אחות", "👧"), W("brother", "brother", "אח", "👦"), W("friend", "friend", "חבר", "🤝"),
               W("house", "house", "בית", "🏠")],
     "grammar": {"title": "have / has", "explain": [
         H("כדי להגיד שיש לי משהו, אומרים"), E("I have a bike."),
         H("עם אני, אתה, אנחנו, והם, אומרים"), E("have."),
         H("אבל עם הוא והיא, אומרים"), E("has."), E("She has a rabbit.")],
         "examples": [X("I have a bike.", "יש לי אופניים"), X("She has a rabbit.", "יש לה ארנב"),
                      X("He has a parrot.", "יש לו תוכי"), X("We have a kite.", "יש לנו עפיפון")]},
     "exercises": [fill("I ___ a dog.", ["have", "has"], "have", "יש לי כלב"), fill("She ___ a doll.", ["have", "has"], "has", "יש לה בובה"),
                   pick("parrot"), fill("He ___ a robot.", ["have", "has"], "has", "יש לו רובוט"),
                   fill("They ___ a kite.", ["have", "has"], "have", "יש להם עפיפון"), listen("hamster"),
                   order("I have a rabbit.", "יש לי ארנב"), fill("We ___ two turtles.", ["have", "has"], "have", "יש לנו שני צבים"),
                   fill("My sister ___ a bike.", ["have", "has"], "has", "לאחותי יש אופניים"), order("He has a brother.", "יש לו אח"),
                   listen("kite"), pick("turtle")]},

    {"id": "b-adj", "title": "גדול, קטן, מהיר", "icon": "🦒", "intro": H("היום נלמד מילים שמתארות דברים!"),
     "words": [W("big", "big", "גדול", "🐘"), W("small", "small", "קטן", "🐭"), W("long", "long", "ארוך", "🐍"),
               W("short", "short", "קצר", "📏"), W("tall", "tall", "גבוה", "🦒"), W("fast", "fast", "מהיר", "🚀"),
               W("slow", "slow", "איטי", "🐢"), W("new", "new", "חדש", "✨"), W("old", "old", "ישן", "🏚️"),
               W("clean", "clean", "נקי", "🧼"), W("dirty", "dirty", "מלוכלך", "🐷"), W("beautiful", "beautiful", "יפה", "🌺"),
               W("frog", "frog", "צפרדע", "🐸")],
     "grammar": {"title": "a big red ball", "explain": [
         H("בעברית אומרים כדור גדול: קודם הדבר, ואחר כך התיאור. באנגלית זה הפוך! קודם התיאור, ואחר כך הדבר."), E("a big ball."),
         H("ואם יש גם צבע, הצבע בא ממש לפני הדבר."), E("a big red ball.")],
         "examples": [X("a big dog", "כלב גדול"), X("a small cat", "חתול קטן"), X("a fast red car", "מכונית אדומה מהירה"),
                      X("The giraffe is tall.", "הג'ירפה גבוהה")]},
     "exercises": [order("a big ball", "כדור גדול"), pick("long"), fill("The turtle is ___.", ["fast", "slow"], "slow", "הצב איטי"),
                   order("a small green frog", "צפרדע ירוקה קטנה"), fill("The giraffe is ___.", ["tall", "short"], "tall", "הג'ירפה גבוהה"),
                   listen("old"), fill("A mouse is ___.", ["big", "small"], "small", "עכבר קטן"), order("a fast red car", "מכונית אדומה מהירה"),
                   fill("The rocket is ___.", ["fast", "slow"], "fast", "הטיל מהיר"), listen("clean"), pick("tall"),
                   fill("The pig is ___.", ["clean", "dirty"], "dirty", "החזיר מלוכלך")]},

    {"id": "b-where", "title": "in / on / under", "icon": "📦", "intro": H("היום נלמד להגיד איפה דברים נמצאים!"),
     "words": [W("in", "in", "בתוך", "📥"), W("on", "on", "על", "🔝"), W("under", "under", "מתחת", "⬇️"), W("next", "next to", "ליד", "↔️"),
               W("bed", "bed", "מיטה", "🛏️"), W("sofa", "sofa", "ספה", "🛋️"), W("cup", "cup", "כוס", "☕"), W("box", "box", "קופסה", "📦"),
               W("bag", "bag", "תיק", "🎒"), W("tree", "tree", "עץ", "🌳"), W("mouse", "mouse", "עכבר", "🐭"), W("bird", "bird", "ציפור", "🐦"),
               W("chair", "chair", "כיסא", "🪑")],
     "grammar": {"title": "in / on / under / next to", "explain": [
         H("כדי להגיד איפה משהו נמצא, משתמשים במילים קטנות."),
         E("in."), H("זה בתוך."), E("on."), H("זה על."), E("under."), H("זה מתחת."), E("next to."), H("זה ליד.")],
         "examples": [X("The cat is in the box.", "החתול בתוך הקופסה"), X("The ball is under the bed.", "הכדור מתחת למיטה"),
                      X("The cup is on the chair.", "הכוס על הכיסא"), X("The mouse is next to the tree.", "העכבר ליד העץ")]},
     "exercises": [fill("The cat is ___ the box.", ["in", "on", "under"], "in", "החתול בתוך הקופסה", "בתוך"),
                   fill("The ball is ___ the bed.", ["in", "on", "under"], "under", "הכדור מתחת למיטה", "מתחת"), listen("under"),
                   fill("The cup is ___ the chair.", ["in", "on", "under"], "on", "הכוס על הכיסא", "על"), pick("sofa"),
                   order("The book is in the bag.", "הספר בתוך התיק"),
                   fill("The dog is ___ the tree.", ["next to", "in", "under"], "next to", "הכלב ליד העץ", "ליד"), listen("sofa"),
                   order("The cat is on the sofa.", "החתול על הספה"), fill("The bird is ___ the tree.", ["in", "under"], "in", "הציפור בתוך העץ", "בתוך"),
                   pick("cup"), order("The mouse is under the chair.", "העכבר מתחת לכיסא")]},

    {"id": "b-can", "title": "can / can't", "icon": "🏊", "intro": H("היום נלמד להגיד מה אנחנו יודעים לעשות!"),
     "words": [W("swim", "swim", "לשחות", "🏊"), W("fly", "fly", "לעוף", "🕊️"), W("run", "run", "לרוץ", "🏃"), W("jump", "jump", "לקפוץ", "🦘"),
               W("climb", "climb", "לטפס", "🧗"), W("read", "read", "לקרוא", "📖"), W("write", "write", "לכתוב", "✍️"),
               W("sing", "sing", "לשיר", "🎤"), W("dance", "dance", "לרקוד", "💃"), W("cook", "cook", "לבשל", "🍳"),
               W("walk", "walk", "ללכת", "🚶"), W("ride", "ride a bike", "לרכוב על אופניים", "🚴"), W("draw", "draw", "לצייר", "🎨")],
     "grammar": {"title": "can / can't", "explain": [
         H("כדי להגיד שאני יודע לעשות משהו, אומרים"), E("I can swim."),
         H("וכשלא יודעים, אומרים"), E("I can't fly."),
         H("אחרי המילה הזאת, הפעולה באה בלי שום תוספת. גם עם הוא והיא."), E("She can sing.")],
         "examples": [X("I can swim.", "אני יודע לשחות"), X("A bird can fly.", "ציפור יכולה לעוף"),
                      X("A fish can't walk.", "דג לא יכול ללכת"), X("He can ride a bike.", "הוא יודע לרכוב על אופניים")]},
     "exercises": [fill("A bird ___ fly.", ["can", "can't"], "can", "ציפור יכולה לעוף"), pick("climb"),
                   fill("A fish ___ walk.", ["can", "can't"], "can't", "דג לא יכול ללכת"), listen("cook"),
                   fill("A monkey ___ climb.", ["can", "can't"], "can", "קוף יכול לטפס"), order("I can swim.", "אני יודע לשחות"),
                   fill("She can ___.", ["sing", "sings"], "sing", "היא יודעת לשיר"), fill("A dog ___ read.", ["can", "can't"], "can't", "כלב לא יודע לקרוא"),
                   order("Can you dance?", "אתה יודע לרקוד?"), listen("write"), pick("fly"),
                   fill("A cat ___ fly.", ["can", "can't"], "can't", "חתול לא יכול לעוף")]},

    {"id": "b-questions", "title": "What? Where? Who?", "icon": "❓", "intro": H("היום נלמד לשאול שאלות!"),
     "words": [W("what", "what", "מה", "❓"), W("where", "where", "איפה", "📍"), W("who", "who", "מי", "🧑"),
               W("howmany", "how many", "כמה", "🔢"), W("howold", "how old", "בן כמה", "🎂"), W("name", "name", "שם", "🏷️"),
               W("home", "home", "בית", "🏠"), W("school", "school", "בית ספר", "🏫"), W("teacher", "teacher", "מורה", "🧑‍🏫"),
               W("park", "park", "פארק", "🌳"), W("my", "my", "שלי", "🙋"), W("your", "your", "שלך", "👉")],
     "grammar": {"title": "what / where / who / how", "explain": [
         H("כדי לשאול מה, אומרים"), E("What?"), H("כדי לשאול איפה, אומרים"), E("Where?"),
         H("כדי לשאול מי, אומרים"), E("Who?"), H("כדי לשאול כמה, אומרים"), E("How many?"),
         H("וכדי לשאול מישהו בן כמה הוא, אומרים"), E("How old are you?")],
         "examples": [X("What is your name?", "מה השם שלך?"), X("Where is the ball?", "איפה הכדור?"), X("Who is she?", "מי היא?"),
                      X("How many cats?", "כמה חתולים?"), X("How old are you?", "בן כמה אתה?")]},
     "exercises": [fill("___ is your name?", ["What", "Where", "Who"], "What", "מה השם שלך?"),
                   fill("___ is the dog?", ["What", "Where", "Who"], "Where", "איפה הכלב?", "איפה"), listen("where"),
                   fill("___ is your teacher?", ["What", "Where", "Who"], "Who", "מי המורה שלך?", "מי"),
                   order("What is this?", "מה זה?"), fill("___ old are you?", ["How", "What"], "How", "בן כמה אתה?"), pick("school"),
                   fill("How ___ apples?", ["many", "old"], "many", "כמה תפוחים?"), order("Where is my bag?", "איפה התיק שלי?"),
                   listen("who"), order("How old are you?", "בן כמה אתה?"), pick("home")]},

    {"id": "b-days", "title": "ימי השבוע", "icon": "📅", "intro": H("היום נלמד את ימי השבוע!"),
     "words": [W("sun", "Sunday", "יום ראשון", show="Sunday"), W("mon", "Monday", "יום שני", show="Monday"),
               W("tue", "Tuesday", "יום שלישי", show="Tuesday"), W("wed", "Wednesday", "יום רביעי", show="Wednesday"),
               W("thu", "Thursday", "יום חמישי", show="Thursday"), W("fri", "Friday", "יום שישי", show="Friday"),
               W("sat", "Saturday", "שבת", show="Saturday"), W("today", "today", "היום", "📍"), W("tomorrow", "tomorrow", "מחר", "➡️"),
               W("yesterday", "yesterday", "אתמול", "⬅️"), W("week", "week", "שבוע", "📅")],
     "grammar": {"title": "Sunday, Monday…", "explain": [
         H("באנגלית, ימי השבוע הם שמות, ולכן כותבים אותם תמיד עם אות גדולה בהתחלה. וכולם נגמרים באותה מילה."), E("day!"),
         H("אצלנו בישראל, השבוע מתחיל ביום ראשון."), E("Sunday.")],
         "examples": [X("Today is Sunday.", "היום יום ראשון"), X("Tomorrow is Monday.", "מחר יום שני"),
                      X("I go to school on Monday.", "אני הולך לבית הספר ביום שני"), X("On Saturday we play.", "בשבת אנחנו משחקים")]},
     "exercises": [listen("wed"), fill("Sunday, Monday, ___", ["Tuesday", "Friday"], "Tuesday", "ראשון, שני, שלישי"),
                   listen("thu"), fill("Today is Sunday. Tomorrow is ___.", ["Monday", "Saturday"], "Monday", "היום ראשון, מחר שני"),
                   order("Today is Friday.", "היום יום שישי"), listen("tomorrow"),
                   fill("I go to school ___ Monday.", ["on", "in"], "on", "אני הולך לבית הספר ביום שני"), listen("sat"),
                   fill("There are seven ___ in a week.", ["day", "days"], "days", "יש שבעה ימים בשבוע"), listen("yesterday"),
                   fill("Thursday, Friday, ___", ["Saturday", "Sunday"], "Saturday", "חמישי, שישי, שבת")]},

    {"id": "b-numbers", "title": "מספרים עד 100", "icon": "💯", "intro": H("היום נספור עד מאה!"),
     "words": [W("20", "twenty", "עשרים", show="20"), W("30", "thirty", "שלושים", show="30"), W("40", "forty", "ארבעים", show="40"),
               W("50", "fifty", "חמישים", show="50"), W("60", "sixty", "שישים", show="60"), W("70", "seventy", "שבעים", show="70"),
               W("80", "eighty", "שמונים", show="80"), W("90", "ninety", "תשעים", show="90"), W("100", "one hundred", "מאה", show="100"),
               W("21", "twenty-one", "עשרים ואחת", show="21"), W("35", "thirty-five", "שלושים וחמש", show="35"), W("14", "fourteen", "ארבע עשרה", show="14")],
     "grammar": {"title": "-ty / -teen", "explain": [
         H("כדי לספור בעשרות, מוסיפים בסוף את הצליל טי."), E("sixty, seventy, eighty."),
         H("שימו לב! זה דומה למספרים מאחת עשרה עד תשע עשרה, שנגמרים בצליל טין."), E("fourteen, forty."),
         H("ואם יש עוד יחידות, פשוט מחברים."), E("twenty-one, twenty-two.")],
         "examples": [X("I am nine years old.", "אני בן תשע"), X("My grandpa is seventy.", "סבא שלי בן שבעים"),
                      X("I have fifty stickers.", "יש לי חמישים מדבקות"), X("One hundred is a big number.", "מאה זה מספר גדול")]},
     "exercises": [listen("40"), fill("10, 20, 30, ___", ["forty", "fourteen"], "forty", "עשר, עשרים, שלושים, ארבעים"),
                   listen("14"), fill("twenty + twenty = ___", ["forty", "fourteen"], "forty", "עשרים ועוד עשרים"), listen("90"),
                   fill("fifty + fifty = ___", ["one hundred", "sixty"], "one hundred", "חמישים ועוד חמישים"),
                   order("I am nine years old.", "אני בן תשע"), listen("21"),
                   fill("thirty, forty, ___", ["fifty", "fifteen"], "fifty", "שלושים, ארבעים, חמישים"), listen("70")]},
]
for l in BASIC:
    l["level"] = "basic"

# Placement test: sections from easy to hard; a section is passed with at most one mistake.
PLACEMENT = {
    "sections": [
        {"level": "starter", "pass": "basic", "items": [
            {"type": "pick", "emoji": ["🐶", "🐱", "🐮", "🦆"], "a": 0, "say": E("dog")},
            {"type": "pick", "emoji": ["🔵", "🔴", "🟢", "🟡"], "a": 1, "say": E("red")},
            {"type": "pick", "emoji": ["🍌", "🍞", "🍎", "🥛"], "a": 2, "say": E("apple")},
            {"type": "pick", "emoji": ["4", "7", "3", "9"], "a": 1, "say": E("seven")}]},
        {"level": "basic", "pass": "explorer", "items": [
            fill("I ___ happy.", ["am", "is", "are"], "am", "אני שמח"),
            fill("She ___ a cat.", ["have", "has"], "has", "יש לה חתול"),
            fill("___ apple", ["a", "an"], "an", "תפוח"),
            fill("A fish ___ fly.", ["can", "can't"], "can't", "דג לא יכול לעוף"),
            fill("___ is your name?", ["What", "Who", "Where"], "What", "מה השם שלך?")]},
        {"level": "explorer", "pass": "reader", "items": [
            fill("He ___ football every day.", ["play", "plays"], "plays", "הוא משחק כדורגל כל יום"),
            fill("___ you like pizza?", ["Do", "Does"], "Do", "אתה אוהב פיצה?"),
            fill("Look! They are ___ now.", ["swim", "swimming"], "swimming", "תראה! הם שוחים עכשיו"),
            fill("There ___ three cats.", ["is", "are"], "are", "יש שלושה חתולים")]},
        {"level": "reader", "pass": "reader", "items": [
            fill("Yesterday I ___ to the park.", ["go", "went"], "went", "אתמול הלכתי לפארק"),
            fill("Tomorrow we are going ___ visit grandma.", ["to", "for"], "to", "מחר אנחנו הולכים לבקר את סבתא"),
            fill("The elephant is the ___ animal.", ["big", "biggest"], "biggest", "הפיל הוא החיה הכי גדולה")]},
    ]
}


def main():
    c = json.loads(CONTENT.read_text(encoding="utf-8"))
    c["levels"] = LEVELS
    c["phrases"].update(PHRASES)
    ids = {l["id"]: i for i, l in enumerate(c["lessons"])}
    for l in BASIC:
        if l["id"] in ids:
            c["lessons"][ids[l["id"]]] = l
        else:
            c["lessons"].append(l)
    c["placement"] = PLACEMENT
    # sanity checks
    for l in c["lessons"]:
        wid = {w["id"] for w in l["words"]}
        for ex in l.get("exercises", []):
            if ex["type"] in ("pick", "listen"):
                assert ex["word"] in wid, (l["id"], ex)
                if ex["type"] == "pick":
                    assert next(w for w in l["words"] if w["id"] == ex["word"]).get("emoji"), (l["id"], ex)
    CONTENT.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    print("lessons:", {lv["id"]: sum(1 for l in c["lessons"] if l["level"] == lv["id"]) for lv in LEVELS})


if __name__ == "__main__":
    main()

import json
from collections import Counter
import re

def get_dynamic_clusters(records, query):
    """
    Generate dynamic content-based clusters from a list of records.
    """
    if not records:
        return [], {}

    # 1. Extract potential keywords from titles and descriptions
    stop_words = set([
        "a", "an", "the", "and", "or", "but", "if", "then", "else", "of", "at", "by", "for", "with", "no", "yes",
        "in", "on", "to", "from", "up", "down", "out", "over", "under", "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can", "will",
        "just", "should", "now", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
        "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
        "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
        "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "ca", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would", "could",
        "should", "shall", "must", "might", "it", "its", "they", "them", "their", "theirs", "him", "his", "her", "hers",
        "i", "me", "my", "mine", "you", "your", "yours", "we", "us", "our", "ours", "studies", "study", "drawing", "drawings",
        "print", "prints", "photograph", "photographs", "painting", "paintings", "watercolour", "watercolours", "design",
        "designs", "poster", "posters", "illustration", "illustrations", "card", "cards", "game", "games", "fragment", "fragments",
        "object", "objects", "view", "views", "detail", "details", "title", "titled", "untitled", "signed", "dated", "made",
        "born", "died", "active", "century", "early", "late", "middle", "ca", "approx", "about", "part", "parts", "set", "sets",
        "various", "miscellaneous", "unknown", "probably", "possibly", "likely", "unidentified", "portrait", "landscape", "scene",
        "composition", "sketch", "figure", "figures", "man", "woman", "child", "children", "people", "person", "group", "groups",
        "large", "small", "big", "little", "new", "old", "modern", "ancient", "classic", "classical", "style", "period", "era",
        "work", "works", "art", "artist", "maker", "creator", "production", "manufacture", "craft", "technique", "method", "material",
        "materials", "paper", "wood", "metal", "stone", "clay", "glass", "silk", "cotton", "wool", "textile", "textiles", "fabric",
        "ink", "pencil", "chalk", "pen", "oil", "canvas", "board", "panel", "ivory", "gold", "silver", "bronze", "iron", "steel",
        "copper", "brass", "tin", "lead", "alloy", "ceramic", "porcelain", "pottery", "terracotta", "earthenware", "stoneware",
        "plastic", "resin", "synthetic", "polyurethane", "polyester", "nylon", "acrylic", "acetate", "celluloid", "ivorine",
        "great", "britain", "england", "london", "europe", "western", "north", "south", "east", "west", "british", "french",
        "german", "italian", "spanish", "american", "japanese", "chinese", "indian", "two", "three", "four", "five", "six",
        "seven", "eight", "nine", "ten", "one", "first", "second", "third", "last", "shown", "showing", "depicting", "depict",
        "depicts", "depiction", "image", "images", "picture", "pictures", "photo", "photos", "back", "front", "side", "top",
        "bottom", "left", "right", "center", "centre", "upper", "lower", "inner", "outer", "inside", "outside", "near", "far",
        "background", "foreground", "midground", "distance", "around", "behind", "across", "between", "throughout", "within",
        "without", "towards", "against", "using", "used", "shows", "features", "including", "called", "known", "named",
        "entitled", "titled", "inscribed", "written", "printed", "published", "issued", "produced", "created", "designed",
        "attributed", "after", "copy", "original", "series", "collection", "museum", "gallery", "v&a", "victoria", "albert",
        "given", "bequeathed", "presented", "purchased", "acquired", "accession", "number", "system", "record", "data",
        "bromide", "negative", "negative", "positives", "positive", "gelatin", "albumen", "process", "type", "types",
        "form", "forms", "shape", "shapes", "color", "colour", "colors", "colours", "colored", "coloured", "black", "white",
        "red", "blue", "green", "yellow", "orange", "purple", "brown", "grey", "gray", "pink", "gold", "silver", "metallic",
        "light", "dark", "bright", "soft", "hard", "clear", "plain", "decorated", "ornamented", "pattern", "patterns",
        "decorated", "decorative", "ornamental", "relief", "incised", "painted", "glazed", "unglazed", "polished", "matt",
        "square", "round", "circular", "oval", "rectangular", "oblong", "hexagonal", "octagonal", "pointed", "curved",
        "straight", "flat", "thin", "thick", "heavy", "light", "weight", "width", "height", "depth", "length", "size",
        "dimensions", "measured", "approximate", "roughly", "nearly", "almost", "quite", "rather", "very", "highly",
        "extremely", "somewhat", "slightly", "fairly", "totally", "entirely", "completely", "mostly", "mainly", "chiefly",
        "principally", "largely", "primarily", "especially", "particularly", "notably", "including", "such", "like",
        "drawn", "memory", "animation", "welfare", "photographic", "school", "john", "edwin", "mid", "boy", "girl", "seated",
        "standing", "running", "jumping", "lying", "playing", "working", "holding", "carrying", "wearing", "dressed",
        "uniform", "costume", "clothing", "fashion", "style", "period", "era", "century", "year", "date", "time", "day",
        "night", "morning", "evening", "summer", "winter", "spring", "autumn", "weather", "rain", "snow", "sun", "cloud",
        "mountain", "river", "lake", "sea", "ocean", "beach", "coast", "forest", "wood", "tree", "plant", "flower", "garden",
        "park", "field", "street", "road", "house", "building", "church", "palace", "castle", "room", "interior", "exterior"
    ])

    subjects = set([
        "dog", "cat", "horse", "bird", "fish", "lion", "tiger", "elephant", "bear", "sheep", "cow", "pig", "monkey", "snake",
        "butterfly", "bee", "rabbit", "deer", "fox", "wolf", "mouse", "rat", "duck", "swan", "goose", "chicken", "eagle",
        "owl", "parrot", "penguin", "whale", "dolphin", "shark", "octopus", "crab", "lobster", "spider", "ant", "fly",
        "rose", "lily", "tulip", "sunflower", "daisy", "orchid", "oak", "pine", "palm", "fern", "grass", "apple", "banana",
        "orange", "grape", "cherry", "strawberry", "lemon", "potato", "tomato", "carrot", "onion", "bread", "cheese", "wine",
        "beer", "chair", "table", "sofa", "bed", "cabinet", "desk", "shelf", "lamp", "mirror", "clock", "cup", "plate",
        "knife", "fork", "spoon", "pot", "pan", "bottle", "glass", "bag", "box", "case", "basket", "hat", "coat", "dress",
        "shirt", "pants", "shoes", "boots", "gloves", "umbrella", "jewelry", "ring", "necklace", "bracelet", "watch",
        "book", "pen", "paper", "phone", "camera", "computer", "tv", "radio", "guitar", "piano", "violin", "drum", "ball",
        "doll", "toy", "bicycle", "car", "bus", "train", "ship", "boat", "plane", "house", "church", "bridge", "tower",
        "castle", "palace", "mountain", "river", "lake", "sea", "sun", "moon", "star", "cloud", "rain", "snow", "fire",
        "water", "wind", "earth", "rock", "sand", "gold", "silver", "diamond", "ruby", "emerald", "pearl", "king", "queen",
        "prince", "princess", "knight", "soldier", "sailor", "pilot", "doctor", "nurse", "teacher", "student", "artist",
        "writer", "actor", "musician", "dancer", "chef", "farmer", "worker", "baby", "child", "boy", "girl", "man", "woman",
        "father", "mother", "son", "daughter", "brother", "sister", "friend", "lover", "enemy", "god", "angel", "devil",
        "ghost", "monster", "dragon", "unicorn", "phoenix", "war", "peace", "love", "hate", "life", "death", "health",
        "wealth", "power", "fame", "fortune", "luck", "fate", "nature", "science", "religion", "history", "future",
        "past", "present", "space", "time", "world", "universe", "spirit", "soul", "mind", "body", "heart", "hand", "eye",
        "face", "head", "leg", "arm", "foot", "hair", "skin", "blood", "bone"
    ])

    # Add plurals to subjects
    plural_subjects = set()
    for s in subjects:
        if s.endswith('y'): plural_subjects.add(s[:-1] + 'ies')
        elif s.endswith('s') or s.endswith('x') or s.endswith('ch') or s.endswith('sh'): plural_subjects.add(s + 'es')
        else: plural_subjects.add(s + 's')
    subjects.update(plural_subjects)
    # Special cases
    subjects.update(["feet", "teeth", "children", "men", "women", "geese", "mice"])

    # Add query words to stop words
    query_words = set(re.findall(r'\w+', query.lower()))
    stop_words.update(query_words)
    # Add a few more variants
    for qw in list(query_words):
        if qw.endswith('s'): stop_words.add(qw[:-1])
        else: stop_words.add(qw + 's')

    all_words = []
    item_keywords = []
    
    for rec in records:
        text_content = []
        # Get title
        titles = rec.get("titles", [])
        if titles and isinstance(titles, list):
            text_content.append(titles[0].get("title", ""))
        elif rec.get("objectType"):
            text_content.append(rec.get("objectType", ""))
            
        # Get brief description
        text_content.append(rec.get("briefDescription", ""))
        # Get content concepts
        concepts = rec.get("contentConcepts", [])
        text_content.extend([c.get("text", "") for c in concepts])
        
        full_text = " ".join(text_content).lower()
        words = re.findall(r'\b[a-z]{3,}\b', full_text)
        filtered_words = [w for w in words if w not in stop_words]
        
        all_words.extend(filtered_words)
        item_keywords.append(set(filtered_words))

    # 2. Find top keywords across all items, prioritizing subjects
    subject_counts = Counter([w for w in all_words if w in subjects])
    other_counts = Counter([w for w in all_words if w not in subjects])
    
    top_subjects = [w for w, count in subject_counts.most_common(10)]
    top_others = [w for w, count in other_counts.most_common(10)]
    
    # 3. Assign each item to the most frequent top keyword it contains
    cluster_mapping = {}
    for i, keywords in enumerate(item_keywords):
        sid = records[i].get("systemNumber")
        assigned = "Other"
        
        # First try to find a subject
        for kw in top_subjects:
            if kw in keywords:
                assigned = kw.capitalize()
                break
        
        # If no subject found, try other top keywords
        if assigned == "Other":
            for kw in top_others:
                if kw in keywords:
                    assigned = kw.capitalize()
                    break
                    
        cluster_mapping[sid] = assigned
        
    # 4. Create the clusters list
    final_counts = Counter(cluster_mapping.values())
    clusters = [{"value": k, "count": v} for k, v in final_counts.most_common(12)]
    
    return clusters, cluster_mapping

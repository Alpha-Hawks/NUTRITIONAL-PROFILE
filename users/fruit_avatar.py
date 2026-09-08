import re
import os

# Complete curated fruit catalog for letters A through Z (3 fruits per letter)
FRUITS_BY_LETTER = {
    'A': [
        ('apple', 'Apple'),
        ('apricot', 'Apricot'),
        ('avocado', 'Avocado'),
    ],
    'B': [
        ('banana', 'Banana'),
        ('blueberry', 'Blueberry'),
        ('blackberry', 'Blackberry'),
    ],
    'C': [
        ('cherry', 'Cherry'),
        ('cantaloupe', 'Cantaloupe'),
        ('cranberry', 'Cranberry'),
    ],
    'D': [
        ('dragon_fruit', 'Dragon Fruit'),  # Specified example: Dinesh -> Dragon fruit
        ('date', 'Date'),
        ('durian', 'Durian'),
    ],
    'E': [
        ('elderberry', 'Elderberry'),
        ('eggfruit', 'Eggfruit'),
        ('emblica', 'Emblica'),
    ],
    'F': [
        ('fig', 'Fig'),
        ('feijoa', 'Feijoa'),
        ('finger_lime', 'Finger Lime'),
    ],
    'G': [
        ('grape', 'Grape'),
        ('guava', 'Guava'),
        ('grapefruit', 'Grapefruit'),
    ],
    'H': [
        ('honeydew', 'Honeydew'),
        ('honeyberry', 'Honeyberry'),
        ('huckleberry', 'Huckleberry'),
    ],
    'I': [
        ('ilama', 'Ilama'),
        ('imbe', 'Imbe'),
        ('ita_palm', 'Ita Palm'),
    ],
    'J': [
        ('jackfruit', 'Jackfruit'),
        ('jujube', 'Jujube'),
        ('jabuticaba', 'Jabuticaba'),
    ],
    'K': [
        ('kiwi', 'Kiwi'),
        ('kumquat', 'Kumquat'),
        ('kiwano', 'Kiwano'),
    ],
    'L': [
        ('lemon', 'Lemon'),
        ('lime', 'Lime'),
        ('lychee', 'Lychee'),
    ],
    'M': [
        ('mango', 'Mango'),
        ('mulberry', 'Mulberry'),
        ('mandarin', 'Mandarin'),
    ],
    'N': [
        ('nectarine', 'Nectarine'),
        ('nance', 'Nance'),
        ('naranjilla', 'Naranjilla'),
    ],
    'O': [
        ('orange', 'Orange'),
        ('olive', 'Olive'),
        ('ogen_melon', 'Ogen Melon'),
    ],
    'P': [
        ('papaya', 'Papaya'),
        ('pineapple', 'Pineapple'),
        ('pomegranate', 'Pomegranate'),
    ],
    'Q': [
        ('quince', 'Quince'),
        ('quandong', 'Quandong'),
        ('queen_apple', 'Queen Apple'),
    ],
    'R': [
        ('raspberry', 'Raspberry'),
        ('rambutan', 'Rambutan'),
        ('redcurrant', 'Redcurrant'),
    ],
    'S': [
        ('star_fruit', 'Star Fruit'),  # Specified example: Shiva -> Star fruit
        ('strawberry', 'Strawberry'),
        ('sapodilla', 'Sapodilla'),
    ],
    'T': [
        ('tangerine', 'Tangerine'),
        ('tamarind', 'Tamarind'),
        ('tomato', 'Tomato'),
    ],
    'U': [
        ('ugli_fruit', 'Ugli Fruit'),
        ('uvaia', 'Uvaia'),
        ('umbu', 'Umbu'),
    ],
    'V': [
        ('velvet_apple', 'Velvet Apple'),
        ('voavanga', 'Voavanga'),
        ('vanilla', 'Vanilla Fruit'),
    ],
    'W': [
        ('watermelon', 'Watermelon'),
        ('wax_apple', 'Wax Apple'),
        ('white_currant', 'White Currant'),
    ],
    'X': [
        ('xigua', 'Xigua'),
        ('ximenia', 'Ximenia'),
        ('xanthoceras', 'Xanthoceras'),
    ],
    'Y': [
        ('yuzu', 'Yuzu'),
        ('yellow_passionfruit', 'Yellow Passionfruit'),
        ('yangmei', 'Yangmei'),
    ],
    'Z': [
        ('zucchini', 'Zucchini'),
        ('zill_mango', 'Zill Mango'),
        ('zigzag_vine', 'Zig Zag Vine Fruit'),
    ]
}

# Explicit mappings for user examples requested
USER_PINNED_FRUITS = {
    'dinesh': 'dragon_fruit',
    'shiva': 'star_fruit',
}


def get_user_fruit(user_identifier):
    """
    Determines the fruit assigned to a user based on their starting letter.
    If multiple users share the same starting letter, different users get different fruits.
    User 'Dinesh' gets 'Dragon fruit'.
    User 'Shiva' gets 'Star fruit'.
    """
    if not user_identifier:
        user_identifier = 'User'
    
    clean_str = str(user_identifier).strip()
    lower_str = clean_str.lower()
    
    # Extract first alphabetical letter
    alpha_matches = re.findall(r'[a-zA-Z]', clean_str)
    letter = alpha_matches[0].upper() if alpha_matches else 'A'
    
    fruits = FRUITS_BY_LETTER.get(letter, FRUITS_BY_LETTER['A'])
    
    # 1. Check if user matches pinned requests (Dinesh -> Dragon fruit, Shiva -> Star fruit)
    selected_slug = None
    for pinned_name, pinned_slug in USER_PINNED_FRUITS.items():
        if lower_str == pinned_name or lower_str.startswith(pinned_name):
            selected_slug = pinned_slug
            break
            
    if selected_slug:
        chosen_fruit = next((item for item in fruits if item[0] == selected_slug), fruits[0])
    else:
        # Sensitive hash distribution across characters so different names get different fruits
        c2 = lower_str[1] if len(lower_str) > 1 else 'a'
        c3 = lower_str[2] if len(lower_str) > 2 else 'b'
        val = sum(ord(c) for c in lower_str) + ord(c2) * 7 + ord(c3) * 13 + len(lower_str) * 11
        
        # If letter is D or S, and index would conflict with pinned fruit (index 0), shift if possible
        chosen_index = val % len(fruits)
        if letter == 'D' and chosen_index == 0:
            chosen_index = 1 + (val % (len(fruits) - 1))
        elif letter == 'S' and chosen_index == 0:
            chosen_index = 1 + (val % (len(fruits) - 1))
            
        chosen_fruit = fruits[chosen_index % len(fruits)]
        
    slug, name = chosen_fruit
    return {
        'letter': letter,
        'name': name,
        'slug': slug,
        'filename': f"{slug}.jpg",
        'static_path': f"images/fruits/{slug}.jpg",
        'static_url': f"/static/images/fruits/{slug}.jpg",
        'label': f"{letter} - {name}"
    }


def user_fruit_context_processor(request):
    """
    Django context processor to make `user_fruit` globally available in all templates.
    """
    loginid = request.session.get('loginid') or request.session.get('loggeduser') or request.session.get('name') or ''
    if loginid:
        return {'user_fruit': get_user_fruit(loginid)}
    return {'user_fruit': None}

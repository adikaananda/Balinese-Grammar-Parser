from flask import Flask, render_template, request, jsonify
import re
from collections import defaultdict

app = Flask(__name__)

# ===== VOCABULARY LENGKAP =====
VOCABULARY = {
    'Noun': {'guru', 'pedagang', 'nelayan', 'balian', 'dokter', 'sopir', 'penari', 'mahasiswa', 
             'juru', 'masak', 'petani', 'seniman', 'montir', 'wartawan', 'matematika', 'usada', 
             'motor', 'lawar', 'tukang', 'mebel', 'penjahit', 'kebaya', 'padi', 'banten', 
             'pelukis', 'lukisan', 'arsitek', 'bangunan', 'perawat', 'pasien', 'pilot', 'pesawat', 
             'ukir', 'topeng', 'buruh', 'bapanne', 'memenne', 'pekakne', 'dadongne', 'tunanganne', 
             'bli', 'luh', 'panakne', 'smp', 'pasar', 'segara', 'desa', 'puskesmas', 'hotel', 
             'pura', 'universitas', 'pabrik', 'sawah', 'bengkel', 'tv', 'warung', 'toko', 'jumah', 
             'studio', 'kantor', 'klinik', 'bandara', 'sanggar', 'temboké', 'meongé', 'kranjangé', 
             'siapé', 'dugas', 'sanja', 'bikul', 'tukadé', 'panggung', 'umahné', 'punyan', 'kayuné', 
             'iteh', 'kedisé', 'ujan', 'pulah', 'palih', 'pmi', 'jukut', 'memene', 'jaja', 'peken', 
             'buku', 'cerita', 'perpustakaane', 'panitia', 'lomba', 'warsa', 'kayu', 'bebek', 
             'sampi', 'rahina', 'buah', 'tunangan', 'pekene', 'umah', 'pekak', 'pondokan', 
             'pamalajahan', 'aksara', 'bali', 'aplikasi', 'gegaenan', 'ajengan', 'duur'},
    'PropNoun': {'wayan', 'komang', 'nyoman', 'putu', 'gede', 'ketut', 'made', 'ubud', 'luh', 
                 'sari', 'arya', 'klungkung'},
    'Pronoun': {'tiang', 'ia'},
    'Det': {'niki', 'ento', 'nika', 'punika', 'ne', 'makejang', 'ane', 'para'},
    # Kata non-nomina (untuk klasifikasi saja)
    'Prep': {'ring', 'di', 'anggon', 'betén', 'sisin', 'rikala'},
    'Verb': {'medagang', 'ngelaksanayang', 'ngadep', 'memace', 'nguber', 'memunyi', 'dadi', 'lakar'},
    'Adj': {'jegeg', 'rame', 'tis', 'luung', 'jaen', 'gati', 'sajan', 'seger', 'gelem'},
    'Num': {'seket', 'telung', 'slae', 'sasur', 'diri', 'atus', 'tiban', 'ukud', 'bungkul'},
    'Adv': {'dibi'}
}

# ===== CFG RULES (untuk display) =====
CFG_RULES = [
    {'no': 1, 'kategori': 'Start Symbol', 'nonTerminal': 'S₀', 'rule': 'S₀ → K'},
    {'no': 2, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P S'},
    {'no': 3, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P Pel S'},
    {'no': 4, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P S Ket'},
    {'no': 5, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P Pel S Ket'},
    {'no': 6, 'kategori': 'Komponen Predikat', 'nonTerminal': 'P', 'rule': 'P → NP'},
    {'no': 7, 'kategori': 'Komponen Subjek', 'nonTerminal': 'S', 'rule': 'S → NP'},
    {'no': 8, 'kategori': 'Komponen Pelengkap', 'nonTerminal': 'Pel', 'rule': 'Pel → NP'},
    {'no': 9, 'kategori': 'Komponen Keterangan', 'nonTerminal': 'Ket', 'rule': 'Ket → PP'},
    {'no': 10, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun Det'},
    {'no': 11, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun'},
    {'no': 12, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun Det'},
    {'no': 13, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun'},
    {'no': 14, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun Det'},
    {'no': 15, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun'},
    {'no': 16, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun Noun'},
    {'no': 17, 'kategori': 'Prepositional Phrase', 'nonTerminal': 'PP', 'rule': 'PP → Prep NP'},
    {'no': 18, 'kategori': 'Prepositional Phrase', 'nonTerminal': 'PP', 'rule': 'PP → Prep Noun'},
    {'no': 19, 'kategori': 'Terminal (Noun)', 'nonTerminal': 'Noun', 'rule': "Noun → 'guru' | 'pedagang' | ... (lihat vocabulary)"},
    {'no': 20, 'kategori': 'Terminal (PropNoun)', 'nonTerminal': 'PropNoun', 'rule': "PropNoun → 'wayan' | 'komang' | ..."},
    {'no': 21, 'kategori': 'Terminal (Pronoun)', 'nonTerminal': 'Pronoun', 'rule': "Pronoun → 'tiang' | 'ia'"},
    {'no': 22, 'kategori': 'Terminal (Determiner)', 'nonTerminal': 'Det', 'rule': "Det → 'niki' | 'ento' | ..."},
    {'no': 23, 'kategori': 'Terminal (Preposition)', 'nonTerminal': 'Prep', 'rule': "Prep → 'ring'"},
]

# ===== CNF RULES (untuk display) =====
def generate_cnf_rules_display():
    """Generate CNF rules untuk display"""
    rules = [
        {'no': 1, 'kategori': 'Start Symbol', 'nonTerminal': 'S₀', 'rule': 'S₀ → K'},
        {'no': 2, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → PS_P1'},
        {'no': 3, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → PS_P2'},
        {'no': 4, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → PS_P3'},
        {'no': 5, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → PS_P4'},
        {'no': 6, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'PS_P1', 'rule': 'PS_P1 → P S'},
        {'no': 7, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'PS_P2', 'rule': 'PS_P2 → P_Pel1 S'},
        {'no': 8, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'P_Pel1', 'rule': 'P_Pel1 → P Pel'},
        {'no': 9, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'PS_P3', 'rule': 'PS_P3 → P S_Ket1'},
        {'no': 10, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_Ket1', 'rule': 'S_Ket1 → S Ket'},
        {'no': 11, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'PS_P4', 'rule': 'PS_P4 → P_Pel1 S_Ket1'},
        {'no': 12, 'kategori': 'Komponen Dasar', 'nonTerminal': 'P', 'rule': 'P → N_D2 | N_T2 | PN_D2 | PN_T2 | PR_D2 | PR_T2'},
        {'no': 13, 'kategori': 'Komponen Dasar', 'nonTerminal': 'S', 'rule': 'S → N_D1 | N_T1 | PN_D1 | PN_T1 | PR_D1 | PR_T1'},
        {'no': 14, 'kategori': 'Komponen Dasar', 'nonTerminal': 'Pel', 'rule': 'Pel → N_D3 | N_T3 | PN_D3 | PN_T3 | PR_D3 | PR_T3'},
        {'no': 15, 'kategori': 'Komponen Dasar', 'nonTerminal': 'Ket', 'rule': 'Ket → Prep_NP1'},
        {'no': 16, 'kategori': 'Frasa Nomina', 'nonTerminal': 'N_D1', 'rule': 'N_D1 → Noun Det'},
        {'no': 17, 'kategori': 'Frasa Nomina', 'nonTerminal': 'N_T1', 'rule': 'N_T1 → Noun'},
        {'no': 18, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PN_D1', 'rule': 'PN_D1 → PropNoun Det'},
        {'no': 19, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun Noun Det'},
        {'no': 20, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun Noun Noun'},
        {'no': 21, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun Noun Noun Det'},
        {'no': 22, 'kategori': 'Terminal (Noun)', 'nonTerminal': 'Noun', 'rule': "Noun → 'guru' | 'pedagang' | ... (lihat vocabulary)"},
        {'no': 23, 'kategori': 'Frasa Nomina', 'nonTerminal': 'N_T2', 'rule': 'N_T2 → Noun'},
        {'no': 24, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PN_D2', 'rule': 'PN_D2 → PropNoun Det'},
        {'no': 25, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PN_T2', 'rule': 'PN_T2 → PropNoun'},
        {'no': 26, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PR_D2', 'rule': 'PR_D2 → Pronoun Det'},
        {'no': 27, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PR_T2', 'rule': 'PR_T2 → Pronoun'},
        {'no': 28, 'kategori': 'Frasa Nomina', 'nonTerminal': 'N_D3', 'rule': 'N_D3 → Noun Det'},
        {'no': 29, 'kategori': 'Frasa Nomina', 'nonTerminal': 'N_T3', 'rule': 'N_T3 → Noun'},
        {'no': 30, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PN_D3', 'rule': 'PN_D3 → PropNoun Det'},
        {'no': 31, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PN_T3', 'rule': 'PN_T3 → PropNoun'},
        {'no': 32, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PR_D3', 'rule': 'PR_D3 → Pronoun Det'},
        {'no': 33, 'kategori': 'Frasa Nomina', 'nonTerminal': 'PR_T3', 'rule': 'PR_T3 → Pronoun'},
        {'no': 34, 'kategori': 'Frasa Preposisional', 'nonTerminal': 'Prep_NP1', 'rule': 'Prep_NP1 → Prep NP_PP1'},
        {'no': 35, 'kategori': 'Frasa Preposisional', 'nonTerminal': 'NP_PP1', 'rule': 'NP_PP1 → Noun'},
        {'no': 36, 'kategori': 'Frasa Preposisional', 'nonTerminal': 'NP_PP1', 'rule': 'NP_PP1 → PropNoun'},
        {'no': 37, 'kategori': 'Terminal', 'nonTerminal': 'Noun', 'rule': 'Noun → guru | pedagang | ... (lihat vocabulary)'},
        {'no': 38, 'kategori': 'Terminal', 'nonTerminal': 'PropNoun', 'rule': 'PropNoun → wayan | komang | ...'},
        {'no': 39, 'kategori': 'Terminal', 'nonTerminal': 'Pronoun', 'rule': 'Pronoun → tiang | ia'},
        {'no': 40, 'kategori': 'Terminal', 'nonTerminal': 'Det', 'rule': 'Det → niki | ento | ...'},
        {'no': 41, 'kategori': 'Terminal', 'nonTerminal': 'Prep', 'rule': 'Prep → ring'},
    ]
    return rules

CNF_RULES = generate_cnf_rules_display()

# ===== KALIMAT INVALID =====
INVALID_SENTENCES = [
    {'no': 1, 'kalimat': 'Ring duur temboké meongé', 'jenis': 'Kalimat Berpredikat Frase Preposisi'},
    {'no': 2, 'kalimat': 'Betén kranjangé siapé dugas sanja', 'jenis': 'Kalimat Berpredikat Frase Preposisi'},
    {'no': 3, 'kalimat': 'Ring duur temboké meongé lakar nguber bikul', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 4, 'kalimat': 'Sisin tukadé dadi panggung umahné', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 5, 'kalimat': 'Duur punyan kayuné iteh memunyi kedisé rikala ujan', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 6, 'kalimat': 'Medagang Luh Sari', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 7, 'kalimat': 'Ngelaksanayang pulah palih ne para PMI punika', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 8, 'kalimat': 'Ngadep jukut memene Luh Sari', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 9, 'kalimat': 'Medagang jaja arya di peken Klungkung', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 10, 'kalimat': 'Memace ia buku cerita ring perpustakaane', 'jenis': 'Kalimat Berpredikat Frase Verba'},
    {'no': 11, 'kalimat': 'Seket diri panitia lomba ento', 'jenis': 'Kalimat Berpredikat Frase Numeralia'},
    {'no': 12, 'kalimat': 'Telung atus tiban warsa kayu ento', 'jenis': 'Kalimat Berpredikat Frase Numeralia'},
    {'no': 13, 'kalimat': 'Slae ukud ane gelem bebek ento', 'jenis': 'Kalimat Berpredikat Frase Numeralia'},
    {'no': 14, 'kalimat': 'Slae ukud ane seger sampi ento', 'jenis': 'Kalimat Berpredikat Frase Numeralia'},
    {'no': 15, 'kalimat': 'Sasur bungkul ring pasar rahina puniki buah ento', 'jenis': 'Kalimat Berpredikat Frase Numeralia'},
    {'no': 16, 'kalimat': 'Jegeg gati tunangan tiang', 'jenis': 'Kalimat Berpredikat Frase Adjektiva'},
    {'no': 17, 'kalimat': 'Rame sajan pekene dibi sanja', 'jenis': 'Kalimat Berpredikat Frase Adjektiva'},
    {'no': 18, 'kalimat': 'Tis umah pekak ento anggon pondokan', 'jenis': 'Kalimat Berpredikat Frase Adjektiva'},
    {'no': 19, 'kalimat': 'Luung anggon pamalajahan aksara Bali aplikasi ento', 'jenis': 'Kalimat Berpredikat Frase Adjektiva'},
    {'no': 20, 'kalimat': 'Jaen ajengan gegaenan Luh Sari dibi sanja', 'jenis': 'Kalimat Berpredikat Frase Adjektiva'}
]

# ===== FUNGSI UTILITY =====
def classify_token(token):
    """Klasifikasi kata menggunakan VOCABULARY lengkap"""
    token_lower = token.lower()
    categories = []
    
    category_names = {
        'Noun': 'Kata Benda (Nomina)',
        'PropNoun': 'Nama Diri',
        'Pronoun': 'Kata Ganti (Pronomina)',
        'Det': 'Penentu (Determiner)',
        'Prep': 'Kata Depan (Preposisi)',
        'Verb': 'Kata Kerja (Verba)',
        'Adj': 'Kata Sifat (Adjektiva)',
        'Num': 'Kata Bilangan (Numeralia)',
        'Adv': 'Kata Keterangan (Adverbia)'
    }
    
    for cat, words in VOCABULARY.items():
        if token_lower in words:
            categories.append(category_names.get(cat, cat))
    
    return categories

def analyze_tokens_full(tokens):
    """Analisis token dengan vocabulary lengkap"""
    analysis = []
    unknown_tokens = []
    
    for token in tokens:
        categories = classify_token(token)
        if categories:
            analysis.append({'token': token, 'categories': categories, 'found': True})
        else:
            analysis.append({'token': token, 'categories': [], 'found': False})
            unknown_tokens.append(token)
    
    return analysis, unknown_tokens

def detect_sentence_type(sentence):
    """Deteksi jenis kalimat berdasarkan predikat (kata pertama)"""
    sentence_lower = sentence.lower()
    tokens = sentence_lower.split()
    
    if not tokens:
        return 'Tidak dapat dideteksi', []
    
    invalid_words = []
    first_token = tokens[0]
    sentence_type = 'Kalimat Berpredikat Frase Nomina'
    
    # Cek kategori token pertama
    found_category = None
    for cat, words in VOCABULARY.items():
        if first_token in words:
            found_category = cat
            break
    
    # Deteksi jenis kalimat dan tandai kata invalid
    if found_category == 'Prep':
        sentence_type = 'Kalimat Berpredikat Frase Preposisi'
        invalid_words.append({'token': first_token, 'category': 'Kata Depan (Preposisi)', 'position': 'predikat'})
    elif found_category == 'Verb':
        sentence_type = 'Kalimat Berpredikat Frase Verba'
        invalid_words.append({'token': first_token, 'category': 'Kata Kerja (Verba)', 'position': 'predikat'})
    elif found_category == 'Num':
        sentence_type = 'Kalimat Berpredikat Frase Numeralia'
        invalid_words.append({'token': first_token, 'category': 'Kata Bilangan (Numeralia)', 'position': 'predikat'})
    elif found_category == 'Adj':
        sentence_type = 'Kalimat Berpredikat Frase Adjektiva'
        invalid_words.append({'token': first_token, 'category': 'Kata Sifat (Adjektiva)', 'position': 'predikat'})
    elif found_category == 'Adv':
        sentence_type = 'Kalimat Berpredikat Frase Adverbia'
        invalid_words.append({'token': first_token, 'category': 'Kata Keterangan (Adverbia)', 'position': 'predikat'})
    elif found_category is None:
        invalid_words.append({'token': first_token, 'category': 'Tidak Dikenali', 'position': 'predikat'})
    
    return sentence_type, invalid_words

# ============= CFG PARSER =============
class CFGParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        self.terminals = {
            'Noun': VOCABULARY['Noun'].copy(),
            'PropNoun': VOCABULARY['PropNoun'].copy(),
            'Pronoun': VOCABULARY['Pronoun'].copy(),
            'Det': VOCABULARY['Det'].copy(),
            'Prep': {'ring'}  # Hanya 'ring' untuk keterangan
        }
        self._build_grammar()
    
    def _build_grammar(self):
        """Build CFG grammar untuk kalimat nomina"""
        # Start symbol
        self.grammar['S₀'] = [['K']]
        
        # Struktur kalimat (K menggunakan S untuk subjek)
        self.grammar['K'] = [
            ['P', 'S'], 
            ['P', 'Pel', 'S'], 
            ['P', 'S', 'Ket'], 
            ['P', 'Pel', 'S', 'Ket']
        ]
        
        # Komponen
        self.grammar['P'] = [['NP']]
        self.grammar['S'] = [['NP']]
        self.grammar['Pel'] = [['NP']]
        self.grammar['Ket'] = [['PP']]
        
        # ========== NOUN PHRASE DENGAN STRUKTUR MAJEMUK ==========
        self.grammar['NP'] = [
            ['Noun', 'Det'],              
            ['Noun'],                      
            ['PropNoun', 'Det'],          
            ['PropNoun'],                   
            ['Pronoun', 'Det'],           
            ['Pronoun'],                   
            ['Noun', 'Noun'],              
            ['Noun', 'Noun', 'Det'],      
            ['Noun', 'Noun', 'Noun'],      
            ['Noun', 'Noun', 'Noun', 'Det'] 
        ]
        
        # Prepositional Phrase
        self.grammar['PP'] = [
            ['Prep', 'NP'], 
            ['Prep', 'Noun']
        ]
    
    def parse(self, tokens):
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        # Initialize dengan terminals
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
        
        # Apply unary closure
        for i in range(n):
            self._apply_unary_closure(chart, backpointer, i, i + 1)
        
        # CYK algorithm dengan dukungan hingga 5-ary rules
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                
                # Binary rules
                for k in range(i + 1, j):
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
                # Ternary rules
                if length >= 3:
                    for k1 in range(i + 1, j - 1):
                        for k2 in range(k1 + 1, j):
                            for lhs, productions in self.grammar.items():
                                for prod in productions:
                                    if len(prod) == 3:
                                        A, B, C = prod
                                        if A in chart[i][k1] and B in chart[k1][k2] and C in chart[k2][j]:
                                            if lhs not in chart[i][j]:
                                                chart[i][j].add(lhs)
                                                backpointer[i][j][lhs] = ('ternary', k1, k2, A, B, C)
                
                # Quaternary rules
                if length >= 4:
                    for k1 in range(i + 1, j - 2):
                        for k2 in range(k1 + 1, j - 1):
                            for k3 in range(k2 + 1, j):
                                for lhs, productions in self.grammar.items():
                                    for prod in productions:
                                        if len(prod) == 4:
                                            A, B, C, D = prod
                                            if A in chart[i][k1] and B in chart[k1][k2] and C in chart[k2][k3] and D in chart[k3][j]:
                                                if lhs not in chart[i][j]:
                                                    chart[i][j].add(lhs)
                                                    backpointer[i][j][lhs] = ('quaternary', k1, k2, k3, A, B, C, D)
                
                # ========== TAMBAHAN: 5-ary rules untuk Noun Noun Noun Noun ==========
                if length >= 5:
                    for k1 in range(i + 1, j - 3):
                        for k2 in range(k1 + 1, j - 2):
                            for k3 in range(k2 + 1, j - 1):
                                for k4 in range(k3 + 1, j):
                                    for lhs, productions in self.grammar.items():
                                        for prod in productions:
                                            if len(prod) == 5:
                                                A, B, C, D, E = prod
                                                if (A in chart[i][k1] and 
                                                    B in chart[k1][k2] and 
                                                    C in chart[k2][k3] and 
                                                    D in chart[k3][k4] and 
                                                    E in chart[k4][j]):
                                                    if lhs not in chart[i][j]:
                                                        chart[i][j].add(lhs)
                                                        backpointer[i][j][lhs] = ('quinary', k1, k2, k3, k4, A, B, C, D, E)
                
                self._apply_unary_closure(chart, backpointer, i, j)
        
        token_analysis, unknown_tokens = analyze_tokens_full(tokens)
        
        if 'S₀' in chart[0][n]:
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'S₀')
            return True, tree, token_analysis, None
        else:
            error_details = []
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            if not unknown_tokens and len(chart[0][n]) > 0:
                error_details.append(f"Struktur tidak sesuai grammar P-S. Simbol: {', '.join(chart[0][n])}")
            elif not unknown_tokens:
                error_details.append("Tidak ada struktur valid yang dapat dibentuk")
            
            return False, None, token_analysis, error_details
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        changed = True
        iterations = 0
        
        while changed and iterations < 50:
            changed = False
            iterations += 1
            original = len(chart[i][j])
            
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if len(prod) == 1 and prod[0] in chart[i][j]:
                        if lhs not in chart[i][j]:
                            chart[i][j].add(lhs)
                            backpointer[i][j][lhs] = ('unary', prod[0])
            
            if len(chart[i][j]) > original:
                changed = True
    
    def _build_tree(self, tokens, chart, backpointer, i, j, symbol):
        if symbol not in backpointer[i][j]:
            return {'label': symbol, 'children': []}
        
        bp = backpointer[i][j][symbol]
        
        if bp[0] == 'terminal':
            return {'label': symbol, 'children': [{'label': bp[1], 'children': []}]}
        
        elif bp[0] == 'unary':
            child = self._build_tree(tokens, chart, backpointer, i, j, bp[1])
            return {'label': symbol, 'children': [child]}
        
        elif bp[0] == 'binary':
            k, B, C = bp[1], bp[2], bp[3]
            left = self._build_tree(tokens, chart, backpointer, i, k, B)
            right = self._build_tree(tokens, chart, backpointer, k, j, C)
            return {'label': symbol, 'children': [left, right]}
        
        elif bp[0] == 'ternary':
            k1, k2, A, B, C = bp[1], bp[2], bp[3], bp[4], bp[5]
            c1 = self._build_tree(tokens, chart, backpointer, i, k1, A)
            c2 = self._build_tree(tokens, chart, backpointer, k1, k2, B)
            c3 = self._build_tree(tokens, chart, backpointer, k2, j, C)
            return {'label': symbol, 'children': [c1, c2, c3]}
        
        elif bp[0] == 'quaternary':
            k1, k2, k3, A, B, C, D = bp[1], bp[2], bp[3], bp[4], bp[5], bp[6], bp[7]
            c1 = self._build_tree(tokens, chart, backpointer, i, k1, A)
            c2 = self._build_tree(tokens, chart, backpointer, k1, k2, B)
            c3 = self._build_tree(tokens, chart, backpointer, k2, k3, C)
            c4 = self._build_tree(tokens, chart, backpointer, k3, j, D)
            return {'label': symbol, 'children': [c1, c2, c3, c4]}
        
        elif bp[0] == 'quinary':
            k1, k2, k3, k4, A, B, C, D, E = bp[1], bp[2], bp[3], bp[4], bp[5], bp[6], bp[7], bp[8], bp[9]
            c1 = self._build_tree(tokens, chart, backpointer, i, k1, A)
            c2 = self._build_tree(tokens, chart, backpointer, k1, k2, B)
            c3 = self._build_tree(tokens, chart, backpointer, k2, k3, C)
            c4 = self._build_tree(tokens, chart, backpointer, k3, k4, D)
            c5 = self._build_tree(tokens, chart, backpointer, k4, j, E)
            return {'label': symbol, 'children': [c1, c2, c3, c4, c5]}
        
        return {'label': symbol, 'children': []}
    
# ============= CNF PARSER =============
class CNFParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        self.terminals = {
            'Noun': VOCABULARY['Noun'].copy(),
            'PropNoun': VOCABULARY['PropNoun'].copy(),
            'Pronoun': VOCABULARY['Pronoun'].copy(),
            'Det': VOCABULARY['Det'].copy(),
            'Prep': {'ring'}
        }
        self._build_grammar()
    
    def _build_grammar(self):
        """Build CNF grammar - semua rules harus binary atau unary"""
        
        # ========== START SYMBOL ==========
        self.grammar['S₀'] = [['K']]
        
        # ========== STRUKTUR KALIMAT ==========
        # K → P S | P Pel S | P S Ket | P Pel S Ket
        # Dipecah jadi binary:
        self.grammar['K'] = [
            ['PS_P1'],    # P S
            ['PS_P2'],    # P Pel S
            ['PS_P3'],    # P S Ket
            ['PS_P4']     # P Pel S Ket
        ]
        
        # Binary decomposition
        self.grammar['PS_P1'] = [['P', 'S']]                    # P S
        self.grammar['PS_P2'] = [['P_Pel1', 'S']]               # (P Pel) S
        self.grammar['P_Pel1'] = [['P', 'Pel']]                 # P Pel
        self.grammar['PS_P3'] = [['P', 'S_Ket1']]               # P (S Ket)
        self.grammar['S_Ket1'] = [['S', 'Ket']]                 # S Ket
        self.grammar['PS_P4'] = [['P_Pel1', 'S_Ket1']]          # (P Pel) (S Ket)
        
        # Noun + Det
        self.grammar['N_D'] = [['Noun', 'Det']]
        # PropNoun + Det
        self.grammar['PN_D'] = [['PropNoun', 'Det']]
        # Pronoun + Det
        self.grammar['PR_D'] = [['Pronoun', 'Det']]
        
        # Noun Noun
        self.grammar['NN'] = [['Noun', 'Noun']]
        # Noun Noun Det → (Noun Noun) Det
        self.grammar['NN_D'] = [['NN', 'Det']]
        

        # Noun Noun Noun → (Noun Noun) Noun
        self.grammar['NNN'] = [['NN', 'Noun']]
        # Noun Noun Noun Det → ((Noun Noun) Noun) Det
        self.grammar['NNN_D'] = [['NNN', 'Det']]
        
        # Noun Noun Noun Noun → ((Noun Noun) Noun) Noun
        self.grammar['NNNN'] = [['NNN', 'Noun']]
        # Noun Noun Noun Noun Det → (((Noun Noun) Noun) Noun) Det
        self.grammar['NNNN_D'] = [['NNNN', 'Det']]
        
        # ========== KOMPONEN P, S, PEL (Unary Rules) ==========
        # Semua kemungkinan NP untuk Predikat
        self.grammar['P'] = [
            ['Noun'], ['N_D'],
            ['PropNoun'], ['PN_D'],
            ['Pronoun'], ['PR_D'],
            ['NN'], ['NN_D'],
            ['NNN'], ['NNN_D'],
            ['NNNN'], ['NNNN_D']
        ]
        
        # Semua kemungkinan NP untuk Subjek
        self.grammar['S'] = [
            ['Noun'], ['N_D'],
            ['PropNoun'], ['PN_D'],
            ['Pronoun'], ['PR_D'],
            ['NN'], ['NN_D'],
            ['NNN'], ['NNN_D'],
            ['NNNN'], ['NNNN_D']
        ]
        
        # Semua kemungkinan NP untuk Pelengkap
        self.grammar['Pel'] = [
            ['Noun'], ['N_D'],
            ['PropNoun'], ['PN_D'],
            ['Pronoun'], ['PR_D'],
            ['NN'], ['NN_D'],
            ['NNN'], ['NNN_D'],
            ['NNNN'], ['NNNN_D']
        ]
        
        # ========== PREPOSITIONAL PHRASE ==========
        # Ket → PP → Prep NP
        self.grammar['Ket'] = [['PP']]
        self.grammar['PP'] = [['Prep', 'NP_Ket']]
        
        # NP untuk Keterangan (bisa Noun atau PropNoun saja)
        self.grammar['NP_Ket'] = [
            ['Noun'],
            ['PropNoun'],
            ['N_D'],
            ['PN_D']
        ]
    
    def parse(self, tokens):
        """CYK Algorithm untuk CNF"""
        n = len(tokens)
        
        # Chart untuk menyimpan non-terminals
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        # Backpointer untuk tree reconstruction
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
       
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Cari di terminal vocabulary
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
        
      
        for i in range(n):
            self._apply_unary_closure(chart, backpointer, i, i + 1)
        
       
        for length in range(2, n + 1):  # Panjang span
            for i in range(n - length + 1):  # Start position
                j = i + length  # End position
                
                # Coba semua split point
                for k in range(i + 1, j):
                    # Coba semua binary rules: A → B C
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:  # Binary rule
                                B, C = prod
                                # Jika B ada di chart[i][k] dan C ada di chart[k][j]
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
                # Apply unary closure setelah semua binary rules
                self._apply_unary_closure(chart, backpointer, i, j)
        
        token_analysis, unknown_tokens = analyze_tokens_full(tokens)
        
        if 'S₀' in chart[0][n]:
            # Berhasil di-parse
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'S₀')
            return True, tree, token_analysis, None
        else:
            # Gagal di-parse
            error_details = []
            
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            
            if not unknown_tokens and len(chart[0][n]) > 0:
                error_details.append(f"Struktur tidak sesuai grammar P-S. Simbol yang berhasil dibentuk: {', '.join(chart[0][n])}")
            elif not unknown_tokens:
                error_details.append("Tidak ada struktur valid yang dapat dibentuk dari kalimat ini")
            
            return False, None, token_analysis, error_details
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        """Apply unary rules sampai tidak ada perubahan"""
        changed = True
        iterations = 0
        max_iterations = 100  # Prevent infinite loop
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            original_size = len(chart[i][j])
            
            # Coba semua unary rules: A → B
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if len(prod) == 1:  # Unary rule
                        B = prod[0]
                        # Jika B ada di chart dan A belum ada
                        if B in chart[i][j] and lhs not in chart[i][j]:
                            chart[i][j].add(lhs)
                            backpointer[i][j][lhs] = ('unary', B)
            
            # Cek apakah ada perubahan
            if len(chart[i][j]) > original_size:
                changed = True
    
    def _build_tree(self, tokens, chart, backpointer, i, j, symbol):
        """Reconstruct parse tree dari backpointers"""
        
        # Jika symbol tidak ada di backpointer, return leaf kosong
        if symbol not in backpointer[i][j]:
            return {'label': symbol, 'children': []}
        
        bp = backpointer[i][j][symbol]
        
        if bp[0] == 'terminal':
            # Leaf node (terminal)
            return {
                'label': symbol,
                'children': [{'label': bp[1], 'children': []}]
            }
        
        elif bp[0] == 'unary':
            # Unary rule: A → B
            child_symbol = bp[1]
            child = self._build_tree(tokens, chart, backpointer, i, j, child_symbol)
            return {
                'label': symbol,
                'children': [child]
            }
        
        elif bp[0] == 'binary':
            # Binary rule: A → B C
            k, B, C = bp[1], bp[2], bp[3]
            left = self._build_tree(tokens, chart, backpointer, i, k, B)
            right = self._build_tree(tokens, chart, backpointer, k, j, C)
            return {
                'label': symbol,
                'children': [left, right]
            }
        
        # Fallback
        return {'label': symbol, 'children': []}

# ===== ROUTES =====
@app.route('/')
def index():
    return render_template('index.html', cfg_rules=CFG_RULES, cnf_rules=CNF_RULES, invalid_sentences=INVALID_SENTENCES)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    mode = data.get('mode', 'cfg')
    
    if not sentence:
        return jsonify({'error': 'Silakan masukkan kalimat', 'valid': False})
    
    tokens = sentence.split()
    
    # Siapkan parser
    parser = CFGParser() if mode == 'cfg' else CNFParser()
    
    # Deteksi jenis kalimat
    detected_type, invalid_words = detect_sentence_type(sentence)
    
    # Analisis token menggunakan vocabulary lengkap
    token_analysis, unknown_tokens = analyze_tokens_full(tokens)
    
    # VALIDASI: Cek apakah ada kata non-nomina
    if invalid_words:
        error_details = [
            f"Kalimat terdeteksi sebagai: {detected_type}",
            "Parser hanya menerima Kalimat Berpredikat Frase Nomina"
        ]
        
        for invalid in invalid_words:
            error_details.append(
                f"Kata '{invalid['token']}' adalah {invalid['category']}, tidak diizinkan dalam kalimat nomina"
            )
        
        return jsonify({
            'valid': False,
            'tokens': tokens,
            'error': f'Kalimat mengandung kata non-nomina',
            'error_details': error_details,
            'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
            'token_analysis': token_analysis,
            'sentence_type': detected_type,
            'show_parse_tree': False
        })
    
    # Cek apakah jenis kalimat adalah Nomina
    is_nomina = (detected_type == 'Kalimat Berpredikat Frase Nomina')
    
    # Lakukan parsing
    try:
        valid_structure, parse_tree, token_analysis, parse_errors = parser.parse(tokens)
        
        if valid_structure and is_nomina:
            return jsonify({
                'valid': True,
                'tokens': tokens,
                'message': f'Berhasil mem-parse {len(tokens)} token',
                'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
                'parse_tree': parse_tree,
                'token_analysis': token_analysis,
                'sentence_type': detected_type,
                'show_parse_tree': True
            })
        else:
            error_details = [
                f"Kalimat terdeteksi sebagai: {detected_type}",
                "Parser hanya menerima Kalimat Berpredikat Frase Nomina"
            ]
            
            if parse_errors:
                error_details.extend(parse_errors)
            
            if unknown_tokens:
                unknown_msg = f"Kata tidak dikenali: {', '.join(unknown_tokens)}"
                if unknown_msg not in error_details:
                    error_details.append(unknown_msg)
            
            return jsonify({
                'valid': False,
                'tokens': tokens,
                'error': 'Kalimat tidak valid',
                'error_details': error_details,
                'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
                'token_analysis': token_analysis,
                'sentence_type': detected_type,
                'show_parse_tree': False
            })
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'tokens': tokens,
            'error': f'Error saat parsing: {str(e)}',
            'error_details': [str(e)],
            'sentence_type': detected_type,
            'token_analysis': token_analysis,
            'show_parse_tree': False
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
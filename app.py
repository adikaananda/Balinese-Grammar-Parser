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
    """Generate CNF rules untuk display - sync dengan CNF Parser"""
    rules = [
        # Start Symbol
        {'no': 1, 'kategori': 'Start Symbol', 'nonTerminal': 'S₀', 'rule': 'S₀ → K'},
        
        # Struktur Kalimat (Binary)
        {'no': 2, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P S'},
        {'no': 3, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P_Pel S'},
        {'no': 4, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P S_Ket'},
        {'no': 5, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → P_Pel S_Ket'},
        
        # Helper Binary Decomposition
        {'no': 6, 'kategori': 'Binary Decomposition', 'nonTerminal': 'P_Pel', 'rule': 'P_Pel → P Pel'},
        {'no': 7, 'kategori': 'Binary Decomposition', 'nonTerminal': 'S_Ket', 'rule': 'S_Ket → S Ket'},
        
        # Komponen Kalimat (Unary ke NP)
        {'no': 8, 'kategori': 'Komponen Predikat', 'nonTerminal': 'P', 'rule': 'P → NP'},
        {'no': 9, 'kategori': 'Komponen Subjek', 'nonTerminal': 'S', 'rule': 'S → NP'},
        {'no': 10, 'kategori': 'Komponen Pelengkap', 'nonTerminal': 'Pel', 'rule': 'Pel → NP'},
        {'no': 11, 'kategori': 'Komponen Keterangan', 'nonTerminal': 'Ket', 'rule': 'Ket → PP'},
        
        # Noun Phrase Binary Rules
        {'no': 12, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Noun_Det', 'rule': 'Noun_Det → Noun Det'},
        {'no': 13, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'PropNoun_Det', 'rule': 'PropNoun_Det → PropNoun Det'},
        {'no': 14, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Pronoun_Det', 'rule': 'Pronoun_Det → Pronoun Det'},
        {'no': 15, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Noun_Noun', 'rule': 'Noun_Noun → Noun Noun'},
        {'no': 16, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Noun_Noun_Det', 'rule': 'Noun_Noun_Det → Noun_Noun Det'},
        {'no': 17, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Noun_Noun_Noun', 'rule': 'Noun_Noun_Noun → Noun_Noun Noun'},
        {'no': 18, 'kategori': 'Frasa Nomina Binary', 'nonTerminal': 'Noun_Noun_Noun_Det', 'rule': 'Noun_Noun_Noun_Det → Noun_Noun_Noun Det'},
        
        # NP Unary Rules 
        {'no': 19, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun'},
        {'no': 20, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun_Det'},
        {'no': 21, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun'},
        {'no': 22, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun_Det'},
        {'no': 23, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun'},
        {'no': 24, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun_Det'},
        {'no': 25, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun_Noun'},
        {'no': 26, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun_Noun_Det'},
        {'no': 27, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun_Noun_Noun'},
        {'no': 28, 'kategori': 'Noun Phrase', 'nonTerminal': 'NP', 'rule': 'NP → Noun_Noun_Noun_Det'},
        
        # Prepositional Phrase
        {'no': 29, 'kategori': 'Prepositional Phrase', 'nonTerminal': 'PP', 'rule': 'PP → Prep NP'},
        {'no': 30, 'kategori': 'Prepositional Phrase', 'nonTerminal': 'PP', 'rule': 'PP → Prep Noun'},
        
        # Terminals
        {'no': 31, 'kategori': 'Terminal', 'nonTerminal': 'Noun', 'rule': "Noun → guru | pedagang | ... (lihat vocabulary)"},
        {'no': 32, 'kategori': 'Terminal', 'nonTerminal': 'PropNoun', 'rule': "PropNoun → wayan | komang | ..."},
        {'no': 33, 'kategori': 'Terminal', 'nonTerminal': 'Pronoun', 'rule': "Pronoun → tiang | ia"},
        {'no': 34, 'kategori': 'Terminal', 'nonTerminal': 'Det', 'rule': "Det → niki | ento | ..."},
        {'no': 35, 'kategori': 'Terminal', 'nonTerminal': 'Prep', 'rule': "Prep → ring"},
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
        """Build CNF grammar"""
        
        # Start Symbol
        self.grammar['S₀'] = [['K']]
        
        # Struktur Kalimat (Binary)
        self.grammar['K'] = [
            ['P', 'S'],
            ['P_Pel', 'S'],
            ['P', 'S_Ket'],
            ['P_Pel', 'S_Ket']
        ]
        
        # Helper untuk struktur kompleks
        self.grammar['P_Pel'] = [['P', 'Pel']]
        self.grammar['S_Ket'] = [['S', 'Ket']]
        
        # Noun Phrase Binary Rules
        self.grammar['Noun_Det'] = [['Noun', 'Det']]
        self.grammar['PropNoun_Det'] = [['PropNoun', 'Det']]
        self.grammar['Pronoun_Det'] = [['Pronoun', 'Det']]
        self.grammar['Noun_Noun'] = [['Noun', 'Noun']]
        self.grammar['Noun_Noun_Det'] = [['Noun_Noun', 'Det']]
        self.grammar['Noun_Noun_Noun'] = [['Noun_Noun', 'Noun']]
        self.grammar['Noun_Noun_Noun_Det'] = [['Noun_Noun_Noun', 'Det']]
        self.grammar['Noun_Noun_Noun_Noun'] = [['Noun_Noun_Noun', 'Noun']]
        self.grammar['Noun_Noun_Noun_Noun_Det'] = [['Noun_Noun_Noun_Noun', 'Det']]
        
        # NP (Noun Phrase) - sama seperti CFG
        self.grammar['NP'] = [
            ['Noun'],
            ['Noun_Det'],
            ['PropNoun'],
            ['PropNoun_Det'],
            ['Pronoun'],
            ['Pronoun_Det'],
            ['Noun_Noun'],
            ['Noun_Noun_Det'],
            ['Noun_Noun_Noun'],
            ['Noun_Noun_Noun_Det'],
            ['Noun_Noun_Noun_Noun'],
            ['Noun_Noun_Noun_Noun_Det']
        ]
        
        # Komponen Predikat - pakai NP (sama seperti CFG)
        self.grammar['P'] = [['NP']]
        
        # Komponen Subjek - pakai NP (sama seperti CFG)
        self.grammar['S'] = [['NP']]
        
        # Komponen Pelengkap - pakai NP (sama seperti CFG)
        self.grammar['Pel'] = [['NP']]
        
        # Prepositional Phrase - sama seperti CFG
        self.grammar['Ket'] = [['PP']]
        self.grammar['PP'] = [
            ['Prep', 'NP'],
            ['Prep', 'Noun']
        ]
    
    def parse(self, tokens):
        """CYK Algorithm"""
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        # Initialize terminals
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
        
        # Apply unary closure
        for i in range(n):
            self._apply_unary_closure(chart, backpointer, i, i + 1)
        
        # CYK bottom-up
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                
                for k in range(i + 1, j):
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
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
                error_details.append(f"Struktur tidak sesuai grammar. Simbol: {', '.join(chart[0][n])}")
            elif not unknown_tokens:
                error_details.append("Tidak ada struktur valid")
            
            return False, None, token_analysis, error_details
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        """Apply unary rules"""
        changed = True
        iterations = 0
        
        while changed and iterations < 50:
            changed = False
            iterations += 1
            original_size = len(chart[i][j])
            
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if len(prod) == 1:
                        B = prod[0]
                        if B in chart[i][j] and lhs not in chart[i][j]:
                            chart[i][j].add(lhs)
                            backpointer[i][j][lhs] = ('unary', B)
            
            if len(chart[i][j]) > original_size:
                changed = True
    
    def _build_tree(self, tokens, chart, backpointer, i, j, symbol):
        """Reconstruct parse tree"""
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
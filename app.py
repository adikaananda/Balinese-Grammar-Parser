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


class CFGParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        
        self.terminals = {
            'Noun': VOCABULARY['Noun'].copy(),
            'PropNoun': VOCABULARY['PropNoun'].copy(),
            'Pronoun': VOCABULARY['Pronoun'].copy(),
            'Det': VOCABULARY['Det'].copy(),
            'Prep': VOCABULARY['Prep'].copy(),
            'Verb': VOCABULARY['Verb'].copy(),
            'Adj': VOCABULARY['Adj'].copy(),
            'Num': VOCABULARY['Num'].copy(),
            'Adv': VOCABULARY['Adv'].copy()
        }
        self._build_grammar()
    
    def _build_grammar(self):
        # ========== STRUKTUR KALIMAT ==========
        self.grammar['K'] = [
            ['P', 'S'],              # Predikat + Subjek
            ['P', 'Pel', 'S'],       # Predikat + Pelengkap + Subjek
            ['P', 'S', 'Ket'],       # Predikat + Subjek + Keterangan
            ['P', 'Pel', 'S', 'Ket'] # Lengkap
        ]
        
        # ========== P - PREDIKAT ==========
        self.grammar['P'] = [
            ['Noun'],                     # guru
            ['PropNoun'],                 # Wayan
            ['Pronoun'],                  # tiang
            ['Noun', 'Noun']             # juru masak, tukang ukir
        ]
        
        # ========== Pel - PELENGKAP ==========
        self.grammar['Pel'] = [
            ['Noun'],                     # lawar, topeng, matematika
        ]
        
        # ========== S - SUBJEK ==========
        self.grammar['S'] = [
            ['Noun'],                     
            ['PropNoun'],                
            ['Pronoun'],                  
            ['Noun', 'Det'],             # memenne ne, bapanne niki
            ['PropNoun', 'Det'],           
            ['Pronoun', 'Det'],
            ['Noun', 'Noun'],             
        ]
        
        # ========== Ket - KETERANGAN ==========
        self.grammar['Ket'] = [['PP']]
        
        # ========== PREPOSITIONAL PHRASE ==========
        self.grammar['PP'] = [
            ['Prep', 'Noun'],            # ring warung, di pasar
            ['Prep', 'PropNoun'],        # ring Ubud
            ['Prep', 'Noun', 'Det'],     # ring warung niki
            ['Prep', 'PropNoun', 'Det']  # ring Ubud punika
        ]
    
    def parse(self, tokens):
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        # STEP 1: Terminal initialization
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
        
        # Apply unary closure untuk terminal
        for i in range(n):
            self._apply_unary_closure(chart, backpointer, i, i + 1)
        
        # STEP 2: Bottom-up parsing dengan support untuk production hingga 4 simbol
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                
                # Binary rules (A → B C)
                for k in range(i + 1, j):
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
                # Ternary rules (A → B C D)
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
                
                # Quaternary rules (A → B C D E)
                if length >= 4:
                    for k1 in range(i + 1, j - 2):
                        for k2 in range(k1 + 1, j - 1):
                            for k3 in range(k2 + 1, j):
                                for lhs, productions in self.grammar.items():
                                    for prod in productions:
                                        if len(prod) == 4:
                                            A, B, C, D = prod
                                            if (A in chart[i][k1] and B in chart[k1][k2] and 
                                                C in chart[k2][k3] and D in chart[k3][j]):
                                                if lhs not in chart[i][j]:
                                                    chart[i][j].add(lhs)
                                                    backpointer[i][j][lhs] = ('quaternary', k1, k2, k3, A, B, C, D)
                
                # Apply unary closure setelah semua kombinasi
                self._apply_unary_closure(chart, backpointer, i, j)
        
        # Analyze results
        sentence_type = self._determine_sentence_type_from_tokens(tokens)
        token_analysis, unknown_tokens = analyze_tokens_full(tokens)
        
        # Cek apakah berhasil parse sebagai K
        if 'K' in chart[0][n]:
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'K')
            return True, tree, token_analysis, None, 'Kalimat Berpredikat Frase Nomina'
        else:
            error_details = []
            
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            
            if not unknown_tokens:
                if sentence_type != 'Kalimat Berpredikat Frase Nomina':
                    error_details.append(f"Kalimat terdeteksi sebagai: {sentence_type}")
                    error_details.append("Parser CFG hanya menerima Kalimat Berpredikat Frase Nomina")
                else:
                    if len(chart[0][n]) > 0:
                        error_details.append(f"Struktur tidak sesuai grammar P-S. Simbol yang terbentuk: {', '.join(chart[0][n])}")
                    else:
                        error_details.append("Tidak ada struktur valid yang dapat dibentuk dari kalimat nomina ini")
            
            return False, None, token_analysis, error_details, sentence_type
    
    def _determine_sentence_type_from_tokens(self, tokens):
        if not tokens:
            return 'Tidak dapat dideteksi'
        
        first_word = tokens[0].lower()
        
        if first_word in VOCABULARY['Prep']:
            return 'Kalimat Berpredikat Frase Preposisi'
        elif first_word in VOCABULARY['Verb']:
            return 'Kalimat Berpredikat Frase Verba'
        elif first_word in VOCABULARY['Num']:
            return 'Kalimat Berpredikat Frase Numeralia'
        elif first_word in VOCABULARY['Adj']:
            return 'Kalimat Berpredikat Frase Adjektiva'
        elif first_word in VOCABULARY['Adv']:
            return 'Kalimat Berpredikat Frase Adverbia'
        elif (first_word in VOCABULARY['Noun'] or 
              first_word in VOCABULARY['PropNoun'] or 
              first_word in VOCABULARY['Pronoun'] or
              first_word in VOCABULARY['Det']):
            return 'Kalimat Berpredikat Frase Nomina'
        else:
            return 'Tidak dapat dideteksi'
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        """Apply unary rules (A → B) dengan proteksi cycle"""
        changed = True
        iterations = 0
        max_iterations = 100
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            original_size = len(chart[i][j])
            
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if len(prod) == 1 and prod[0] in chart[i][j]:
                        if lhs not in chart[i][j]:
                            chart[i][j].add(lhs)
                            backpointer[i][j][lhs] = ('unary', prod[0])
            
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
        
        return {'label': symbol, 'children': []}

class CNFParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        self._build_grammar()
    
    def _build_grammar(self):
        """Build CNF grammar - A → BC atau A → a"""
        
        # ========== TERMINALS (A → terminal) ==========
        for word in VOCABULARY['Noun']:
            self.grammar['Noun'].append([word])
        
        for word in VOCABULARY['PropNoun']:
            self.grammar['PropNoun'].append([word])
        
        for word in VOCABULARY['Pronoun']:
            self.grammar['Pronoun'].append([word])
        
        for word in VOCABULARY['Det']:
            self.grammar['Det'].append([word])
        
        for word in VOCABULARY['Prep']:
            self.grammar['Prep'].append([word])
        
        # ========== BINARY RULES (A → BC) ==========
        
        # Noun Phrases
        self.grammar['NP'] = [
            ['Noun', 'Noun']  # tukang ukir
        ]
        
        self.grammar['NP_Det'] = [
            ['Noun', 'Det'],      
            ['PropNoun', 'Det'],  # bli niki
            ['Pronoun', 'Det']
        ]
        
        # Prepositional Phrases
        self.grammar['PP'] = [
            ['Prep', 'Noun'],     # ring sanggar
            ['Prep', 'PropNoun'],
            ['Prep', 'NP_Det']
        ]
        
        # Main Constituents (dengan unary rules)
        self.grammar['P'] = [
            ['Noun'],
            ['PropNoun'],
            ['Pronoun'],
            ['NP']
        ]
        
        self.grammar['Pel'] = [
            ['Noun']
        ]
        
        self.grammar['S'] = [
            ['Noun'],
            ['PropNoun'],
            ['Pronoun'],
            ['NP_Det']
        ]
        
        self.grammar['Ket'] = [
            ['PP']
        ]
        
        # Intermediate Combinations
        self.grammar['P_Pel'] = [
            ['P', 'Pel'],
            ['NP', 'Noun'],
            ['Noun', 'Noun'],
            ['PropNoun', 'Noun'],
            ['Pronoun', 'Noun']
        ]
        
        self.grammar['S_Ket'] = [
            ['S', 'Ket'],
            ['S', 'PP'],
            ['Noun', 'PP'],
            ['PropNoun', 'PP'],
            ['Pronoun', 'PP'],
            ['NP_Det', 'PP'],
            ['Noun', 'Ket'],
            ['PropNoun', 'Ket'],
            ['Pronoun', 'Ket'],
            ['NP_Det', 'Ket']
        ]
        
        self.grammar['P_S'] = [
            ['P', 'S'],
            ['Noun', 'Noun'],
            ['Noun', 'PropNoun'],
            ['Noun', 'Pronoun'],
            ['Noun', 'NP_Det'],
            ['PropNoun', 'Noun'],
            ['PropNoun', 'PropNoun'],
            ['PropNoun', 'Pronoun'],
            ['PropNoun', 'NP_Det'],
            ['Pronoun', 'Noun'],
            ['Pronoun', 'PropNoun'],
            ['Pronoun', 'Pronoun'],
            ['Pronoun', 'NP_Det'],
            ['NP', 'Noun'],
            ['NP', 'PropNoun'],
            ['NP', 'Pronoun'],
            ['NP', 'NP_Det']
        ]
        
        self.grammar['P_Pel_S'] = [
            ['P_Pel', 'S'],
            ['P_Pel', 'Noun'],
            ['P_Pel', 'PropNoun'],
            ['P_Pel', 'Pronoun'],
            ['P_Pel', 'NP_Det']
        ]
        
        # Kalimat
        self.grammar['K'] = [
            ['P', 'S'],
            ['P_S', 'Ket'],
            ['P_S', 'PP'],
            ['P_Pel', 'S'],
            ['P_Pel_S', 'Ket'],
            ['P_Pel_S', 'PP'],
            ['P', 'S_Ket'],
            ['Noun', 'S_Ket'],
            ['PropNoun', 'S_Ket'],
            ['Pronoun', 'S_Ket'],
            ['NP', 'S_Ket']
        ]
    
    def parse(self, tokens):
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        # ========== Terminal initialization ==========
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            # Cari semua non-terminal yang bisa generate token ini
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if len(prod) == 1 and prod[0] == token_lower:
                        chart[i][i + 1].add(lhs)
                        if lhs not in backpointer[i][i + 1]:
                            backpointer[i][i + 1][lhs] = ('terminal', token)
        
        # Apply unary closure untuk terminals
        for i in range(n):
            self._apply_unary_closure(chart, backpointer, i, i + 1)
        
        # ========== CYK Algorithm ==========
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                
                # Try all split points
                for k in range(i + 1, j):
                    # Try all binary rules
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
                # Apply unary closure
                self._apply_unary_closure(chart, backpointer, i, j)
        
        # ========== SAnalyze results ==========
        sentence_type = self._determine_sentence_type(chart, n, tokens)
        token_analysis, unknown_tokens = analyze_tokens_full(tokens)
        
        if 'K' in chart[0][n]:
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'K')
            tree = self._simplify_tree(tree)
            return True, tree, token_analysis, None, sentence_type
        else:
            error_details = []
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            
            if not unknown_tokens:
                found = list(chart[0][n])
                if found:
                    error_details.append(f"Struktur tidak lengkap. Simbol terbentuk: {', '.join(found)}")
                else:
                    error_details.append("Tidak ada struktur valid yang dapat dibentuk")
            
            return False, None, token_analysis, error_details, sentence_type
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        """Apply unary rules A → B"""
        changed = True
        iterations = 0
        max_iterations = 50
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            current_symbols = list(chart[i][j])
            
            for symbol in current_symbols:
                for lhs, productions in self.grammar.items():
                    for prod in productions:
                        if len(prod) == 1 and prod[0] == symbol:
                            if lhs not in chart[i][j]:
                                chart[i][j].add(lhs)
                                if lhs not in backpointer[i][j]:
                                    backpointer[i][j][lhs] = ('unary', symbol)
                                changed = True
    
    def _determine_sentence_type(self, chart, n, tokens):
        """Tentukan jenis kalimat"""
        if 'K' in chart[0][n]:
            return 'Kalimat Berpredikat Frase Nomina'
        
        if tokens:
            first = tokens[0].lower()
            if first in VOCABULARY['Prep']:
                return 'Kalimat Berpredikat Frase Preposisi'
            elif first in VOCABULARY['Verb']:
                return 'Kalimat Berpredikat Frase Verba'
            elif first in VOCABULARY['Num']:
                return 'Kalimat Berpredikat Frase Numeralia'
            elif first in VOCABULARY['Adj']:
                return 'Kalimat Berpredikat Frase Adjektiva'
            elif first in VOCABULARY['Adv']:
                return 'Kalimat Berpredikat Frase Adverbia'
        
        return 'Tidak dapat dideteksi'
    
    def _build_tree(self, tokens, chart, backpointer, i, j, symbol):
        """Reconstruct parse tree - mirip dengan CFG parser"""
        if symbol not in backpointer[i][j]:
            return {'label': symbol, 'children': []}
        
        bp = backpointer[i][j][symbol]
        
        if bp[0] == 'terminal':
            return {
                'label': symbol,
                'children': [{'label': bp[1], 'children': []}]
            }
        
        elif bp[0] == 'unary':
            child_symbol = bp[1]
            child = self._build_tree(tokens, chart, backpointer, i, j, child_symbol)
            return {
                'label': symbol,
                'children': [child]
            }
        
        elif bp[0] == 'binary':
            k, B, C = bp[1], bp[2], bp[3]
            left = self._build_tree(tokens, chart, backpointer, i, k, B)
            right = self._build_tree(tokens, chart, backpointer, k, j, C)
            
            return {
                'label': symbol,
                'children': [left, right]
            }
        
        return {'label': symbol, 'children': []}
    
    def _simplify_tree(self, tree):
        """Simplify tree - keep semua struktur termasuk terminal"""
        if not tree:
            return tree
        
        if tree.get('children'):
            tree['children'] = [
                self._simplify_tree(child) 
                for child in tree['children']
            ]
        
        return tree
    
# ===== ROUTES =====
@app.route('/')
def index():
    return render_template('index.html', invalid_sentences=INVALID_SENTENCES)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    mode = data.get('mode', 'cfg')
    
    if not sentence:
        return jsonify({'error': 'Silakan masukkan kalimat', 'valid': False})
    
    tokens = sentence.split()
    
    # Pilih parser
    parser = CFGParser() if mode == 'cfg' else CNFParser()
    
    # Analisis token untuk cek kata tidak dikenal
    token_analysis, unknown_tokens = analyze_tokens_full(tokens)
    
    # Lakukan parsing - parser akan menentukan jenis kalimat
    try:
        valid_structure, parse_tree, token_analysis, parse_errors, sentence_type = parser.parse(tokens)
        
        # Cek apakah kalimat nomina
        is_nomina = (sentence_type == 'Kalimat Berpredikat Frase Nomina')
        
        if valid_structure and is_nomina:
            return jsonify({
                'valid': True,
                'tokens': tokens,
                'message': f'Berhasil mem-parse {len(tokens)} token',
                'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
                'parse_tree': parse_tree,
                'token_analysis': token_analysis,
                'sentence_type': sentence_type,
                'show_parse_tree': True
            })
        else:
            error_details = [
                f"Kalimat terdeteksi sebagai: {sentence_type}"
            ]
            
            if not is_nomina:
                error_details.append("Parser hanya menerima Kalimat Berpredikat Frase Nomina")
            
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
                'sentence_type': sentence_type,
                'show_parse_tree': False
            })
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'tokens': tokens,
            'error': f'Error saat parsing: {str(e)}',
            'error_details': [str(e)],
            'sentence_type': 'Error',
            'token_analysis': token_analysis,
            'show_parse_tree': False
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
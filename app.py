from flask import Flask, render_template, request, jsonify
import re
from collections import defaultdict

app = Flask(__name__)

# Data CFG Rules
CFG_RULES = [
    {'no': 1, 'kategori': 'Start Symbol', 'nonTerminal': 'S', 'rule': 'S → K'},
    {'no': 2, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S P'},
    {'no': 3, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S P Pel'},
    {'no': 4, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S P Ket'},
    {'no': 5, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S P Pel Ket'},
    {'no': 6, 'kategori': 'Komponen Dasar', 'nonTerminal': 'S', 'rule': 'S → NP'},
    {'no': 7, 'kategori': 'Komponen Dasar', 'nonTerminal': 'P', 'rule': 'P → NP'},
    {'no': 8, 'kategori': 'Komponen Dasar', 'nonTerminal': 'Pel', 'rule': 'Pel → NP'},
    {'no': 9, 'kategori': 'Komponen Dasar', 'nonTerminal': 'Ket', 'rule': 'Ket → PP'},
    {'no': 10, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Noun Det'},
    {'no': 11, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Noun'},
    {'no': 12, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun Det'},
    {'no': 13, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → PropNoun'},
    {'no': 14, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun Det'},
    {'no': 15, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Pronoun'},
    {'no': 16, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Det Noun'},
    {'no': 17, 'kategori': 'Frasa Nomina', 'nonTerminal': 'NP', 'rule': 'NP → Det PropNoun'},
    {'no': 18, 'kategori': 'Frasa Preposisional', 'nonTerminal': 'PP', 'rule': 'PP → Prep NP'},
    {'no': 19, 'kategori': 'Terminal (Nomina)', 'nonTerminal': 'Noun', 'rule': "Noun → 'bapanne' | 'memenne' | 'pekakne' | 'dadongne' | 'tunanganne' | 'bli' | 'luh' | 'panakne' | 'guru' | 'pedagang' | 'nelayan' | 'balian' | 'dokter' | 'sopir' | 'penari' | 'mahasiswa' | 'juru' | 'masak' | 'petani' | 'seniman' | 'montir' | 'wartawan' | 'matematika' | 'usada' | 'motor' | 'lawar' | 'tukang' | 'mebel' | 'penjahit' | 'kebaya' | 'padi' | 'banten' | 'pelukis' | 'lukisan' | 'arsitek' | 'bangunan' | 'perawat' | 'pasien' | 'pilot' | 'pesawat' | 'ukir' | 'topeng' | 'buruh' | 'SMP' | 'pasar' | 'segara' | 'desa' | 'puskesmas' | 'hotel' | 'pura' | 'universitas' | 'pabrik' | 'sawah' | 'bengkel' | 'TV' | 'warung' | 'toko' | 'jumah' | 'studio' | 'kantor' | 'klinik' | 'bandara' | 'sanggar'"},
    {'no': 20, 'kategori': 'Terminal (Nama Diri)', 'nonTerminal': 'PropNoun', 'rule': "PropNoun → 'Wayan' | 'Komang' | 'Nyoman' | 'Putu' | 'Gede' | 'Ketut' | 'Made' | 'Ubud'"},
    {'no': 21, 'kategori': 'Terminal (Pronomina)', 'nonTerminal': 'Pronoun', 'rule': "Pronoun → 'tiang'"},
    {'no': 22, 'kategori': 'Terminal (Determiner)', 'nonTerminal': 'Det', 'rule': "Det → 'niki' | 'ento' | 'nika' | 'punika' | 'ne' | 'makejang'"},
    {'no': 23, 'kategori': 'Terminal (Preposisi)', 'nonTerminal': 'Prep', 'rule': "Prep → 'ring'"}
]

# Data CNF Rules
CNF_RULES = []

def generate_cnf_rules():
    """Generate COMPLETE CNF rules with all alternatives properly expanded"""
    rules = [
        {'no': 1, 'kategori': 'Start Symbol', 'nonTerminal': 'S₀', 'rule': 'S₀ → K'},
        {'no': 2, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S_P1'},
        {'no': 3, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S_P2'},
        {'no': 4, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S_P3'},
        {'no': 5, 'kategori': 'Struktur Kalimat', 'nonTerminal': 'K', 'rule': 'K → S_P4'},
        {'no': 6, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_P1', 'rule': 'S_P1 → S P'},
        {'no': 7, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_P2', 'rule': 'S_P2 → S S_PP1'},
        {'no': 8, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_PP1', 'rule': 'S_PP1 → P Pel'},
        {'no': 9, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_P3', 'rule': 'S_P3 → S S_PK1'},
        {'no': 10, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_PK1', 'rule': 'S_PK1 → P Ket'},
        {'no': 11, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_P4', 'rule': 'S_P4 → S S_PPK1'},
        {'no': 12, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'S_PPK1', 'rule': 'S_PPK1 → P_Pel1 Ket'},
        {'no': 13, 'kategori': 'Struktur Kalimat (Binary)', 'nonTerminal': 'P_Pel1', 'rule': 'P_Pel1 → P Pel'},
    ]
    
    rule_num = 14
    
    # S, P, Pel ke NP
    for component in ['S', 'P', 'Pel']:
        rules.append({
            'no': rule_num,
            'kategori': 'Komponen Dasar',
            'nonTerminal': component,
            'rule': f'{component} → NP'
        })
        rule_num += 1
    
    # Ket ke PP
    rules.append({'no': rule_num, 'kategori': 'Komponen Dasar', 'nonTerminal': 'Ket', 'rule': 'Ket → PP'})
    rule_num += 1
    
    # PP productions
    rules.append({'no': rule_num, 'kategori': 'Frasa Preposisional', 'nonTerminal': 'PP', 'rule': 'PP → Prep NP'})
    rule_num += 1
    
    # NP productions - All alternatives INCLUDING Det Noun and Det PropNoun
    np_rules = [
        ('NP', 'Noun Det'),
        ('NP', 'Noun'),
        ('NP', 'PropNoun Det'),
        ('NP', 'PropNoun'),
        ('NP', 'Pronoun Det'),
        ('NP', 'Pronoun'),
        ('NP', 'Det Noun'),
        ('NP', 'Det PropNoun'),
        ('NP', 'Noun Noun'),  
    ]
    
    for lhs, rhs in np_rules:
        if ' ' in rhs:  # Binary
            parts = rhs.split()
            inter = f'{parts[0]}_{parts[1]}'
            rules.append({'no': rule_num, 'kategori': 'Frasa Nomina', 'nonTerminal': lhs, 'rule': f'{lhs} → {inter}'})
            rule_num += 1
            rules.append({'no': rule_num, 'kategori': 'Frasa Nomina (Binary)', 'nonTerminal': inter, 'rule': f'{inter} → {rhs}'})
            rule_num += 1
        else:  # Unary
            rules.append({'no': rule_num, 'kategori': 'Frasa Nomina', 'nonTerminal': lhs, 'rule': f'{lhs} → {rhs}'})
            rule_num += 1
    
    # Terminal rules - EXPANDED
    nouns = ['bapanne', 'memenne', 'pekakne', 'dadongne', 'tunanganne', 'bli', 'luh', 'panakne', 
             'guru', 'pedagang', 'nelayan', 'balian', 'dokter', 'sopir', 'penari', 'mahasiswa', 
             'juru', 'masak', 'petani', 'seniman', 'montir', 'wartawan', 'matematika', 'usada', 
             'motor', 'lawar', 'tukang', 'mebel', 'penjahit', 'kebaya', 'padi', 'banten', 
             'pelukis', 'lukisan', 'arsitek', 'bangunan', 'perawat', 'pasien', 'pilot', 'pesawat', 
             'ukir', 'topeng', 'buruh', 'smp', 'pasar', 'segara', 'desa', 'puskesmas', 'hotel', 
             'pura', 'universitas', 'pabrik', 'sawah', 'bengkel', 'tv', 'warung', 'toko', 'jumah', 
             'studio', 'kantor', 'klinik', 'bandara', 'sanggar']
    
    for noun in nouns:
        rules.append({'no': rule_num, 'kategori': 'Terminal (Nomina)', 'nonTerminal': 'Noun', 'rule': f'Noun → {noun}'})
        rule_num += 1
    
    propnouns = ['wayan', 'komang', 'nyoman', 'putu', 'gede', 'ketut', 'made', 'ubud']
    for pn in propnouns:
        rules.append({'no': rule_num, 'kategori': 'Terminal (Nama Diri)', 'nonTerminal': 'PropNoun', 'rule': f'PropNoun → {pn}'})
        rule_num += 1
    
    rules.append({'no': rule_num, 'kategori': 'Terminal (Pronomina)', 'nonTerminal': 'Pronoun', 'rule': 'Pronoun → tiang'})
    rule_num += 1
    
    dets = ['niki', 'ento', 'nika', 'punika', 'ne', 'makejang']
    for det in dets:
        rules.append({'no': rule_num, 'kategori': 'Terminal (Determiner)', 'nonTerminal': 'Det', 'rule': f'Det → {det}'})
        rule_num += 1
    
    rules.append({'no': rule_num, 'kategori': 'Terminal (Preposisi)', 'nonTerminal': 'Prep', 'rule': 'Prep → ring'})
    
    return rules

CNF_RULES = generate_cnf_rules()

# ============= CFG PARSER ============= 

class CFGParser:
    """FIXED CFG Parser - Logic identik dengan CNF Parser"""
    
    def __init__(self):
        self.grammar = defaultdict(list)
        self.terminals = defaultdict(set)
        self._build_grammar()
    
    def analyze_tokens(self, tokens):
        """Analisis kategori kata untuk setiap token"""
        analysis = []
        unknown_tokens = []
        
        for token in tokens:
            token_lower = token.lower()
            categories = []
            
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    category_name = {
                        'Noun': 'Nomina (Kata Benda)',
                        'PropNoun': 'PropNoun (Nama Orang)',
                        'Pronoun': 'Pronomina (Kata Ganti)',
                        'Det': 'Determiner (Kata Penentu)',
                        'Prep': 'Preposisi (Kata Depan)'
                    }.get(non_terminal, non_terminal)
                    categories.append(category_name)
            
            if categories:
                analysis.append({'token': token, 'categories': categories, 'found': True})
            else:
                analysis.append({'token': token, 'categories': [], 'found': False})
                unknown_tokens.append(token)
        
        return analysis, unknown_tokens
    
    def _build_grammar(self):
        """Build grammar dari CFG_RULES dengan parsing yang BENAR"""
        for rule in CFG_RULES:
            rule_text = rule['rule']
            if ' → ' in rule_text:
                left, right = rule_text.split(' → ')
                left = left.strip()
                right = right.strip()
                
                if "'" in right or '"' in right:
                    terminals = re.findall(r"['\"\']([^'\"\']*)['\"\']", right)
                    for term in terminals:
                        if term:  
                            self.terminals[left].add(term.lower())
                else:
                    symbols = right.split()
                    if symbols:
                        self.grammar[left].append(symbols)
        
        print(f"\n{'='*60}")
        print(f"CFG GRAMMAR LOADED")
        print(f"{'='*60}")
        print(f"Productions: {len(self.grammar)} non-terminals")
        print(f"Terminals: {len(self.terminals)} categories")
        print(f"{'='*60}\n")
    
    def parse(self, tokens):
        """CYK-style parser SAMA dengan CNF"""
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        print(f"\n{'='*60}")
        print(f"CFG PARSING: {' '.join(tokens)}")
        print(f"{'='*60}\n")
        
        # STEP 1: Terminal Recognition
        print("STEP 1: Terminal Recognition")
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            found = False
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
                    print(f"  [{i},{i+1}] '{token}' → {non_terminal}")
                    found = True
            if not found:
                print(f"  [{i},{i+1}]  '{token}' TIDAK DITEMUKAN!")
        
        # STEP 2: Unary closure
        print("\nSTEP 2: Unary Closure for Terminals")
        for i in range(n):
            before = len(chart[i][i + 1])
            self._apply_unary_closure(chart, backpointer, i, i + 1)
            after = len(chart[i][i + 1])
            if after > before:
                print(f"  [{i},{i+1}] Added: {chart[i][i+1]} (+{after-before})")
        
        # STEP 3: Bottom-up parsing
        print("\nSTEP 3: Bottom-Up Parsing")
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                
                # Binary productions
                for k in range(i + 1, j):
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                
                # Ternary productions
                if length >= 3:
                    for k1 in range(i + 1, j - 1):
                        for k2 in range(k1 + 1, j):
                            for lhs, productions in self.grammar.items():
                                for prod in productions:
                                    if len(prod) == 3:
                                        A, B, C = prod
                                        if (A in chart[i][k1] and B in chart[k1][k2] and C in chart[k2][j]):
                                            if lhs not in chart[i][j]:
                                                chart[i][j].add(lhs)
                                                backpointer[i][j][lhs] = ('ternary', k1, k2, A, B, C)
                
                # Quaternary productions
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
                
                # Apply unary closure
                self._apply_unary_closure(chart, backpointer, i, j)
        
        # Analisis kategori kata
        token_analysis, unknown_tokens = self.analyze_tokens(tokens)
        
        # Check start symbol
        print(f"\n{'='*60}")
        print(f"FINAL CHECK: Chart[0][{n}] = {chart[0][n]}")
        print(f"{'='*60}")
        
        if 'S' in chart[0][n]:
            print("SUCCESS: Start symbol 'S' found!")
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'S')
            return True, tree, token_analysis, None
        else:
            print("FAILED: Start symbol 'S' NOT found!")
            
            error_details = []
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            if not unknown_tokens and len(chart[0][n]) > 0:
                error_details.append(f"Struktur kalimat tidak sesuai grammar. Simbol ditemukan: {', '.join(chart[0][n])}")
            elif not unknown_tokens:
                error_details.append("Tidak ada struktur kalimat yang valid yang dapat dibentuk")
            
            return False, None, token_analysis, error_details
    
    def _apply_unary_closure(self, chart, backpointer, i, j):
        """Apply unary productions hingga fixpoint"""
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
        """Build parse tree"""
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

# ============= CNF PARSER =============
class CNFParser:
    """CNF Parser with proper CYK algorithm - FIXED VERSION"""
    
    def __init__(self):
        self.grammar = defaultdict(list)
        self.terminals = defaultdict(set)
        self._build_grammar()
    
    def analyze_tokens(self, tokens):
        """Analisis kategori kata untuk setiap token"""
        analysis = []
        unknown_tokens = []
        
        for token in tokens:
            token_lower = token.lower()
            categories = []
            
            # Cari kategori untuk token ini
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    # Tentukan nama kategori yang user-friendly
                    category_name = {
                        'Noun': 'Nomina (Kata Benda)',
                        'PropNoun': 'PropNoun (Nama Orang)',
                        'Pronoun': 'Pronomina (Kata Ganti)',
                        'Det': 'Determiner (Kata Penentu)',
                        'Prep': 'Preposisi (Kata Depan)'
                    }.get(non_terminal, non_terminal)
                    
                    categories.append(category_name)
            
            if categories:
                analysis.append({
                    'token': token,
                    'categories': categories,
                    'found': True
                })
            else:
                analysis.append({
                    'token': token,
                    'categories': [],
                    'found': False
                })
                unknown_tokens.append(token)
        
        return analysis, unknown_tokens
    
    def _build_grammar(self):
        """Build grammar from CNF_RULES"""
        for rule in CNF_RULES:
            rule_text = rule['rule']
            if ' → ' in rule_text:
                left, right = rule_text.split(' → ')
                left = left.strip()
                right = right.strip()
                
                symbols = right.split()
                
                if len(symbols) == 1:
                    sym = symbols[0]
                    # Terminal (lowercase or special like 'tv', 'smp')
                    if sym[0].islower() or sym in ['tv', 'smp']:
                        self.terminals[left].add(sym.lower())
                    else:
                        # Unary production
                        self.grammar[left].append(symbols)
                elif len(symbols) == 2:
                    # Binary production
                    self.grammar[left].append(symbols)
        
        print(f"\n{'='*60}")
        print(f"CNF GRAMMAR LOADED")
        print(f"{'='*60}")
        print(f"Productions: {len(self.grammar)} non-terminals")
        print(f"Terminals: {len(self.terminals)} categories")
        print(f"{'='*60}\n")
    
    def parse(self, tokens):
        """Standard CYK Algorithm - CLEAN & EFFICIENT"""
        n = len(tokens)
        chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
        backpointer = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
        
        print(f"\n{'='*60}")
        print(f"CNF PARSING: {' '.join(tokens)}")
        print(f"{'='*60}\n")
        
        # STEP 1: Fill chart with terminals
        print("STEP 1: Terminal Recognition")
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            found = False
            for non_terminal, terms in self.terminals.items():
                if token_lower in terms:
                    chart[i][i + 1].add(non_terminal)
                    backpointer[i][i + 1][non_terminal] = ('terminal', token)
                    print(f"  [{i},{i+1}] '{token}' → {non_terminal}")
                    found = True
            if not found:
                print(f"  [{i},{i+1}] '{token}' TIDAK DITEMUKAN!")
        
        # STEP 2: Apply unary productions to terminals
        print("\nSTEP 2: Unary Closure for Terminals")
        for i in range(n):
            before = len(chart[i][i + 1])
            changed = True
            iterations = 0
            
            while changed and iterations < 50:
                changed = False
                iterations += 1
                original_size = len(chart[i][i + 1])
                
                for lhs, productions in self.grammar.items():
                    for prod in productions:
                        if len(prod) == 1 and prod[0] in chart[i][i + 1]:
                            if lhs not in chart[i][i + 1]:
                                chart[i][i + 1].add(lhs)
                                backpointer[i][i + 1][lhs] = ('unary', prod[0])
                
                if len(chart[i][i + 1]) > original_size:
                    changed = True
            
            after = len(chart[i][i + 1])
            if after > before:
                print(f"  [{i},{i+1}] Added: {chart[i][i+1]} (+{after-before})")
        
        # STEP 3: CYK bottom-up
        print("\nSTEP 3: CYK Bottom-Up Parsing")
        for length in range(2, n + 1):
            print(f"\n--- Length {length} ---")
            for i in range(n - length + 1):
                j = i + length
                print(f"Processing [{i},{j}]:")
                
                # Try all split points k
                for k in range(i + 1, j):
                    for lhs, productions in self.grammar.items():
                        for prod in productions:
                            if len(prod) == 2:
                                B, C = prod
                                if B in chart[i][k] and C in chart[k][j]:
                                    if lhs not in chart[i][j]:
                                        chart[i][j].add(lhs)
                                        backpointer[i][j][lhs] = ('binary', k, B, C)
                                        print(f"  ✓ {lhs} ← {B}[{i},{k}] + {C}[{k},{j}]")
                
                # Apply unary productions
                changed = True
                iterations = 0
                while changed and iterations < 50:
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
                
                if chart[i][j]:
                    print(f"  Final [{i},{j}]: {chart[i][j]}")
        
        # Analisis kategori kata
        token_analysis, unknown_tokens = self.analyze_tokens(tokens)
        
        # FINAL CHECK
        print(f"\n{'='*60}")
        print(f"FINAL CHECK: Chart[0][{n}] = {chart[0][n]}")
        print(f"{'='*60}")
        
        # Check for start symbol
        if 'S₀' in chart[0][n]:
            print("SUCCESS: Start symbol 'S₀' found!")
            tree = self._build_tree(tokens, chart, backpointer, 0, n, 'S₀')
            return True, tree, token_analysis, None
        else:
            print("FAILED: Start symbol 'S₀' NOT found!")
            
            error_details = []
            if unknown_tokens:
                error_details.append(f"Kata tidak dikenali: {', '.join(unknown_tokens)}")
            if not unknown_tokens and len(chart[0][n]) > 0:
                error_details.append(f"Struktur kalimat tidak sesuai grammar. Simbol ditemukan: {', '.join(chart[0][n])}")
            elif not unknown_tokens:
                error_details.append("Tidak ada struktur kalimat yang valid yang dapat dibentuk")
            
            return False, None, token_analysis, error_details
    
    def _build_tree(self, tokens, chart, backpointer, i, j, symbol):
        """Recursively build parse tree"""
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
    return render_template('index.html', cfg_rules=CFG_RULES, cnf_rules=CNF_RULES)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    mode = data.get('mode', 'cfg')
    
    if not sentence:
        return jsonify({'error': 'Silakan masukkan kalimat', 'valid': False})
    
    tokens = sentence.split()
    
    try:
        parser = CFGParser() if mode == 'cfg' else CNFParser()
        valid, parse_tree, token_analysis, error_details = parser.parse(tokens)
        
        if valid:
            return jsonify({
                'valid': True,
                'tokens': tokens,
                'message': f'Berhasil mem-parse {len(tokens)} token',
                'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
                'parse_tree': parse_tree,
                'token_analysis': token_analysis
            })
        else:
            error_message = ' | '.join(error_details) if error_details else 'Kalimat tidak sesuai grammar'
            return jsonify({
                'valid': False,
                'tokens': tokens,
                'error': error_message,
                'error_details': error_details,
                'structure': 'Context-Free Grammar' if mode == 'cfg' else 'Chomsky Normal Form',
                'token_analysis': token_analysis
            })
    except Exception as e:
        return jsonify({'valid': False, 'tokens': tokens, 'error': f'Error: {str(e)}'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

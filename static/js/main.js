let currentTab = 'cfg';

function switchTab(tab) {
    currentTab = tab;
    const cfgBtn = document.getElementById('btn-cfg');
    const cnfBtn = document.getElementById('btn-cnf');

    if (tab === 'cfg') {
        cfgBtn.className = 'tab-btn flex-1 sm:flex-none px-4 sm:px-8 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 bg-amber-600 text-white shadow-lg';
        cnfBtn.className = 'tab-btn flex-1 sm:flex-none px-4 sm:px-8 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 text-gray-300 hover:text-white hover:bg-white/10';
    } else {
        cnfBtn.className = 'tab-btn flex-1 sm:flex-none px-4 sm:px-8 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 bg-amber-600 text-white shadow-lg';
        cfgBtn.className = 'tab-btn flex-1 sm:flex-none px-4 sm:px-8 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 text-gray-300 hover:text-white hover:bg-white/10';
    }
}

function calculateTreeDimensions(node, depth = 0) {
    if (!node || !node.children || node.children.length === 0) {
        return { width: 120, height: 60, leaves: 1 };
    }
    
    let totalWidth = 0;
    let maxHeight = 60;
    let totalLeaves = 0;
    
    for (const child of node.children) {
        const childDim = calculateTreeDimensions(child, depth + 1);
        totalWidth += childDim.width;
        maxHeight = Math.max(maxHeight, childDim.height + 80);
        totalLeaves += childDim.leaves;
    }
    
    return { 
        width: Math.max(totalWidth, 120), 
        height: maxHeight,
        leaves: totalLeaves
    };
}

function renderTreeNode(node, x, y, width, svg, depth = 0) {
    if (!node) return;
    
    const colors = {
        0: { bg: '#7C3AED', text: '#FFFFFF' }, // purple
        1: { bg: '#3B82F6', text: '#FFFFFF' }, // blue
        2: { bg: '#10B981', text: '#FFFFFF' }, // green
        3: { bg: '#F59E0B', text: '#FFFFFF' }  // amber
    };
    
    const color = colors[Math.min(depth, 3)];
    
    // Responsive node dimensions
    const isMobile = window.innerWidth < 640;
    const nodeWidth = isMobile ? 80 : 100;
    const nodeHeight = isMobile ? 32 : 40;
    const fontSize = isMobile ? '11' : '14';
    const verticalSpacing = isMobile ? 60 : 80;
    
    const nodeX = x + (width - nodeWidth) / 2;
    
    // Draw node
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'tree-node');
    
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', nodeX);
    rect.setAttribute('y', y);
    rect.setAttribute('width', nodeWidth);
    rect.setAttribute('height', nodeHeight);
    rect.setAttribute('rx', '8');
    rect.setAttribute('fill', color.bg);
    rect.setAttribute('class', 'drop-shadow-md');
    
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', nodeX + nodeWidth / 2);
    text.setAttribute('y', y + nodeHeight / 2 + (isMobile ? 4 : 5));
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', color.text);
    text.setAttribute('font-weight', 'bold');
    text.setAttribute('font-size', fontSize);
    text.setAttribute('font-family', 'monospace');
    text.textContent = node.label;
    
    g.appendChild(rect);
    g.appendChild(text);
    svg.appendChild(g);
    
    // Draw children
    if (node.children && node.children.length > 0) {
        const childY = y + verticalSpacing;
        const childrenWidth = width / node.children.length;
        
        node.children.forEach((child, i) => {
            const childX = x + i * childrenWidth;
            const childNodeX = childX + (childrenWidth - nodeWidth) / 2 + nodeWidth / 2;
            
            // Draw line from parent to child
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', nodeX + nodeWidth / 2);
            line.setAttribute('y1', y + nodeHeight);
            line.setAttribute('x2', childNodeX);
            line.setAttribute('y2', childY);
            line.setAttribute('stroke', '#CBD5E1');
            line.setAttribute('stroke-width', isMobile ? '1.5' : '2');
            svg.appendChild(line);
            
            renderTreeNode(child, childX, childY, childrenWidth, svg, depth + 1);
        });
    }
}

function renderTree(node) {
    if (!node) return '';
    
    const dimensions = calculateTreeDimensions(node);
    const isMobile = window.innerWidth < 640;
      const isTablet = window.innerWidth >= 640 && window.innerWidth < 1024;
    
    // Gunakan fixed width untuk semua ukuran layar agar bisa scroll
    const svgWidth = Math.max(dimensions.width * 1.2, 800);
    const svgHeight = dimensions.height + (isMobile ? 80 : 100);
    
    // Padding yang konsisten
    const padding = 20;
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    // Set fixed width untuk enable scrolling di semua ukuran
    svg.setAttribute('width', svgWidth + padding * 2);
    svg.setAttribute('height', svgHeight);
    svg.setAttribute('class', 'mx-auto');
    svg.setAttribute('viewBox', `0 0 ${svgWidth + padding * 2} ${svgHeight}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMin meet');
    
    renderTreeNode(node, padding, 20, svgWidth, svg, 0);
    
    return svg.outerHTML;
}

async function analyzeSentence() {
    const sentence = document.getElementById('inputSentence').value.trim();
    
    if (!sentence) {
        alert('Silakan masukkan kalimat untuk dianalisis.');
        return;
    }

    // Show loading state
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `
        <svg class="animate-spin w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        <span>Menganalisis...</span>
    `;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sentence: sentence,
                mode: currentTab
            })
        });

        const data = await response.json();
        
        const resultSection = document.getElementById('resultSection');
        const resultTitle = document.getElementById('resultTitle');
        const resultMessage = document.getElementById('resultMessage');
        const resultStructure = document.getElementById('resultStructure');
        const tokenList = document.getElementById('tokenList');
        const resultIcon = document.getElementById('resultIcon');
        const treeVisualization = document.getElementById('treeVisualization');
        const parseTreeSection = document.getElementById('parseTreeSection');
        const sentenceType = document.getElementById('sentenceType');

        const resultContainer = resultSection.querySelector('.bg-white');
        
        // Display sentence type
        if (data.sentence_type) {
            sentenceType.textContent = data.sentence_type;
        }
        
        if (data.valid) {
            resultSection.classList.remove('hidden');
            resultContainer.className = 'bg-white rounded-xl p-4 sm:p-6 shadow-xl border border-green-200';
            
            const iconContainer = resultContainer.querySelector('.w-8, .w-10');
            if (iconContainer) {
                iconContainer.className = 'w-8 h-8 sm:w-10 sm:h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0';
            }
            
            resultTitle.className = 'font-bold text-green-900 mb-1 text-sm sm:text-base';
            resultTitle.textContent = 'Kalimat Valid';
            resultMessage.className = 'text-xs sm:text-sm text-green-700';
            resultMessage.textContent = `Berhasil mem-parse ${data.tokens.length} token menggunakan ${currentTab.toUpperCase()}`;
            resultStructure.className = 'text-xs text-green-600 mt-1';
            resultStructure.textContent = `Struktur: ${data.structure}`;
            
            resultIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
            resultIcon.className = 'w-4 h-4 sm:w-5 sm:h-5 text-green-600';
            
            if (data.parse_tree) {
                parseTreeSection.classList.remove('hidden');
                treeVisualization.innerHTML = renderTree(data.parse_tree);
            }
        } else {
            resultSection.classList.remove('hidden');
            resultContainer.className = 'bg-white rounded-xl p-4 sm:p-6 shadow-xl border border-red-200';
            
            const iconContainer = resultContainer.querySelector('.w-8, .w-10');
            if (iconContainer) {
                iconContainer.className = 'w-8 h-8 sm:w-10 sm:h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0';
            }
            
            resultTitle.className = 'font-bold text-red-900 mb-1 text-sm sm:text-base';
            resultTitle.textContent = 'Kalimat Tidak Valid';
            resultMessage.className = 'text-xs sm:text-sm text-red-700';
            resultMessage.textContent = data.error || 'Kalimat tidak sesuai dengan grammar yang didefinisikan';
            resultStructure.className = 'text-xs text-red-600 mt-1';
            resultStructure.textContent = `Mode: ${currentTab.toUpperCase()}`;
            
            resultIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
            resultIcon.className = 'w-4 h-4 sm:w-5 sm:h-5 text-red-600';
            
            parseTreeSection.classList.add('hidden');
        }

        // Display tokens
        tokenList.innerHTML = '';
        data.tokens.forEach(token => {
            const span = document.createElement('span');
            span.className = data.valid ? 
                'bg-amber-100 text-gray-900 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-md text-xs font-medium border border-amber-300 hover:bg-amber-200 transition-colors' :
                'bg-red-100 text-gray-900 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-md text-xs font-medium border border-red-300 hover:bg-red-200 transition-colors';
            span.textContent = token;
            tokenList.appendChild(span);
        });

        // Display token analysis
        if (data.token_analysis) {
            // Remove existing analysis if any
            const existingAnalysis = tokenList.parentElement.parentElement.querySelector('.mt-4.bg-gray-50');
            if (existingAnalysis) {
                existingAnalysis.remove();
            }
            
            const analysisDiv = document.createElement('div');
            analysisDiv.className = 'mt-4 bg-gray-50 rounded-lg p-3 sm:p-4 border border-gray-200';
            analysisDiv.innerHTML = '<h4 class="text-xs font-bold text-gray-700 mb-3 uppercase tracking-wide">Analisis Kategori Kata</h4>';
            
            const analysisTable = document.createElement('div');
            analysisTable.className = 'space-y-2';
            
            data.token_analysis.forEach(item => {
                const row = document.createElement('div');
                row.className = 'flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-3 text-xs sm:text-sm';
                
                const tokenSpan = document.createElement('span');
                tokenSpan.className = 'font-mono font-bold sm:min-w-[100px] text-gray-800';
                tokenSpan.textContent = item.token;
                
                const categorySpan = document.createElement('span');
                if (item.found) {
                    categorySpan.className = 'text-gray-700';
                    categorySpan.textContent = '→ ' + item.categories.join(', ');
                } else {
                    categorySpan.className = 'text-red-600 font-semibold';
                    categorySpan.textContent = '→ TIDAK DIKENALI';
                }
                
                row.appendChild(tokenSpan);
                row.appendChild(categorySpan);
                analysisTable.appendChild(row);
            });
            
            analysisDiv.appendChild(analysisTable);
            tokenList.parentElement.parentElement.appendChild(analysisDiv);
        }

        // Display error details
        if (!data.valid && data.error_details) {
            // Remove existing error details if any
            const existingError = tokenList.parentElement.parentElement.querySelector('.mt-4.bg-red-50');
            if (existingError) {
                existingError.remove();
            }
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'mt-4 bg-red-50 rounded-lg p-3 sm:p-4 border border-red-200';
            errorDiv.innerHTML = '<h4 class="text-xs font-bold text-red-700 mb-3 uppercase tracking-wide">Detail Kesalahan</h4>';
            
            const errorList = document.createElement('ul');
            errorList.className = 'space-y-2 text-xs sm:text-sm text-red-700';
            
            data.error_details.forEach(detail => {
                const li = document.createElement('li');
                li.className = 'flex items-start gap-2';
                li.innerHTML = `<span class="text-red-500 font-bold">•</span><span>${detail}</span>`;
                errorList.appendChild(li);
            });
            
            errorDiv.appendChild(errorList);
            tokenList.parentElement.parentElement.appendChild(errorDiv);
        }

        // Scroll to results - with smooth behavior
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);

    } catch (error) {
        console.error('Error:', error);
        alert('Terjadi kesalahan saat menganalisis kalimat. Silakan coba lagi.');
    } finally {
        // Restore button state
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Handle window resize for responsive tree rendering
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        const treeVisualization = document.getElementById('treeVisualization');
        if (treeVisualization && treeVisualization.innerHTML) {
            // Re-render tree if it exists
            const resultSection = document.getElementById('resultSection');
            if (!resultSection.classList.contains('hidden')) {
            }
        }
    }, 250);
});

// Initialize
switchTab('cfg');
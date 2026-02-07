/**
 * Physics Problem Solver - Frontend JavaScript
 * Handles image upload, API communication, and solution display
 */

// DOM Elements
const imageInput = document.getElementById('imageInput');
const uploadBox = document.getElementById('uploadBox');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const removeImageBtn = document.getElementById('removeImage');
const solveButton = document.getElementById('solveButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const solutionSection = document.getElementById('solutionSection');
const solutionOutput = document.getElementById('solutionOutput');
const solveAnotherBtn = document.getElementById('solveAnother');
const errorMessage = document.getElementById('errorMessage');

// API Configuration
const API_BASE_URL = window.location.origin;

// State
let selectedFile = null;

/**
 * Initialize event listeners
 */
function init() {
    // File input change
    imageInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadBox.addEventListener('dragover', handleDragOver);
    uploadBox.addEventListener('drop', handleDrop);
    uploadBox.addEventListener('dragleave', handleDragLeave);
    
    // Buttons
    removeImageBtn.addEventListener('click', resetUpload);
    solveButton.addEventListener('click', solveProblem);
    solveAnotherBtn.addEventListener('click', resetAll);
}

/**
 * Handle file selection from input
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

/**
 * Handle drag over event
 */
function handleDragOver(event) {
    event.preventDefault();
    uploadBox.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(event) {
    event.preventDefault();
    uploadBox.classList.remove('drag-over');
}

/**
 * Handle file drop
 */
function handleDrop(event) {
    event.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        processFile(file);
    } else {
        showError('Please drop an image file (PNG, JPG, JPEG)');
    }
}

/**
 * Process and validate selected file
 */
function processFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload PNG, JPG, or JPEG.');
        return;
    }
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 10MB.');
        return;
    }
    
    selectedFile = file;
    displayPreview(file);
    solveButton.disabled = false;
    hideError();
}

/**
 * Display image preview
 */
function displayPreview(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        uploadBox.style.display = 'none';
        preview.style.display = 'block';
    };
    
    reader.readAsDataURL(file);
}

/**
 * Reset upload (remove selected image)
 */
function resetUpload() {
    selectedFile = null;
    imageInput.value = '';
    previewImage.src = '';
    uploadBox.style.display = 'block';
    preview.style.display = 'none';
    solveButton.disabled = true;
    hideError();
}

/**
 * Reset entire application
 */
function resetAll() {
    resetUpload();
    solutionSection.style.display = 'none';
    solutionOutput.innerHTML = '';
}

/**
 * Send image to backend API and get solution
 */
async function solveProblem() {
    if (!selectedFile) {
        showError('Please select an image first.');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    // Show loading indicator
    loadingIndicator.style.display = 'block';
    solveButton.disabled = true;
    hideError();
    solutionSection.style.display = 'none';
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/solve`, {
            method: 'POST',
            body: formData
        });
        
        // Parse response
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to process image');
        }
        
        if (data.success && data.solution) {
            displaySolution(data.solution, data.diagrams || []);
        } else {
            throw new Error('No solution received from server');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
        solveButton.disabled = false;
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * Clean up LaTeX formatting issues
 */
function cleanLatexText(text) {
    // Replace \text{} with \mathrm{} for better rendering
    text = text.replace(/\\text\{([^}]+)\}/g, '\\mathrm{$1}');
    
    // Fix common spacing issues with units
    text = text.replace(/(\d+)\s*\\mathrm\{/g, '$1~\\mathrm{');
    
    return text;
}

/**
 * Display the solution in the output area with LaTeX rendering and diagram generation
 */
function displaySolution(solution, diagrams = []) {
    // Clean up LaTeX formatting
    solution = cleanLatexText(solution);
    
    // Clear previous content
    solutionOutput.innerHTML = '';
    
    // Extract diagram markers
    const diagramRegex = /\[DIAGRAM:\s*([^\]]+)\]/g;
    let diagramMatches = [];
    let match;
    
    while ((match = diagramRegex.exec(solution)) !== null) {
        diagramMatches.push({
            fullMatch: match[0],
            description: match[1].trim()
        });
    }
    
    // Split solution by diagram markers
    let parts = solution.split(/\[DIAGRAM:[^\]]+\]/);
    
    // Create the solution HTML
    let htmlContent = '';
    
    for (let i = 0; i < parts.length; i++) {
        // Add the text part
        if (parts[i].trim()) {
            htmlContent += `<div class="solution-text">${escapeHtml(parts[i])}</div>`;
        }
        
        // Add diagram if there's one after this part
        if (i < diagramMatches.length) {
            const diagramData = diagrams[i];
            
            htmlContent += `
                <div class="diagram-section">
                    <div class="diagram-header">📐 Diagram</div>
                    <div class="diagram-description">${escapeHtml(diagramMatches[i].description)}</div>
            `;
            
            // If we have a generated diagram, show it
            if (diagramData && diagramData.image) {
                htmlContent += `
                    <img src="${diagramData.image}" alt="Generated Diagram" class="diagram-canvas">
                `;
            } else {
                // Fallback placeholder
                htmlContent += `
                    <div class="diagram-placeholder">
                        <svg width="100%" height="300" style="background: white; border: 2px solid #e2e8f0; border-radius: 8px;">
                            <text x="50%" y="50%" text-anchor="middle" fill="#718096" font-size="14" font-family="Arial">
                                📝 Draw this diagram on paper based on the description above
                            </text>
                        </svg>
                    </div>
                `;
            }
            
            htmlContent += `</div>`;
        }
    }
    
    solutionOutput.innerHTML = htmlContent;
    
    // Render LaTeX with KaTeX
    renderMathInElement(solutionOutput, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ],
        throwOnError: false,
        trust: true
    });
    
    solutionSection.style.display = 'block';
    
    // Scroll to solution
    solutionSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

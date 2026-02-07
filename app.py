"""
Physics Problem Solver Backend
Flask application that processes physics problem screenshots using Google Gemini API
"""

import os
import base64
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from diagram_generator import generate_diagram_from_description

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for local development

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable must be set")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Structured prompt for physics problem solving with LaTeX and diagram instructions
PHYSICS_PROMPT = """You are an expert physics tutor specializing in AP Physics and introductory college-level physics.

Analyze the physics problem shown in the image and provide a complete, step-by-step solution.

IMPORTANT FORMATTING RULES:
- Use LaTeX for ALL mathematical expressions, equations, and variables
- Wrap inline math in single dollar signs: $v = 10 \text{ m/s}$
- Wrap display equations in double dollar signs: $$F = ma$$
- Use proper LaTeX subscripts: $v_0$, $a_x$, $F_{net}$
- Use proper LaTeX superscripts: $x^2$, $v^2$
- Use \text{} for units inside math: $10 \text{ m/s}^2$
- Use \vec{} for vectors: $\vec{F}$, $\vec{v}$

DIAGRAM INSTRUCTIONS:
If a free body diagram or any physics diagram would help understand the problem:
1. Include a section titled "## Free Body Diagram" or "## Diagram"
2. Describe the diagram in detail using this format:
   [DIAGRAM: detailed description of what to draw, including all forces, angles, coordinate system, labels]
3. Example: [DIAGRAM: Draw a box on an inclined plane at 30°. Show weight vector mg pointing down, normal force N perpendicular to plane, friction force f parallel to plane pointing up. Include coordinate axes with x along the plane.]

Follow these guidelines:
1. **Identify the Problem**: Clearly state what is being asked.

2. **Free Body Diagram / Diagram** (if applicable): 
   - Provide detailed diagram description in [DIAGRAM: ...] format
   - This will be used to generate a visual diagram

3. **List Given Information**: 
   - Extract all known values, constants, and conditions
   - Use LaTeX for all variables and values: $m = 5 \text{ kg}$, $\theta = 30°$

4. **Determine Relevant Concepts**: 
   - Identify the physics principles and equations needed
   - Write equations in LaTeX: $$F_{net} = ma$$

5. **Solve Step-by-Step**: 
   - Show all work clearly with LaTeX formatting
   - Explain the reasoning for each step
   - Include all calculations with units
   - Use proper subscripts and superscripts
   - Example: $$v_f^2 = v_0^2 + 2a\Delta x$$

6. **Final Answer**: 
   - State the answer clearly with proper LaTeX formatting
   - Include units and significant figures
   - Example: $$v_f = 15.3 \text{ m/s}$$

Keep explanations clear and concise. Use LaTeX for ALL math. Provide diagram descriptions when helpful.

If the image does not contain a physics problem, politely state that you can only solve physics problems."""


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('templates', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files (CSS/JS)"""
    return send_from_directory('static', path)


@app.route('/solve', methods=['POST'])
def solve_physics_problem():
    """
    Endpoint to solve physics problems from uploaded images
    
    Expects:
        - multipart/form-data with 'image' file field
    
    Returns:
        - JSON with 'solution' field containing the step-by-step explanation
    """
    try:
        # Validate that an image file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_extension = image_file.filename.rsplit('.', 1)[-1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or JPEG'}), 400
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Prepare image for Gemini API
        image_part = {
            'mime_type': image_file.content_type or f'image/{file_extension}',
            'data': image_bytes
        }
        
        # Send to Gemini API
        response = model.generate_content([PHYSICS_PROMPT, image_part])
        
        # Extract solution text
        solution = response.text
        
        # Extract diagram descriptions and generate diagrams
        diagram_pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
        diagrams = []
        
        for match in re.finditer(diagram_pattern, solution):
            description = match.group(1).strip()
            diagram_base64 = generate_diagram_from_description(description)
            if diagram_base64:
                diagrams.append({
                    'description': description,
                    'image': diagram_base64
                })
        
        return jsonify({
            'success': True,
            'solution': solution,
            'diagrams': diagrams
        })
    
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to process image: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'api_configured': bool(GEMINI_API_KEY)})


if __name__ == '__main__':
    # Run Flask development server
    # In production, use a proper WSGI server like gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)

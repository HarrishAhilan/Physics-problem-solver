# Physics Problem Solver MVP

A web application that uses Google Gemini AI to solve physics problems from uploaded screenshots. Built with Flask (Python) backend and vanilla JavaScript frontend.

## Features

- 📸 Upload physics problem screenshots (PNG, JPG, JPEG)
- 🤖 AI-powered analysis using Google Gemini Vision API
- 📝 Step-by-step solutions with clear explanations
- 🔢 **LaTeX math rendering** with proper subscripts, superscripts, and equations
- 📐 **Auto-generated free body diagrams** and physics visualizations
- 🎯 Supports AP Physics and introductory college-level problems
- 💡 Clean, minimal interface focused on usability

## Project Structure

```
physics-solver/
├── app.py                  # Flask backend server
├── diagram_generator.py    # Physics diagram generation (matplotlib)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML page (with KaTeX support)
├── static/
│   ├── script.js          # Frontend JavaScript (LaTeX rendering)
│   └── styles.css         # CSS styling
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd physics-solver
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Set your Gemini API key as an environment variable:

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

Alternatively, create a `.env` file in the project root:
```
GEMINI_API_KEY=your-api-key-here
```

Then modify `app.py` to load from `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
```

(Requires `pip install python-dotenv`)

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a physics problem screenshot and click "Solve Problem"

## Usage

1. **Upload Image**: Click the upload area or drag and drop a screenshot
2. **Submit**: Click "Solve Problem" button
3. **View Solution**: AI-generated step-by-step solution appears below with:
   - **Formatted equations** using LaTeX (proper subscripts like $v_0$, superscripts like $x^2$)
   - **Auto-generated diagrams** for free body diagrams and inclined planes
   - Clear step-by-step explanations
4. **Solve Another**: Click "Solve Another Problem" to reset

### Math Formatting
All mathematical expressions are rendered using KaTeX:
- Variables: $v$, $a$, $F$
- Subscripts: $v_0$, $F_{net}$
- Superscripts: $v^2$, $x^3$
- Equations: $$F = ma$$
- Units: $10 \text{ m/s}^2$

### Diagram Generation
The app automatically generates visual diagrams when Gemini describes them:
- **Free body diagrams** with force vectors
- **Inclined plane problems** with angles and forces
- **Custom physics visualizations**

## Gemini Prompt Structure

The backend uses a structured prompt that instructs Gemini to:

- Identify the physics problem clearly
- List all given information
- Determine relevant physics concepts and equations
- Solve step-by-step with clear reasoning
- Provide final answers with proper units

Example prompt excerpt:
```
You are an expert physics tutor specializing in AP Physics...
1. Identify the Problem: Clearly state what is being asked.
2. List Given Information: Extract all known values...
3. Determine Relevant Concepts: Identify physics principles...
4. Solve Step-by-Step: Show all work clearly...
5. Final Answer: State the answer with proper units...
```

See `app.py` for the complete prompt.

## API Endpoints

### `GET /`
Serves the main HTML page

### `POST /solve`
Processes physics problem images

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` file field

**Response:**
```json
{
  "success": true,
  "solution": "Step-by-step solution text..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "api_configured": true
}
```

## Technical Stack

**Backend:**
- Flask 3.0.0 - Python web framework
- google-generativeai 0.8.3 - Gemini API client
- flask-cors 4.0.0 - CORS support

**Frontend:**
- Vanilla JavaScript (no frameworks)
- HTML5 with drag-and-drop API
- CSS3 with responsive design

## Security Considerations

- API key stored in environment variable (never in code)
- No API key exposure to frontend
- File type and size validation
- CORS enabled for local development only
- Input sanitization on file uploads

## Limitations & Non-Goals

This is an MVP (Minimum Viable Product). The following are explicitly excluded:

- ❌ User authentication/accounts
- ❌ Database storage
- ❌ PDF export functionality
- ❌ Image annotation or cropping
- ❌ LaTeX rendering
- ❌ Production deployment configuration
- ❌ Advanced styling/animations

## Troubleshooting

**Issue: "GEMINI_API_KEY environment variable must be set"**
- Solution: Make sure you've set the API key environment variable before running

**Issue: "Module not found" errors**
- Solution: Install dependencies with `pip install -r requirements.txt`

**Issue: API rate limits**
- Solution: Gemini has free tier limits. Check your usage at the Google AI Studio

**Issue: Large file uploads fail**
- Solution: Ensure images are under 10MB. Resize if necessary.

## Production Deployment

For production deployment:

1. Use a production WSGI server (gunicorn, uWSGI)
2. Set up proper environment variable management
3. Configure CORS for specific domains only
4. Add rate limiting
5. Implement proper logging
6. Use HTTPS
7. Add error monitoring (e.g., Sentry)

Example gunicorn command:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

This project is for educational and portfolio purposes.

## Credits

Built with:
- Google Gemini API
- Flask Framework
- Love for physics ❤️

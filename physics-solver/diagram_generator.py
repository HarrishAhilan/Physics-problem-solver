"""
Diagram Generator for Physics Problems
Uses matplotlib to generate free body diagrams and other physics visualizations
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import numpy as np
import io
import base64
import re


def parse_diagram_description(description):
    """
    Parse the diagram description from Gemini to extract key information
    Returns a dict with diagram type and parameters
    """
    description_lower = description.lower()
    
    # Detect diagram type
    diagram_type = 'generic'
    if 'free body' in description_lower or 'fbd' in description_lower:
        diagram_type = 'free_body'
    elif 'inclined plane' in description_lower or 'ramp' in description_lower:
        diagram_type = 'inclined_plane'
    elif 'pulley' in description_lower:
        diagram_type = 'pulley'
    elif 'projectile' in description_lower or 'trajectory' in description_lower:
        diagram_type = 'projectile'
    
    # Extract forces mentioned
    forces = []
    force_patterns = [
        (r'weight|gravity|mg', 'Weight'),
        (r'normal force|normal|n', 'Normal'),
        (r'friction|f[_k]?|f[_s]?', 'Friction'),
        (r'tension|t', 'Tension'),
        (r'applied force|push|pull', 'Applied'),
        (r'drag|air resistance', 'Drag'),
    ]
    
    for pattern, force_name in force_patterns:
        if re.search(pattern, description_lower):
            forces.append(force_name)
    
    # Extract angle if mentioned
    angle = None
    angle_match = re.search(r'(\d+)°|(\d+)\s*degrees', description)
    if angle_match:
        angle = int(angle_match.group(1) or angle_match.group(2))
    
    return {
        'type': diagram_type,
        'forces': forces,
        'angle': angle,
        'description': description
    }


def generate_free_body_diagram(forces, angle=None):
    """Generate a free body diagram with specified forces"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    
    # Draw the object (box)
    box_size = 0.4
    box = Rectangle((-box_size/2, -box_size/2), box_size, box_size, 
                    fill=True, facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(box)
    
    # Define force vectors
    force_vectors = {
        'Weight': {'dx': 0, 'dy': -1.5, 'color': 'red', 'label': r'$\vec{F}_g = mg$'},
        'Normal': {'dx': 0, 'dy': 1.5, 'color': 'blue', 'label': r'$\vec{N}$'},
        'Friction': {'dx': -1.5, 'dy': 0, 'color': 'orange', 'label': r'$\vec{f}$'},
        'Tension': {'dx': 1.5, 'dy': 0, 'color': 'green', 'label': r'$\vec{T}$'},
        'Applied': {'dx': 1.5, 'dy': 0, 'color': 'purple', 'label': r'$\vec{F}_{app}$'},
        'Drag': {'dx': -1.2, 'dy': 0, 'color': 'brown', 'label': r'$\vec{F}_D$'},
    }
    
    # Draw forces
    for force in forces:
        if force in force_vectors:
            vec = force_vectors[force]
            arrow = FancyArrowPatch((0, 0), (vec['dx'], vec['dy']),
                                   arrowstyle='->', mutation_scale=30, 
                                   linewidth=3, color=vec['color'])
            ax.add_patch(arrow)
            
            # Add label
            label_x = vec['dx'] * 1.2
            label_y = vec['dy'] * 1.2
            ax.text(label_x, label_y, vec['label'], 
                   fontsize=14, ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add coordinate system
    ax.arrow(2, -2.5, 0.5, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(2, -2.5, 0, 0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.text(2.6, -2.5, '+x', fontsize=12)
    ax.text(2, -1.9, '+y', fontsize=12)
    
    ax.set_title('Free Body Diagram', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    return fig


def generate_inclined_plane_diagram(angle=30, forces=None):
    """Generate an inclined plane diagram"""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(-1, 6)
    ax.set_ylim(-1, 4)
    ax.set_aspect('equal')
    
    if forces is None:
        forces = ['Weight', 'Normal', 'Friction']
    
    # Draw inclined plane
    angle_rad = np.radians(angle)
    plane_length = 5
    plane_height = plane_length * np.sin(angle_rad)
    
    # Plane triangle
    plane = plt.Polygon([[0, 0], [plane_length * np.cos(angle_rad), plane_height], 
                        [plane_length * np.cos(angle_rad), 0]], 
                       fill=True, facecolor='lightgray', edgecolor='black', linewidth=2)
    ax.add_patch(plane)
    
    # Box on incline
    box_center_x = 2.5 * np.cos(angle_rad)
    box_center_y = 2.5 * np.sin(angle_rad)
    box_size = 0.3
    
    # Rotate box to align with plane
    box_vertices = [
        [-box_size/2, -box_size/2],
        [box_size/2, -box_size/2],
        [box_size/2, box_size/2],
        [-box_size/2, box_size/2]
    ]
    
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    rotated_vertices = [rotation_matrix @ np.array(v) + np.array([box_center_x, box_center_y]) 
                       for v in box_vertices]
    
    box = plt.Polygon(rotated_vertices, fill=True, facecolor='lightblue', 
                     edgecolor='black', linewidth=2)
    ax.add_patch(box)
    
    # Draw forces
    if 'Weight' in forces:
        # Weight (straight down)
        ax.arrow(box_center_x, box_center_y, 0, -1.2, 
                head_width=0.15, head_length=0.1, fc='red', ec='red', linewidth=2)
        ax.text(box_center_x - 0.4, box_center_y - 0.7, r'$mg$', 
               fontsize=14, color='red', fontweight='bold')
    
    if 'Normal' in forces:
        # Normal (perpendicular to plane)
        normal_dx = -0.8 * np.sin(angle_rad)
        normal_dy = 0.8 * np.cos(angle_rad)
        ax.arrow(box_center_x, box_center_y, normal_dx, normal_dy,
                head_width=0.15, head_length=0.1, fc='blue', ec='blue', linewidth=2)
        ax.text(box_center_x + normal_dx - 0.3, box_center_y + normal_dy + 0.2, 
               r'$N$', fontsize=14, color='blue', fontweight='bold')
    
    if 'Friction' in forces:
        # Friction (parallel to plane, opposing motion)
        friction_dx = -0.8 * np.cos(angle_rad)
        friction_dy = -0.8 * np.sin(angle_rad)
        ax.arrow(box_center_x, box_center_y, friction_dx, friction_dy,
                head_width=0.15, head_length=0.1, fc='orange', ec='orange', linewidth=2)
        ax.text(box_center_x + friction_dx, box_center_y + friction_dy - 0.3, 
               r'$f$', fontsize=14, color='orange', fontweight='bold')
    
    # Draw angle
    arc = patches.Arc((0, 0), 1, 1, angle=0, theta1=0, theta2=angle, 
                     color='black', linewidth=2)
    ax.add_patch(arc)
    ax.text(0.6, 0.15, f'{angle}°', fontsize=12, fontweight='bold')
    
    # Coordinate system
    ax.arrow(4.5, -0.5, 0.5, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(4.5, -0.5, 0, 0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.text(5.1, -0.5, '+x', fontsize=12)
    ax.text(4.5, 0.2, '+y', fontsize=12)
    
    ax.set_title(f'Inclined Plane ({angle}°)', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    return fig


def generate_diagram_from_description(description):
    """
    Main function to generate diagram based on Gemini's description
    Returns base64 encoded PNG image
    """
    parsed = parse_diagram_description(description)
    
    try:
        if parsed['type'] == 'inclined_plane' and parsed['angle']:
            fig = generate_inclined_plane_diagram(parsed['angle'], parsed['forces'])
        elif parsed['forces']:
            fig = generate_free_body_diagram(parsed['forces'], parsed['angle'])
        else:
            # Generic diagram with text description
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f"Diagram:\n{description}", 
                   ha='center', va='center', fontsize=12, wrap=True)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{img_base64}"
    
    except Exception as e:
        print(f"Error generating diagram: {e}")
        # Return None if diagram generation fails
        return None

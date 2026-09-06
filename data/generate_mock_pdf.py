import os
try:
    from fpdf import FPDF
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf"])
    from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="City Building Code 2024", ln=1, align='C')
pdf.set_font("Arial", size=12)

content = """
Chapter 1: Residential Requirements

Section 101.1: Minimum Room Dimensions
The master bedroom must have a minimum floor area of 120 square feet. 
The minimum width of a master bedroom shall be no less than 10 feet.

Section 101.2: Egress and Hallways
All interior hallways in residential properties must maintain a minimum clear width of 3.5 feet (42 inches).

Section 101.3: Windows
Every habitable room shall have at least one operable window for emergency escape.
"""

for line in content.split('\n'):
    pdf.cell(200, 10, txt=line, ln=1, align='L')

output_path = os.path.join(os.path.dirname(__file__), "raw", "building_code_2024.pdf")
pdf.output(output_path)
print(f"Created mock PDF at {output_path}")

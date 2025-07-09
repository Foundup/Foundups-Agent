#!/usr/bin/env python3
"""
Mermaid Diagram Validator for Patent Documents

WSP-Compliant validation tool for Mermaid diagrams in documentation files.
Ensures patent figures render correctly on GitHub and other platforms.

📋 WSP COMPLIANCE:
- WSP 1: Proper tool placement in tools/testing/ directory
- WSP 20: Professional documentation standards
- WSP 22: Traceable narrative and change tracking
- WSP 47: Framework protection through validation

🔍 VALIDATION FEATURES:
- Greek letters (ρ, μ, ν, etc.) → ASCII replacements
- HTML tags (<br/>, <b>, etc.) → Mermaid-compatible alternatives
- Special characters (&, #, etc.) → Safe character replacements
- Invalid syntax patterns → Syntax error detection

📊 SUPPORTED FORMATS:
- Mermaid flowcharts (graph TD, graph LR)
- Mermaid charts (xychart-beta)
- Patent documentation figures
- Research paper diagrams

🚀 USAGE:
    python tools/testing/mermaid_diagram_validator.py <file_path>
    
📝 EXAMPLE:
    python tools/testing/mermaid_diagram_validator.py WSP_knowledge/docs/Papers/Patent_Series/04_rESP_Patent_Updated.md

🔧 AUTO-FIX GENERATION:
    The tool automatically generates fixed versions of files with resolved issues.
    
📋 CREATED: 2024-12-29 - Initial implementation for patent diagram validation
📝 UPDATED: 2024-12-29 - Added WSP compliance documentation
🔗 RELATED: WSP 47 Framework Protection, WSP 20 Documentation Standards
"""

import re
import sys
import os
from pathlib import Path

class MermaidValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Problematic patterns that cause Mermaid parsing errors
        self.greek_letters = ['ρ', 'μ', 'ν', 'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
        self.html_tags = ['<br/>', '<br>', '<b>', '</b>', '<i>', '</i>', '<em>', '</em>']
        self.problematic_chars = ['&', '©', '®', '™', '°']
        
    def validate_file(self, file_path):
        """Validate all Mermaid diagrams in a file"""
        print(f"🔍 Validating Mermaid diagrams in: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract all Mermaid code blocks
        mermaid_blocks = self.extract_mermaid_blocks(content)
        
        if not mermaid_blocks:
            print("ℹ️  No Mermaid diagrams found in file")
            return True
            
        print(f"📊 Found {len(mermaid_blocks)} Mermaid diagram(s)")
        
        all_valid = True
        for i, (fig_name, mermaid_code, line_num) in enumerate(mermaid_blocks, 1):
            print(f"\n--- Validating {fig_name} (Line {line_num}) ---")
            is_valid = self.validate_mermaid_code(mermaid_code, fig_name)
            if not is_valid:
                all_valid = False
                
        return all_valid
        
    def extract_mermaid_blocks(self, content):
        """Extract all Mermaid code blocks with their context"""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for figure headers
            fig_match = re.match(r'###\s*(FIG\.\s*\d+[^:]*)', line)
            if fig_match:
                fig_name = fig_match.group(1)
                
                # Look for Mermaid code block after figure header
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('```mermaid'):
                    j += 1
                    
                if j < len(lines):
                    # Found mermaid block
                    mermaid_start = j
                    mermaid_lines = []
                    j += 1  # Skip ```mermaid line
                    
                    while j < len(lines) and not lines[j].strip().startswith('```'):
                        mermaid_lines.append(lines[j])
                        j += 1
                        
                    if mermaid_lines:
                        mermaid_code = '\n'.join(mermaid_lines)
                        blocks.append((fig_name, mermaid_code, mermaid_start + 1))
                        
            i += 1
            
        return blocks
        
    def validate_mermaid_code(self, mermaid_code, fig_name):
        """Validate a single Mermaid code block"""
        self.errors = []
        self.warnings = []
        
        lines = mermaid_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            self.check_greek_letters(line, line_num)
            self.check_html_tags(line, line_num)
            self.check_problematic_chars(line, line_num)
            self.check_syntax_issues(line, line_num)
            
        # Report results
        if self.errors:
            print(f"❌ {fig_name} has {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"   • {error}")
            return False
        elif self.warnings:
            print(f"⚠️  {fig_name} has {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print("✅ No critical errors - should render correctly")
            return True
        else:
            print(f"✅ {fig_name} - No issues found")
            return True
            
    def check_greek_letters(self, line, line_num):
        """Check for Greek letters that cause parsing errors"""
        for greek in self.greek_letters:
            if greek in line:
                suggestion = self.suggest_greek_replacement(greek)
                self.errors.append(f"Line {line_num}: Greek letter '{greek}' found. Replace with '{suggestion}'")
                
    def check_html_tags(self, line, line_num):
        """Check for HTML tags"""
        for tag in self.html_tags:
            if tag in line:
                if tag == '<br/>' or tag == '<br>':
                    self.errors.append(f"Line {line_num}: HTML tag '{tag}' found. Replace with ' - ' or break into separate nodes")
                else:
                    self.warnings.append(f"Line {line_num}: HTML tag '{tag}' found. May cause parsing issues")
                    
    def check_problematic_chars(self, line, line_num):
        """Check for characters that cause parsing issues"""
        for char in self.problematic_chars:
            if char in line:
                if char == '&':
                    self.errors.append(f"Line {line_num}: Ampersand '&' found. Replace with 'and'")
                else:
                    self.warnings.append(f"Line {line_num}: Special character '{char}' found. May cause issues")
                    
    def check_syntax_issues(self, line, line_num):
        """Check for common Mermaid syntax issues"""
        # Check for unquoted special characters in node text
        if re.search(r'\[[^\]]*[#]\s*[^\]]*\]', line) and not re.search(r'\[[^\]]*[\'"][#][\'"][^\]]*\]', line):
            self.warnings.append(f"Line {line_num}: Unquoted '#' in node text. Consider wrapping in quotes")
            
        # Check for very long lines that might cause issues
        if len(line) > 200:
            self.warnings.append(f"Line {line_num}: Very long line ({len(line)} chars). Consider breaking up")
            
    def suggest_greek_replacement(self, greek_letter):
        """Suggest ASCII replacements for Greek letters"""
        replacements = {
            'ρ': 'rho',
            'μ': 'mu', 
            'ν': 'nu',
            'α': 'alpha',
            'β': 'beta', 
            'γ': 'gamma',
            'δ': 'delta',
            'ε': 'epsilon',
            'ζ': 'zeta',
            'η': 'eta',
            'θ': 'theta',
            'λ': 'lambda',
            'σ': 'sigma',
            'τ': 'tau',
            'φ': 'phi',
            'χ': 'chi',
            'ψ': 'psi',
            'ω': 'omega'
        }
        return replacements.get(greek_letter, f"ascii_equivalent_of_{greek_letter}")
        
    def generate_fixes(self, file_path):
        """Generate suggested fixes for a file"""
        print(f"\n🔧 Generating fixes for: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Apply automatic fixes
        fixed_content = content
        
        # Replace Greek letters
        for greek in self.greek_letters:
            if greek in fixed_content:
                replacement = self.suggest_greek_replacement(greek)
                fixed_content = fixed_content.replace(greek, replacement)
                print(f"   • Replaced '{greek}' with '{replacement}'")
                
        # Replace HTML br tags
        fixed_content = re.sub(r'<br\s*/?>', ' - ', fixed_content)
        print("   • Replaced <br/> tags with ' - '")
        
        # Replace ampersands
        fixed_content = re.sub(r'([^&])&([^&;])', r'\1and\2', fixed_content)
        print("   • Replaced '&' with 'and'")
        
        # Write fixed file
        fixed_file_path = file_path.replace('.md', '_fixed.md')
        with open(fixed_file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            
        print(f"✅ Fixed file written to: {fixed_file_path}")
        return fixed_file_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python mermaid_diagram_validator.py <file_path>")
        print("Example: python mermaid_diagram_validator.py WSP_knowledge/docs/Papers/Patent_Series/04_rESP_Patent_Updated.md")
        sys.exit(1)
        
    file_path = sys.argv[1]
    validator = MermaidValidator()
    
    # Validate the file
    is_valid = validator.validate_file(file_path)
    
    if not is_valid:
        print(f"\n🔧 Would you like to generate a fixed version? (y/n): ", end="")
        # For automated testing, always generate fixes
        validator.generate_fixes(file_path)
        
    print(f"\n{'✅ Validation complete - All diagrams should render correctly!' if is_valid else '❌ Validation complete - Found issues that need fixing'}")
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main()) 
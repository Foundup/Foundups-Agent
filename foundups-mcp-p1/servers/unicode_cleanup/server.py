from fastmcp import FastMCP
import asyncio
import sys
import os
import unicodedata

# Add Foundups paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from qwen_gemma_unicode_campaign import QwenGemmaUnicodeCampaign

app = FastMCP("Foundups Unicode Cleanup MCP Server")

class UnicodeCleanupMCPServer:
    """MCP server for AI-powered Unicode cleanup and WSP 90 compliance"""

    def __init__(self):
        self.campaign = QwenGemmaUnicodeCampaign()

    @app.tool()
    async def analyze_file_unicode(self, file_path: str) -> dict:
        """Analyze a specific file for problematic Unicode characters"""
        try:
            analysis = self.campaign.qwen_analyze_file(file_path)

            if analysis['success']:
                problematic_chars = []
                for char, info in analysis['problematic_chars'].items():
                    problematic_chars.append({
                        'character': char,
                        'unicode_code': f"U+{ord(char):04X}",
                        'name': info['name'],
                        'count': info['count'],
                        'suggested_replacement': info['replacement']
                    })

                return {
                    'success': True,
                    'file_path': file_path,
                    'total_chars': analysis['total_chars'],
                    'problematic_chars_count': len(problematic_chars),
                    'total_problems': analysis['total_problems'],
                    'problematic_characters': problematic_chars,
                    'needs_cleanup': analysis['total_problems'] > 0
                }
            else:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'Analysis failed'
                }

        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    @app.tool()
    async def clean_file_unicode(self, file_path: str, create_backup: bool = True) -> dict:
        """Clean problematic Unicode characters from a specific file"""
        try:
            # First analyze the file
            analysis = self.campaign.qwen_analyze_file(file_path)

            if not analysis['success']:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'Analysis failed'
                }

            if analysis['total_problems'] == 0:
                return {
                    'success': True,
                    'file_path': file_path,
                    'message': 'File already clean - no problematic Unicode found',
                    'chars_cleaned': 0
                }

            # Apply cleanup
            cleanup_result = self.campaign.gemma_apply_cleanup(analysis)

            return {
                'success': cleanup_result['success'],
                'file_path': file_path,
                'chars_cleaned': cleanup_result.get('replacements_made', 0),
                'backup_created': cleanup_result.get('backup_created', None),
                'message': f"Cleaned {cleanup_result.get('replacements_made', 0)} problematic Unicode characters"
            }

        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    @app.tool()
    async def scan_codebase_unicode(self, extensions: list = None) -> dict:
        """Scan the entire codebase for files containing problematic Unicode"""
        if extensions is None:
            extensions = ['.py', '.md', '.txt', '.json', '.yaml', '.yml']

        try:
            unicode_files = []

            for root, dirs, files in os.walk('.'):
                # Skip unwanted directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]

                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Check for problematic Unicode
                            has_problematic = any(char in content for char in self.campaign.gemma_patterns.keys())
                            if has_problematic:
                                # Count problems
                                problem_count = sum(content.count(char) for char in self.campaign.gemma_patterns.keys() if char in content)

                                unicode_files.append({
                                    'file_path': os.path.relpath(file_path),
                                    'problem_count': problem_count
                                })

                        except (UnicodeDecodeError, OSError):
                            continue

            # Sort by problem count (most problematic first)
            unicode_files.sort(key=lambda x: x['problem_count'], reverse=True)

            return {
                'success': True,
                'total_files': len(unicode_files),
                'files': unicode_files[:100],  # Limit to top 100 for response size
                'message': f"Found {len(unicode_files)} files with problematic Unicode characters"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @app.tool()
    async def get_unicode_patterns(self) -> dict:
        """Get all Unicode replacement patterns used by Gemma"""
        patterns = []
        for char, replacement in self.campaign.gemma_patterns.items():
            patterns.append({
                'character': char,
                'unicode_code': f"U+{ord(char):04X}",
                'name': unicodedata.name(char, 'UNKNOWN'),
                'replacement': replacement
            })

        return {
            'success': True,
            'total_patterns': len(patterns),
            'patterns': patterns,
            'description': 'Gemma\'s learned intelligent Unicode replacement patterns'
        }

    @app.tool()
    async def run_full_cleanup_campaign(self, batch_size: int = 50) -> dict:
        """Run the full Qwen/Gemma Unicode cleanup campaign on the entire codebase"""
        try:
            # Run the campaign
            await self.campaign.orchestrate_campaign()

            # Return summary stats
            return {
                'success': True,
                'stats': self.campaign.stats,
                'message': f"Campaign completed: {self.campaign.stats['files_cleaned']} files cleaned, {self.campaign.stats['total_chars_replaced']} characters replaced"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Unicode Cleanup MCP Server running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

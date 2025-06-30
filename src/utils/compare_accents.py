#!/usr/bin/env python3
"""
Yiddish Accent Comparison Utility
=================================
Generates the same text with all available accents for comparison.

Usage:
    1. Paste your text in the YIDDISH_TEXT variable
    2. Run: python src/utils/compare_accents.py
    3. Listen to all the generated files to pick your favorite accent
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.enhanced_synthesizer import EnhancedYiddishSynthesizer


# ============================================================================
# PASTE YOUR TEXT HERE:
# ============================================================================

YIDDISH_TEXT = """שלום עליכם, ווי גייט עס?"""

# ============================================================================
# That's it! Run this file to generate comparison files.
# ============================================================================


def main():
    """Generate accent comparison files."""
    print("🎭 Yiddish Accent Comparison")
    print("=" * 35)
    
    # Check if text was provided
    if not YIDDISH_TEXT.strip():
        print("❌ No text provided! Please paste your Yiddish text in the YIDDISH_TEXT variable.")
        return
    
    # Initialize synthesizer (accent doesn't matter for comparison)
    synthesizer = EnhancedYiddishSynthesizer()
    
    print(f"📝 Text: {YIDDISH_TEXT}")
    print("\n🎭 Generating samples with all available accents...")
    print("   This will help you choose the most authentic sound.")
    
    # Generate comparison files
    generated_files = synthesizer.compare_accents(YIDDISH_TEXT, "output")
    
    if generated_files:
        print(f"\n✅ Generated {len(generated_files)} accent samples:")
        print("\n🎧 Listen to these files to compare:")
        print("=" * 50)
        
        for accent_key, accent_name, filepath in generated_files:
            print(f"  {accent_key:10} - {accent_name}")
            print(f"             File: {filepath}")
            print()
        
        print("🎯 Recommendations:")
        print("  • 'german' - Most authentic (Yiddish evolved from German)")
        print("  • 'polish' - Eastern European communities")
        print("  • 'russian' - Slavic influence")
        print("  • 'hungarian' - Central European accent")
        print("  • 'dutch' - Germanic language family")
        print("  • 'english' - Fallback option (less authentic)")
        
        print(f"\n💡 To use your preferred accent, edit the ACCENT variable")
        print(f"    in src/utils/accent_tts.py")
        
    else:
        print("❌ Failed to generate comparison files.")


if __name__ == "__main__":
    main() 
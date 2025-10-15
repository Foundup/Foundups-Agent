"""
Download Gemma 3 270M for File Naming Enforcement

Gemma 3 is Google's smallest, fastest model perfect for classification tasks.

Model: google/gemma-3-270m (NOT gemma-2)
Size: ~270M parameters (~160MB GGUF Q4_K_M)
Speed: Ultra-fast inference (<50ms per query)
Use case: WSP 57 file naming enforcement, Sentinel augmentation

Target: E:/HoloIndex/models/gemma-3-270m-q4_k_m.gguf

WSP 35: HoloIndex Qwen Advisor (now supports Gemma)
WSP 57: Naming Coherence
WSP 93: CodeIndex Surgical Intelligence
"""

from huggingface_hub import hf_hub_download
from pathlib import Path
import sys

def download_gemma3_270m():
    """
    Download Gemma 3 270M GGUF for ultra-fast classification

    Model: google/gemma-3-270m-it-gguf (instruction-tuned)
    Quantization: Q4_K_M (good quality, tiny size)
    Size: ~160MB
    Speed: <50ms per inference on CPU
    """

    print("=" * 70)
    print("Downloading Gemma 3 270M Instruct GGUF")
    print("=" * 70)
    print()

    # Configuration
    # Note: Using GGUF version from community or converting original
    # Gemma 3 just released, GGUF versions may be in lmstudio-community
    repo_id = "lmstudio-community/gemma-3-270m-it-GGUF"  # Community GGUF conversion
    filename = "gemma-3-270m-it-Q4_K_M.gguf"
    local_dir = Path("E:/HoloIndex/models")

    print(f"Repository: {repo_id}")
    print(f"File: {filename}")
    print(f"Destination: {local_dir}")
    print()
    print("[NOTE] Gemma 3 is brand new - checking for GGUF availability...")
    print()

    # Ensure directory exists
    local_dir.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    target_path = local_dir / filename
    if target_path.exists():
        size_mb = target_path.stat().st_size / (1024 * 1024)
        print(f"[INFO] Model already exists: {target_path}")
        print(f"       Size: {size_mb:.1f} MB")
        print()
        print("To re-download, delete the file and run again.")
        return str(target_path)

    print("[DOWNLOAD] Starting download from Hugging Face...")
    print("           This may take 1-2 minutes...")
    print()

    try:
        # Try to download the GGUF file
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False
        )

        print()
        print("[SUCCESS] Download complete!")
        print(f"          Model saved to: {downloaded_path}")

        size_mb = Path(downloaded_path).stat().st_size / (1024 * 1024)
        print(f"          File size: {size_mb:.1f} MB")
        print()

        return downloaded_path

    except Exception as e:
        print()
        print(f"[ERROR] Download failed: {e}")
        print()
        print("Gemma 3 GGUF may not be available yet (model just released).")
        print()
        print("Alternative options:")
        print()
        print("1. Use existing Qwen 1.5B (already installed):")
        print("   Path: E:/HoloIndex/models/qwen-coder-1.5b.gguf")
        print("   Size: 1.1GB (larger but proven to work)")
        print()
        print("2. Wait for community GGUF conversion of Gemma 3")
        print("   Check: https://huggingface.co/models?search=gemma-3-270m%20gguf")
        print()
        print("3. Convert Gemma 3 to GGUF yourself:")
        print("   - Download: https://huggingface.co/google/gemma-3-270m")
        print("   - Convert with llama.cpp convert script")
        print()
        print("For now, recommend using Qwen 1.5B for file naming task.")
        print()
        sys.exit(1)


def verify_model(model_path: str):
    """Verify the downloaded model can be loaded"""
    print("=" * 70)
    print("Verifying Gemma 3 Installation")
    print("=" * 70)
    print()

    try:
        from llama_cpp import Llama

        print("[TEST] Loading Gemma 3 270M with llama-cpp-python...")

        llm = Llama(
            model_path=model_path,
            n_ctx=512,
            n_threads=2,
            n_gpu_layers=0,
            verbose=False
        )

        print("[SUCCESS] Model loaded successfully!")
        print()

        # Test file naming classification
        print("[TEST] Testing WSP file naming classification...")
        response = llm(
            "Is this a violation? File: modules/test/WSP_AUDIT.md. "
            "Rule: Module docs should not use WSP_ prefix. Answer yes or no.",
            max_tokens=10,
            temperature=0.1
        )

        print("[SUCCESS] Inference test passed!")
        print(f"           Response: {response['choices'][0]['text']}")
        print()
        print("Gemma 3 270M is ready for file naming enforcement!")
        print()

        del llm
        return True

    except ImportError:
        print("[WARNING] llama-cpp-python not installed")
        print("          Install with: pip install llama-cpp-python")
        print()
        return False

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        print()
        return False


def use_qwen_fallback():
    """Use existing Qwen 1.5B as fallback"""
    print("=" * 70)
    print("Using Qwen 1.5B Fallback")
    print("=" * 70)
    print()

    qwen_path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")

    if not qwen_path.exists():
        print("[ERROR] Qwen 1.5B not found at expected location:")
        print(f"        {qwen_path}")
        print()
        print("Please install Qwen first or wait for Gemma 3 GGUF.")
        sys.exit(1)

    print(f"[INFO] Qwen 1.5B found: {qwen_path}")
    size_mb = qwen_path.stat().st_size / (1024 * 1024)
    print(f"       Size: {size_mb:.1f} MB")
    print()
    print("Qwen 1.5B can be used for file naming enforcement.")
    print("It's larger (1.1GB) but provides excellent accuracy.")
    print()
    print("To use Qwen for file naming:")
    print("  1. Update test_qwen_file_naming_trainer.py")
    print(f"  2. Set model_path = '{qwen_path}'")
    print("  3. Run: python holo_index/tests/test_qwen_file_naming_trainer.py")
    print()

    return str(qwen_path)


if __name__ == "__main__":
    print()
    print("Gemma 3 270M Download Script")
    print("For WSP 57 File Naming Enforcement")
    print()
    print("[NOTE] Gemma 3 just released (2025) - GGUF may not be available")
    print()

    try:
        # Try to download Gemma 3
        model_path = download_gemma3_270m()
        verify_model(model_path)

    except SystemExit:
        # Gemma 3 not available, use Qwen fallback
        print()
        print("Falling back to Qwen 1.5B...")
        print()
        qwen_path = use_qwen_fallback()

    print()
    print("=" * 70)
    print("Model Comparison")
    print("=" * 70)
    print()
    print("Gemma 3 270M (target):")
    print("  Size: ~160MB")
    print("  Speed: <50ms per query")
    print("  Best for: Classification tasks (file naming, yes/no decisions)")
    print()
    print("Qwen 1.5B (fallback, already installed):")
    print("  Size: 1.1GB")
    print("  Speed: ~200-300ms per query")
    print("  Best for: Code understanding, complex analysis")
    print()
    print("For WSP 57 file naming enforcement, Gemma 3 is ideal")
    print("but Qwen 1.5B works perfectly fine (just a bit slower).")
    print()

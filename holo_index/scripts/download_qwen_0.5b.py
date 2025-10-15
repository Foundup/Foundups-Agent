"""
Download Qwen 2.5 0.5B Instruct GGUF Model for File Naming Enforcement

This downloads a smaller, faster Qwen model (0.5B params) optimized for
simple classification tasks like file naming violation detection.

Target: E:/HoloIndex/models/qwen2.5-0.5b-instruct-q4_k_m.gguf
Size: ~320MB (vs 1.1GB for qwen-coder-1.5b)
Speed: ~3-5x faster inference
Use case: WSP 57 file naming enforcement

WSP 35: HoloIndex Qwen Advisor
WSP 57: Naming Coherence
"""

from huggingface_hub import hf_hub_download
from pathlib import Path
import sys

def download_qwen_0_5b():
    """
    Download Qwen 2.5 0.5B Instruct Q4_K_M GGUF

    Model: Qwen/Qwen2.5-0.5B-Instruct-GGUF
    Quantization: Q4_K_M (good quality, small size)
    Size: ~320MB
    """

    print("=" * 70)
    print("Downloading Qwen 2.5 0.5B Instruct GGUF")
    print("=" * 70)
    print()

    # Configuration
    repo_id = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    filename = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    local_dir = Path("E:/HoloIndex/models")

    print(f"Repository: {repo_id}")
    print(f"File: {filename}")
    print(f"Destination: {local_dir}")
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
    print("           This may take a few minutes...")
    print()

    try:
        # Download the file
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False  # Copy file instead of symlink
        )

        print()
        print("[SUCCESS] Download complete!")
        print(f"          Model saved to: {downloaded_path}")

        # Verify file size
        size_mb = Path(downloaded_path).stat().st_size / (1024 * 1024)
        print(f"          File size: {size_mb:.1f} MB")
        print()

        return downloaded_path

    except Exception as e:
        print()
        print(f"[ERROR] Download failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("  2. Install huggingface_hub: pip install huggingface_hub")
        print("  3. Verify E:/HoloIndex/models is writable")
        print()
        sys.exit(1)


def verify_model(model_path: str):
    """Verify the downloaded model can be loaded"""
    print("=" * 70)
    print("Verifying Model Installation")
    print("=" * 70)
    print()

    try:
        from llama_cpp import Llama

        print("[TEST] Loading model with llama-cpp-python...")

        # Try to load the model
        llm = Llama(
            model_path=model_path,
            n_ctx=512,  # Small context for testing
            n_threads=2,
            n_gpu_layers=0,
            verbose=False
        )

        print("[SUCCESS] Model loaded successfully!")
        print()

        # Test inference
        print("[TEST] Running inference test...")
        response = llm(
            "Is this a WSP file naming violation? modules/test/WSP_AUDIT.md",
            max_tokens=50,
            temperature=0.1
        )

        print("[SUCCESS] Inference test passed!")
        print()
        print("Model is ready for use!")
        print()

        # Cleanup
        del llm

        return True

    except ImportError:
        print("[WARNING] llama-cpp-python not installed")
        print("          Install with: pip install llama-cpp-python")
        print()
        print("Model downloaded but not verified.")
        return False

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        print()
        print("Model downloaded but failed to load.")
        print("Check llama-cpp-python installation.")
        return False


if __name__ == "__main__":
    print()
    print("Qwen 2.5 0.5B Instruct Download Script")
    print("For WSP 57 File Naming Enforcement")
    print()

    # Download model
    model_path = download_qwen_0_5b()

    # Verify installation
    print()
    verify_success = verify_model(model_path)

    print()
    print("=" * 70)
    print("Next Steps")
    print("=" * 70)
    print()

    if verify_success:
        print("1. Model is ready to use!")
        print("2. Run file naming test:")
        print("   python holo_index/tests/test_qwen_file_naming_trainer.py")
        print()
        print("3. Configure as default for file naming:")
        print(f"   export HOLO_QWEN_MODEL={model_path}")
        print()
    else:
        print("1. Install llama-cpp-python:")
        print("   pip install llama-cpp-python")
        print()
        print("2. Then verify model:")
        print(f"   python -c \"from llama_cpp import Llama; Llama(model_path='{model_path}')\"")
        print()

    print("Model comparison:")
    print(f"  - qwen-coder-1.5b.gguf: 1.1GB, slower, better code understanding")
    print(f"  - qwen2.5-0.5b-instruct-q4_k_m.gguf: 320MB, faster, good for classification")
    print()
    print("For file naming enforcement, use the 0.5B model (3-5x faster).")
    print()

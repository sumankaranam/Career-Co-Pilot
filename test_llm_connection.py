#!/usr/bin/env python3
"""
Quick test script to verify local LLM connection
"""
import requests
import sys

def test_ollama():
    """Test Ollama connection"""
    print("Testing Ollama at http://localhost:11434...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": "Hello",
                "stream": False
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Ollama is running and responding!")
            result = response.json()
            print(f"Response: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("   Make sure to run: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_custom_llm():
    """Test custom LLM server"""
    print("\nTesting custom LLM at http://localhost:8000...")
    try:
        response = requests.post(
            "http://localhost:8000/generate",
            json={
                "prompt": "Hello",
                "max_tokens": 10,
                "temperature": 0.7
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Custom LLM server is running!")
            return True
        else:
            print(f"❌ Custom LLM returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to custom LLM at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Local LLM Connection Test\n" + "="*50)
    
    ollama_ok = test_ollama()
    custom_ok = test_custom_llm()
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"  Ollama (11434): {'✅ OK' if ollama_ok else '❌ FAILED'}")
    print(f"  Custom LLM (8000): {'✅ OK' if custom_ok else '❌ FAILED'}")
    
    if not (ollama_ok or custom_ok):
        print("\n⚠️  NO LLM SERVER RUNNING!")
        print("\nTo start Ollama:")
        print("  1. Install from: https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. In another terminal: ollama pull llama3.1")
        sys.exit(1)
    else:
        print("\n✅ LLM is ready!")
        sys.exit(0)

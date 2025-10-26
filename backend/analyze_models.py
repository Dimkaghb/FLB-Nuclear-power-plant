#!/usr/bin/env python3
"""
Model Analysis Script for FLB Nuclear Power Plant
Analyzes ONNX models to understand their structure and requirements.
"""

import os
import sys
from pathlib import Path
import onnxruntime as ort
import numpy as np

def analyze_model(model_path: Path) -> dict:
    """
    Analyze an ONNX model and return its metadata.
    
    Args:
        model_path: Path to the ONNX model file
        
    Returns:
        dict: Model metadata including inputs, outputs, and shapes
    """
    try:
        # Create ONNX Runtime session
        session = ort.InferenceSession(str(model_path))
        
        # Get model metadata
        metadata = {
            "model_name": model_path.stem,
            "file_path": str(model_path),
            "file_size_mb": model_path.stat().st_size / (1024 * 1024),
            "inputs": [],
            "outputs": []
        }
        
        # Analyze inputs
        for input_info in session.get_inputs():
            metadata["inputs"].append({
                "name": input_info.name,
                "shape": input_info.shape,
                "type": input_info.type
            })
        
        # Analyze outputs
        for output_info in session.get_outputs():
            metadata["outputs"].append({
                "name": output_info.name,
                "shape": output_info.shape,
                "type": output_info.type
            })
        
        return metadata
        
    except Exception as e:
        return {
            "model_name": model_path.stem,
            "error": str(e)
        }

def main():
    """Main function to analyze all models in the AI directory."""
    # Get the AI models directory
    ai_dir = Path(__file__).parent / "ai"
    
    if not ai_dir.exists():
        print(f"AI directory not found: {ai_dir}")
        return
    
    # Find all ONNX files
    onnx_files = list(ai_dir.glob("*.onnx"))
    
    if not onnx_files:
        print(f"No ONNX files found in {ai_dir}")
        return
    
    print("=" * 80)
    print("FLB Nuclear Power Plant - Model Analysis Report")
    print("=" * 80)
    print(f"Analyzing {len(onnx_files)} models in: {ai_dir}")
    print()
    
    for model_path in sorted(onnx_files):
        print(f"Analyzing: {model_path.name}")
        print("-" * 60)
        
        metadata = analyze_model(model_path)
        
        if "error" in metadata:
            print(f"❌ Error: {metadata['error']}")
        else:
            print(f"📁 File Size: {metadata['file_size_mb']:.2f} MB")
            print(f"📥 Inputs ({len(metadata['inputs'])}):")
            for i, input_info in enumerate(metadata['inputs']):
                print(f"   {i+1}. {input_info['name']}: {input_info['shape']} ({input_info['type']})")
            
            print(f"📤 Outputs ({len(metadata['outputs'])}):")
            for i, output_info in enumerate(metadata['outputs']):
                print(f"   {i+1}. {output_info['name']}: {output_info['shape']} ({output_info['type']})")
            
            # Determine model type
            model_name = metadata['model_name'].lower()
            if 'clf' in model_name:
                model_type = "Classification"
            elif 'reg' in model_name:
                model_type = "Regression"
            else:
                model_type = "Unknown"
            
            print(f"🔍 Detected Type: {model_type}")
            
            # Check for version information
            if 'v2' in model_name:
                print("🆕 Version: v2 (New Model)")
            elif 'v1' in model_name:
                print("📦 Version: v1 (Legacy Model)")
            else:
                print("📦 Version: Unspecified")
        
        print()

if __name__ == "__main__":
    main()
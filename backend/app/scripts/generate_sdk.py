"""
SDK generation script.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi.openapi.utils import get_openapi

from app.api import app

logger = logging.getLogger(__name__)


def generate_openapi_spec():
    """Generate OpenAPI specification."""
    logger.info("Generating OpenAPI specification...")
    
    try:
        # Generate OpenAPI spec
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Write to file
        spec_path = Path(__file__).parent.parent.parent / "openapi.json"
        with open(spec_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
        
        logger.info(f"OpenAPI spec written to {spec_path}")
        return spec_path
        
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {e}")
        raise


def generate_typescript_types(spec_path: Path):
    """Generate TypeScript types from OpenAPI spec."""
    logger.info("Generating TypeScript types...")
    
    try:
        # Path to types package
        types_path = Path(__file__).parent.parent.parent.parent / "packages" / "types"
        
        # Run openapi-typescript
        cmd = [
            "npx", "openapi-typescript", 
            str(spec_path), 
            "-o", str(types_path / "src" / "api.ts")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=types_path)
        
        if result.returncode != 0:
            logger.error(f"Error generating TypeScript types: {result.stderr}")
            raise RuntimeError(f"TypeScript generation failed: {result.stderr}")
        
        logger.info("TypeScript types generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating TypeScript types: {e}")
        raise


def generate_javascript_sdk(spec_path: Path):
    """Generate JavaScript SDK from OpenAPI spec."""
    logger.info("Generating JavaScript SDK...")
    
    try:
        # Path to SDK package
        sdk_path = Path(__file__).parent.parent.parent.parent / "packages" / "sdk-js"
        
        # Run openapi-generator
        cmd = [
            "npx", "@openapitools/openapi-generator-cli", "generate",
            "-i", str(spec_path),
            "-g", "typescript-fetch",
            "-o", str(sdk_path / "src" / "generated"),
            "--additional-properties=typescriptThreePlus=true,supportsES6=true"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sdk_path)
        
        if result.returncode != 0:
            logger.error(f"Error generating JavaScript SDK: {result.stderr}")
            raise RuntimeError(f"SDK generation failed: {result.stderr}")
        
        logger.info("JavaScript SDK generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating JavaScript SDK: {e}")
        raise


def build_packages():
    """Build the generated packages."""
    logger.info("Building packages...")
    
    try:
        # Build types package
        types_path = Path(__file__).parent.parent.parent.parent / "packages" / "types"
        result = subprocess.run(["pnpm", "build"], cwd=types_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error building types package: {result.stderr}")
            raise RuntimeError(f"Types build failed: {result.stderr}")
        
        # Build SDK package
        sdk_path = Path(__file__).parent.parent.parent.parent / "packages" / "sdk-js"
        result = subprocess.run(["pnpm", "build"], cwd=sdk_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error building SDK package: {result.stderr}")
            raise RuntimeError(f"SDK build failed: {result.stderr}")
        
        logger.info("Packages built successfully")
        
    except Exception as e:
        logger.error(f"Error building packages: {e}")
        raise


def main():
    """Main SDK generation function."""
    logger.info("Starting SDK generation...")
    
    try:
        # Generate OpenAPI spec
        spec_path = generate_openapi_spec()
        
        # Generate TypeScript types
        generate_typescript_types(spec_path)
        
        # Generate JavaScript SDK
        generate_javascript_sdk(spec_path)
        
        # Build packages
        build_packages()
        
        logger.info("SDK generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during SDK generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

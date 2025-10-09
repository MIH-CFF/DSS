"""
Main application entry point with new plugin-based architecture.
Supports both desktop GUI and REST API server modes.
"""
import sys
import argparse


def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(description="DSS - DNA Sequence Similarity Analysis")
    parser.add_argument("--mode", choices=["gui", "api"], default="gui",
                       help="Run mode: gui (desktop application) or api (REST server)")
    parser.add_argument("--host", default="127.0.0.1", help="API server host")
    parser.add_argument("--port", type=int, default=8000, help="API server port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        from src.ui import main as gui_main
        gui_main()
    elif args.mode == "api":
        import uvicorn
        uvicorn.run(
            "src.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )


if __name__ == "__main__":
    main()

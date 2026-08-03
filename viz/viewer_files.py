"""Entry point: python -m viz.viewer_files path/to/a.h5 path/to/b.h5 ...

Serves the same read-only browser viewer as viz/viewer.py, but against
arbitrary pre-existing .h5 files instead of a pipeline config — useful for
inspecting files that weren't produced by run_tsvp.py (e.g. raw captures).
Does not run the pipeline itself.
"""
import os
import sys
import webbrowser
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from viz.viewer import create_viz_app_from_files, find_available_port


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Standalone viewer for arbitrary .h5 files (no pipeline config needed)')
    parser.add_argument('h5_files', nargs='+',
                        help='Paths to .h5 files to visualize. Prefix a path with "thw:" if its '
                             'datasets are laid out (T, H, W) on disk (e.g. a raw sensor capture) '
                             'instead of the viewer\'s usual (H, W, T).')
    parser.add_argument('--bind', action='store_true',
                        help='Bind to 0.0.0.0 instead of localhost')
    args = parser.parse_args()

    h5_paths = []
    for p in args.h5_files:
        thw_prefix = 'thw:' if p.startswith('thw:') else ''
        raw = p[len(thw_prefix):]
        resolved = Path(raw).resolve()
        if not resolved.exists():
            print(f"File not found: {resolved}", file=sys.stderr)
            sys.exit(1)
        h5_paths.append(f"{thw_prefix}{resolved}")

    app = create_viz_app_from_files(h5_paths)

    host = '0.0.0.0' if args.bind else os.environ.get('VIEWER_HOST', 'localhost')
    port = int(os.environ.get('VIEWER_PORT', '8765'))
    port = find_available_port(port)

    if args.bind:
        print("WARNING: --bind exposes the viewer on all network interfaces with no authentication.")

    print("Starting standalone video viewer (file mode)")
    print(f"Files:  {', '.join(h5_paths)}")
    print(f"Bind:   {host}:{port}")
    print(f"URL:    http://localhost:{port}")

    # Open browser after a short delay
    def _open():
        import time; time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')

    import threading
    threading.Thread(target=_open, daemon=True).start()

    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level='info')


if __name__ == '__main__':
    main()

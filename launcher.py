import subprocess
import webbrowser
import time
import os
import sys

def kill_port_3000():
    """Kill any process listening on port 3000."""
    try:
        # Find PID using netstat
        cmd = 'netstat -ano | findstr :3000'
        # Run command, capture output
        # creationflags=0x08000000 (CREATE_NO_WINDOW) to avoid flashing window if compiled
        output = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode()
        
        pids = set()
        for line in output.splitlines():
            parts = line.split()
            # Line format: TCP 0.0.0.0:3000 0.0.0.0:0 LISTENING 1234
            if 'LISTENING' in line:
                pid = parts[-1]
                pids.add(pid)
        
        for pid in pids:
            print(f"Killing process {pid} on port 3000...")
            subprocess.call(f'taskkill /F /PID {pid}', shell=True, creationflags=0x08000000)
    except subprocess.CalledProcessError:
        # netstat returns non-zero if no match found
        pass
    except Exception as e:
        print(f"Error killing port 3000: {e}")

def main():
    print("Initializing Account Book...")
    
    # 1. Clean up port 3000
    kill_port_3000()

    # 2. Define paths
    # Using absolute paths as requested, but verifying existence
    app_path = r'D:\accountBook\accountBook\app.py'
    html_path = r'D:\accountBook\accountBook\templates\index.html'
    
    # Fallback check if user meant a different location or if we are portable
    if not os.path.exists(app_path):
        # Try checking current directory
        cwd_app = os.path.join(os.getcwd(), 'app.py')
        if os.path.exists(cwd_app):
            app_path = cwd_app
        else:
            print(f"Error: Could not find app.py at {app_path}")
            input("Press Enter to exit...")
            return

    if not os.path.exists(html_path):
        print(f"Warning: Could not find index.html at {html_path}")

    # 3. Start the server
    print(f"Starting server: {app_path}")
    # We assume 'python' is in PATH. 
    # If this is run from an env where python is set up, it works.
    try:
        # Use Popen to run in background
        server_process = subprocess.Popen(['python', app_path], shell=True)
    except Exception as e:
        print(f"Failed to start server: {e}")
        input("Press Enter to exit...")
        return

    # 4. Wait for server to initialize
    print("Waiting for server to start...")
    time.sleep(3)

    # 5. Open the HTML file
    # User requested: access localhost:3000
    target_url = 'http://localhost:3000'
    print(f"Opening {target_url}...")
    webbrowser.open(target_url)
    
    # Also open localhost for convenience/robustness? 
    # No, stick to user instructions.
    
    print("\n" + "="*50)
    print(" Application is running!")
    print(" Close this window to stop the server.")
    print("="*50)

    try:
        # Keep the launcher alive
        while True:
            time.sleep(1)
            # Check if server process is still alive?
            if server_process.poll() is not None:
                print("Server process ended unexpectedly.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping server...")
        # Kill the server process tree
        subprocess.call(f'taskkill /F /T /PID {server_process.pid}', shell=True)
        time.sleep(1)

if __name__ == '__main__':
    main()

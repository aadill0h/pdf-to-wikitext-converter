# File: app.py
import os
import sys
import docker
import tempfile
import shutil
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

# --- Configuration ---
DOCKER_IMAGE_NAME = "pdf-converter-isolated:latest"
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the uploaded file has a .pdf extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_docker_image_once(client):
    """Builds the Docker image if it doesn't already exist."""
    try:
        client.images.get(DOCKER_IMAGE_NAME)
        print(f"Docker image '{DOCKER_IMAGE_NAME}' already exists. Skipping build.")
    except docker.errors.ImageNotFound:
        print(f"Docker image '{DOCKER_IMAGE_NAME}' not found. Building...")
        try:
            client.images.build(
                path=".",
                dockerfile="Dockerfile",
                tag=DOCKER_IMAGE_NAME,
                rm=True
            )
            print("Docker image built successfully.")
        except docker.errors.BuildError as e:
            print("--- DOCKER BUILD FAILED ---", file=sys.stderr)
            for line in e.build_log:
                if 'stream' in line:
                    print(line['stream'].strip(), file=sys.stderr)
            # Exit the app if the image can't be built
            sys.exit("Critical error: Docker image could not be built.")

def run_conversion_in_container(client, host_dir, pdf_filename):
    """Runs the conversion in a container and returns the result path."""
    print(f"Starting container for file: {pdf_filename}")
    try:
        client.containers.run(
            image=DOCKER_IMAGE_NAME,
            command=[pdf_filename],
            volumes={host_dir: {'bind': '/data', 'mode': 'rw'}},
            remove=True # Essential for statelessness
        )
        base_name = os.path.splitext(pdf_filename)[0]
        result_filename = f"{base_name}_wikitext.txt"
        return os.path.join(host_dir, result_filename)
    except docker.errors.ContainerError as e:
        print(f"--- CONTAINER FAILED --- \n{e.stderr.decode('utf-8')}", file=sys.stderr)
        raise RuntimeError("The conversion process inside the container failed.")
    except Exception as e:
        print(f"An unexpected Docker error occurred: {e}", file=sys.stderr)
        raise

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Just show the main page
        return render_template('index.html')

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdf_file' not in request.files:
            return render_template('index.html', error="No file part in the request.")
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            return render_template('index.html', error="No file selected.")

        if file and allowed_file(file.filename):
            # Sanitize the filename for security
            filename = secure_filename(file.filename)
            
            # Create a secure, temporary directory for this one request
            temp_dir = tempfile.mkdtemp()
            print(f"Created temporary directory: {temp_dir}")
            
            try:
                pdf_path = os.path.join(temp_dir, filename)
                file.save(pdf_path)

                # Get Docker client and run the conversion
                docker_client = docker.from_env()
                result_path = run_conversion_in_container(docker_client, temp_dir, filename)

                # Read the result from the output file
                with open(result_path, 'r', encoding='utf-8') as f:
                    wikitext_content = f.read()

                return render_template('index.html', wikitext=wikitext_content)

            except Exception as e:
                print(f"An error occurred during processing: {e}")
                return render_template('index.html', error=str(e))
            
            finally:
                # CRITICAL: Clean up the temporary directory and its contents
                if os.path.exists(temp_dir):
                    print(f"Removing temporary directory: {temp_dir}")
                    shutil.rmtree(temp_dir)
        else:
            return render_template('index.html', error="Invalid file type. Please upload a PDF.")

if __name__ == '__main__':
    # Ensure Docker is running and build the image on startup
    try:
        docker_client = docker.from_env()
        build_docker_image_once(docker_client)
    except Exception as e:
        sys.exit(f"Failed to connect to Docker or build image. Is Docker running? Error: {e}")

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0')

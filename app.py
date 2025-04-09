import gradio as gr
from src.main import create_gradio

# Create the Gradio interface
demo = create_gradio()

# Launch for Hugging Face Spaces
demo.launch(
    server_name="0.0.0.0",  # Required for Hugging Face Spaces
    share=False,  # Don't create a public link since we're deploying on Spaces
)

import gradio as gr
import os
from pathlib import Path
from typing import Tuple, Dict, List


# Validate if the uploaded file format is valid
# Parameters: file_path - Path of the uploaded file
# Return: Tuple (validation result [bool], error message [str])
def validate_file_format(file_path: str) -> Tuple[bool, str]:
    valid_extensions = {".pdf", ".docx", ".txt"}
    file_ext = Path(file_path).suffix.lower()

    if file_ext not in valid_extensions:
        return False, f"Unsupported format ({file_ext}), only {valid_extensions} are allowed"
    return True, ""


# Preview the first few lines of the file (example)
# Parameters: file_path - Path of the file; max_lines - Maximum number of preview lines (default 5)
# Return: Preview content string
def preview_file_content(file_path: str, max_lines: int = 5) -> str:
    # simulating content here
    preview = f"[File Preview] {os.path.basename(file_path)}\n"
    preview += "=" * 30 + "\n"
    return "preview completed"


# Simulate the grading process
# Parameters: paper_file - Path of the exam paper file; answer_file - Path of the answer file
# Return: Grading result dictionary
def simulate_marking(paper_file: str, answer_file: str) -> Dict[str, any]:
    # Simulate grading result
    result = {
        "paper_name": os.path.basename(paper_file),
        "answer_name": os.path.basename(answer_file),
        "score": round(85 + (hash(paper_file) % 15), 1),  # Simulate score between 85-100
        "evaluation": [
            "Covers all knowledge points",
            "Clear logic, but some steps can be more detailed",
            "Standard format with complete annotations",
            "New record! Highest score!"
        ],
        "error": ""
    }
    return result


# Main processing function
# Parameters: paper_file - Uploaded exam paper; answer_file - Uploaded answer; progress - Progress bar component
# Return: Tuple (preview content, grading result, error message)
def process_submission(paper_file: str, answer_file: str, progress=gr.Progress()) -> Tuple[str, str, str]:
    error_msg = ""

    # Check if files are fully uploaded
    if not paper_file or not answer_file:
        error_msg = "Please upload both exam paper and answer files"
        return "", "", error_msg

    # Validate file formats
    for file_path in [paper_file, answer_file]:
        valid, msg = validate_file_format(file_path)
        if not valid:
            error_msg = f"File validation failed: {msg}"
            return "", "", error_msg

    progress(0, desc="Starting processing...")

    # Generate file previews
    paper_preview = preview_file_content(paper_file)
    answer_preview = preview_file_content(answer_file)
    full_preview = f"[Exam Paper Preview]\n{paper_preview}\n\n[Answer Preview]\n{answer_preview}"

    progress(0.5, desc="Grading in progress...")

    # Perform grading
    marking_result = simulate_marking(paper_file, answer_file)

    # Format grading result
    result_str = (
        f"Grading completed!\n"
        f"Exam Paper: {marking_result['paper_name']}\n"
        f"Answer: {marking_result['answer_name']}\n"
        f"Score: {marking_result['score']}/100\n"
        f"Evaluation:\n" + "\n".join([f"- {item}" for item in marking_result['evaluation']])
    )

    progress(1.0, desc="Processing completed")
    return full_preview, result_str, error_msg


# Create Gradio interface
def create_gui():
    with gr.Blocks(title="Automatic Exam Paper Grading System - GUI") as demo:
        gr.Markdown("# 📝 Automatic Exam Paper Grading System")
        gr.Markdown("Please drag and drop or select exam paper and answer files (supports pdf/docx/txt), the system will process automatically and return results")

        with gr.Row():
            # Left input area
            with gr.Column(scale=1):
                paper_input = gr.File(label="Upload Exam Paper", file_types=[".pdf", ".docx", ".txt"])
                answer_input = gr.File(label="Upload Answer", file_types=[".pdf", ".docx", ".txt"])
                process_btn = gr.Button("Start Processing", variant="primary")

            # Right output area
            with gr.Column(scale=2):
                preview_output = gr.Textbox(label="File Content Preview", lines=10)
                result_output = gr.Textbox(label="Grading Result", lines=8)
                error_output = gr.Textbox(label="Error Message", lines=2, interactive=False)

        # Bind button event
        process_btn.click(
            fn=process_submission,
            inputs=[paper_input, answer_input],
            outputs=[preview_output, result_output, error_output]
        )

        # Instructions
        gr.Markdown("""
        ### Instructions
        1. Upload student's exam paper and reference answer
        2. Click the "Start Processing" button
        3. The system will validate formats, preview content and simulate grading
        4. Results will be displayed in the right area
        """)

    return demo


if __name__ == "__main__":
    gui = create_gui()
    gui.launch(debug=True)
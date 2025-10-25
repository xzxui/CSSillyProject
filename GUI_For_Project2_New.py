import gradio as gr
import os
from pathlib import Path
from typing import Tuple, Dict, List
# Import required modules
import ModuleMarkPaper
import ModuleProduceFeedbackForStudent


# Validate uploaded file format
def validate_file_format(file_path: str) -> Tuple[bool, str]:
    valid_extensions = {".pdf", ".docx", ".txt"}
    file_ext = Path(file_path).suffix.lower()

    if file_ext not in valid_extensions:
        return False, f"Unsupported format ({file_ext}), only {valid_extensions} are allowed"
    return True, ""


# Preview file content (can be extended based on actual needs, basic framework retained here)
def preview_file_content(file_path: str, max_lines: int = 5) -> str:
    try:
        # Basic text file preview (add pdf/docx parsing based on file type in actual use)
        if file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f.readlines()[:max_lines]]
                return "\n".join(lines) or "File content is empty"
        else:
            return f"[{os.path.basename(file_path)}] Preview available (non-text file)"
    except Exception as e:
        return f"Preview failed: {str(e)}"


# Main processing function (integrated new module calls)
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
            error_msg = f"File format validation failed: {msg}"
            return "", "", error_msg

    progress(0.2, desc="Starting file processing...")

    # Generate file previews
    paper_preview = preview_file_content(paper_file)
    answer_preview = preview_file_content(answer_file)
    full_preview = (
        f"[Exam Paper Preview]\n{paper_preview}\n\n"
        f"[Answer Preview]\n{answer_preview}"
    )

    progress(0.4, desc="Grading in progress...")

    try:
        # Call grading module to get score
        marking_result = ModuleMarkPaper.MarkPaper(paper_file, answer_file)
        # Check if grading result contains necessary score information
        if "score" not in marking_result:
            raise ValueError("Invalid grading result format - score information missing")

        progress(0.7, desc="Generating feedback...")

        # Call feedback generation module
        feedback = ModuleProduceFeedbackForStudent.ProduceFeedbackForStudent(
            paper_file, answer_file, marking_result["score"]
        )
        # Ensure feedback is in list format
        if not isinstance(feedback, list):
            feedback = [str(feedback)]

    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        return full_preview, "", error_msg

    progress(0.9, desc="Organizing results...")

    # Format grading result
    result_str = (
            f"Grading completed!\n"
            f"Exam Paper: {os.path.basename(paper_file)}\n"
            f"Reference Answer: {os.path.basename(answer_file)}\n"
            f"Score: {marking_result['score']}/100\n"
            f"Feedback:\n" + "\n".join([f"- {item}" for item in feedback])
    )

    progress(1.0, desc="Processing completed")
    return full_preview, result_str, error_msg


# Create Gradio interface
def create_gui():
    with gr.Blocks(title="Automatic Exam Paper Grading System") as demo:
        gr.Markdown("# 📝 Automatic Exam Paper Grading System")
        gr.Markdown(
            "Please upload exam paper and reference answer files (supports pdf/docx/txt). The system will automatically grade and generate feedback.")

        with gr.Row():
            # Left input area
            with gr.Column(scale=1):
                paper_input = gr.File(label="Upload Exam Paper", file_types=[".pdf", ".docx", ".txt"])
                answer_input = gr.File(label="Upload Reference Answer", file_types=[".pdf", ".docx", ".txt"])
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
        1. Upload the student's exam paper and reference answer files
        2. Click the "Start Processing" button
        3. The system will validate file formats, preview content, and call the grading and feedback generation modules
        4. Results will be displayed in the right area

        Note: Grading logic is provided by ModuleMarkPaper, and feedback content is generated by ModuleProduceFeedbackForStudent
        """)

    return demo


if __name__ == "__main__":
    gui = create_gui()
    gui.launch(debug=True)
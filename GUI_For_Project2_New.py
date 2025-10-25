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
def process_submission(paper_file: str, answer_file: str, threshold_file: str, progress=gr.Progress()) -> Tuple[str, str, str]:
    error_msg = ""

    # Check if files are fully uploaded
    if not paper_file or not answer_file or not threshold_file:
        error_msg = "Please upload both the exam paper, the marking scheme and the grading threshold table"
        return "", error_msg

    # Validate file formats
    for file_path in [paper_file, answer_file, threshold_file]:
        valid, msg = validate_file_format(file_path)
        if not valid:
            error_msg = f"File format validation failed: {msg}"
            return "", error_msg

    progress(0.05, desc="Starting file processing...")

    # Generate file previews
    paper_preview = preview_file_content(paper_file)
    answer_preview = preview_file_content(answer_file)
    threshold_preview = preview_file_content(threshold_file)

    progress(0.1, desc="Grading in progress...")

    try:
        # Call marking module
        score, max_score, grade, pros, cons = ModuleMarkPaper.MarkPaper(paper_file, answer_file, threshold_file)
        progress(0.8, desc="Generating feedback...")

        # Call feedback generation module
        comment_based_on_history = ModuleProduceFeedbackForStudent.ProduceFeedbackForStudent()

    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        return "", error_msg

    progress(0.95, desc="Organizing results...")

    # Format grading result
    result_str = (
            f"Grading completed!\n"
            f"Exam Paper: {os.path.basename(paper_file)}\n"
            f"Reference Answer: {os.path.basename(answer_file)}\n"
            f"Score: {score}/{max_score}\n"
            f"Grade: {grade}\n"
            f"Strengths: {pros}\n"
            f"Weaknesses: {cons}\n"
            f"Feedback: {comment_based_on_history}\n"
    )

    progress(1.0, desc="Processing completed")
    return result_str, error_msg


# Create Gradio interface
def create_gui():
    with gr.Blocks(title="Automatic Exam Paper Grading System") as demo:
        gr.Markdown("# 📝 Automatic Exam Paper Grading System")
        gr.Markdown(
            "Please upload exam paper and reference answer files (supports pdf/docx/txt). The system will automatically grade and generate feedback.")

        with gr.Row():
            # Left input area
            with gr.Column(scale=1):
                paper_input = gr.File(label="Upload Completed Question Paper", file_types=[".pdf"])
                answer_input = gr.File(label="Upload Marking Scheme", file_types=[".pdf"])
                threshold_input = gr.File(label="Upload Grading Threshold Table", file_types=[".pdf"])
                process_btn = gr.Button("Start Processing", variant="primary")

            # Right output area
            with gr.Column(scale=2):
                result_output = gr.Textbox(label="Grading Result", lines=8)
                error_output = gr.Textbox(label="Error Message", lines=2, interactive=False)

        # Bind button event
        process_btn.click(
            fn=process_submission,
            inputs=[paper_input, answer_input, threshold_input],
            outputs=[result_output, error_output]
        )

        # Instructions
        gr.Markdown("""
        ### Instructions
        1. Upload the student's completed question paper, the marking scheme and the grading threshold table
        2. Click the "Start Processing" button. This should take fewer than 10 minutes.
        3. The system will validate file formats, preview content, and call the grading and feedback generation modules
        4. Results will be displayed in the right area

        Note: Grading logic is provided by ModuleMarkPaper, and feedback content is generated by ModuleProduceFeedbackForStudent
        """)

    return demo


if __name__ == "__main__":
    gui = create_gui()
    gui.launch(debug=True)

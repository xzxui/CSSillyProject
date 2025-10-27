import configs
import pymupdf
import base64

def PDF2b64s(pdf_path):
    """
    Args:
        1. pdf_path (<class 'str'>)
    Return:
        an instance of <class 'list'>, each element being a <class 'str'>, which is a base 64 image converted from a page in the pdf
    Process:
        Convert the pdf into base 64 images, and the base 64 images should be stored in a bunch of <class 'str'>
    """
    doc = pymupdf.open(pdf_path)
    b64_imgs = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # set to better resolution for better OCR by AI
        mat = pymupdf.Matrix(1.5, 1.5)  # scaling to make it clearer
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes(configs.img_extension)
        b64_imgs.append(base64.b64encode(img_data).decode('utf-8'))
    
    doc.close()
    return b64_imgs

# For testing
if __name__ == "__main__":
    print("Converting")
    b64_imgs = PDF2b64s("test_folder/ModulePDF2b64s/original1.pdf")
    print("Done converting")
    with open("test_folder/ModulePDF2b64s/last_page2.png", "wb") as f:
        f.write(base64.b64decode(b64_imgs[-1]))
    print("Last page saved")
    with open("test_folder/ModulePDF2b64s/first_page2.png", "wb") as f:
        f.write(base64.b64decode(b64_imgs[0]))
    print("First page saved\n")
    
    print("Converting")
    b64_imgs = PDF2b64s("test_folder/ModulePDF2b64s/original2.pdf")
    print("Done converting")
    with open("test_folder/ModulePDF2b64s/last_page2.png", "wb") as f:
        f.write(base64.b64decode(b64_imgs[-1]))
    print("Last page saved")
    with open("test_folder/ModulePDF2b64s/first_page2.png", "wb") as f:
        f.write(base64.b64decode(b64_imgs[0]))
    print("First page saved\n")

    print(b64_imgs[-1])


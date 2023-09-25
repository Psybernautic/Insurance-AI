#                     ____   ___   ____ _   _ __  __ _____ _   _ _____      _    ___ 
#                    |  _ \ / _ \ / ___| | | |  \/  | ____| \ | |_   _|    / \  |_ _|
#                    | | | | | | | |   | | | | |\/| |  _| |  \| | | |     / _ \  | | 
#                    | |_| | |_| | |___| |_| | |  | | |___| |\  | | |    / ___ \ | | 
#                    |____/ \___/ \____|\___/|_|  |_|_____|_| \_| |_|   /_/   \_\___|
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------                   


#   Project         :   Insurance-AI 
#   File            :   document_ai_functions.py
#   Programmers     :   Alonzo Gutierrez, Sebastian Posada
#   Description     :   This module provides functions for interacting with Google Cloud Document AI.
#                       It includes functions for processing documents, extracting text and layout information,
#                       and printing information about detected tokens, languages, and page dimensions.

#   First Version   :   September 11, 2023

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from typing import Optional, Sequence
import os

# TODO(developer): Uncomment these variables before running the sample.
project_id = 'loadaccess'
location = 'us' # Format is 'us' or 'eu'
processor_id = '12bc9b18db8b8b92' #  Create processor before running sample
file_path = ''
mime_type = 'application/pdf' # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\sposada\Downloads\loadaccess-fbd47a118e0b.json"


def quickstart(
    project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
):
    # You must set the api_endpoint if you use a location other than 'us'.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project_id/locations/location/processor/processor_id
    name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    response = client.process_document(request=request)

    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
    #document = response.document

    return response
    # print(document)

def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document"s text. This function converts
    offsets to a string.
    """
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )

def print_tokens(tokens: Sequence[documentai.Document.Page.Token], text: str) -> None:
    """
    Print information about detected tokens in a Document AI analysis result.

    Args:
        tokens (Sequence[documentai.Document.Page.Token]): A list of tokens detected in the document.
        text (str): The original text content of the document.

    Returns:
        None
    """
    print(f"    {len(tokens)} tokens detected:")  # Print the total number of tokens
    # Information about the first token
    first_token_text = layout_to_text(tokens[0].layout, text)
    first_token_break_type = tokens[0].detected_break.type_.name
    print(f"        First token text: {repr(first_token_text)}")  # Print the text of the first token
    print(f"        First token break type: {repr(first_token_break_type)}")  # Print the break type of the first token
    # Information about the last token
    last_token_text = layout_to_text(tokens[-1].layout, text)
    last_token_break_type = tokens[-1].detected_break.type_.name
    print(f"        Last token text: {repr(last_token_text)}")  # Print the text of the last token
    print(f"        Last token break type: {repr(last_token_break_type)}")  # Print the break type of the last token

def print_page_dimensions(dimension: documentai.Document.Page.Dimension) -> None:
    """
    Print the width and height dimensions of a page in a Document AI analysis result.

    Args:
        dimension (documentai.Document.Page.Dimension): The dimensions of the page.

    Returns:
        None
    """
    print(f"    Width: {str(dimension.width)}")  # Print the width of the page
    print(f"    Height: {str(dimension.height)}")  # Print the height of the page


def print_detected_langauges(
    detected_languages: Sequence[documentai.Document.Page.DetectedLanguage],
) -> None:
    print("    Detected languages:")
    for lang in detected_languages:
        print(f"        {lang.language_code} ({lang.confidence:.1%} confidence)")


def print_blocks(blocks: Sequence[documentai.Document.Page.Block], text: str) -> None:
    print(f"    {len(blocks)} blocks detected:")
    first_block_text = layout_to_text(blocks[0].layout, text)
    print(f"        First text block: {repr(first_block_text)}")
    last_block_text = layout_to_text(blocks[-1].layout, text)
    print(f"        Last text block: {repr(last_block_text)}")

def print_all_blocks(blocks: Sequence[documentai.Document.Page.Block], text: str) -> None:
    print(f"    {len(blocks)} blocks detected:")
    for block in blocks:
        block_text = layout_to_text(block.layout, text)
        #print(f"    Block text: {repr(block_text)}")
        #print("")


def print_paragraphs(
    paragraphs: Sequence[documentai.Document.Page.Paragraph], text: str
) -> None:
    print(f"    {len(paragraphs)} paragraphs detected:")
    first_paragraph_text = layout_to_text(paragraphs[0].layout, text)
    print(f"        First paragraph text: {repr(first_paragraph_text)}")
    last_paragraph_text = layout_to_text(paragraphs[-1].layout, text)
    print(f"        Last paragraph text: {repr(last_paragraph_text)}")


def print_lines(lines: Sequence[documentai.Document.Page.Line], text: str) -> None:
    print(f"    {len(lines)} lines detected:")
    first_line_text = layout_to_text(lines[0].layout, text)
    print(f"        First line text: {repr(first_line_text)}")
    last_line_text = layout_to_text(lines[-1].layout, text)
    print(f"        Last line text: {repr(last_line_text)}")


def print_symbols(
    symbols: Sequence[documentai.Document.Page.Symbol], text: str
) -> None:
    print(f"    {len(symbols)} symbols detected:")
    first_symbol_text = layout_to_text(symbols[0].layout, text)
    print(f"        First symbol text: {repr(first_symbol_text)}")
    last_symbol_text = layout_to_text(symbols[-1].layout, text)
    print(f"        Last symbol text: {repr(last_symbol_text)}")


def print_image_quality_scores(
    image_quality_scores: documentai.Document.Page.ImageQualityScores,
) -> None:
    print(f"    Quality score: {image_quality_scores.quality_score:.1%}")
    print("    Detected defects:")

    for detected_defect in image_quality_scores.detected_defects:
        print(f"        {detected_defect.type_}: {detected_defect.confidence:.1%}")


def print_styles(styles: Sequence[documentai.Document.Style], text: str) -> None:
    print(f"    {len(styles)} styles detected:")
    first_style_text = layout_to_text(styles[0].layout, text)
    print(f"        First style text: {repr(first_style_text)}")
    print(f"           Color: {styles[0].color}")
    print(f"           Background Color: {styles[0].background_color}")
    print(f"           Font Weight: {styles[0].font_weight}")
    print(f"           Text Style: {styles[0].text_style}")
    print(f"           Text Decoration: {styles[0].text_decoration}")
    print(f"           Font Size: {styles[0].font_size.size}{styles[0].font_size.unit}")
    print(f"           Font Family: {styles[0].font_family}")

def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document"s text. This function converts
    offsets to a string.
    """
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )

    
def show_all_info(document, pages, text):
    for page in pages:
        print(f"Page {page.page_number}:")
        print_page_dimensions(page.dimension)
        print_detected_langauges(page.detected_languages)
        

    if page.blocks:
        print_blocks(page.blocks, text)
        print_paragraphs(page.paragraphs, text)
        print_lines(page.lines, text)
        print_tokens(page.tokens, text)

    if page.symbols:
        print_symbols(page.symbols, text)

    if page.image_quality_scores:
        print_image_quality_scores(page.image_quality_scores)

    if document.text_styles:
        print_styles(document.text_styles, text)

    return page                                            
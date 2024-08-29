import chainlit as cl
from model import stream_gemini_response
from markdown_pdf import MarkdownPdf, Section
import PyPDF2
import docx

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_doc(file_path):
    doc = docx.Document(file_path)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])


@cl.on_chat_start

async def on_chat_start():
    text = """
Hey there!
 I am paddi for travel Agents, I can help you with anything relating to visa roadmaps
"""
    await cl.Message(content=text).send()
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    
    # Check if there's a file attached
    if message.elements:
        file_path = message.elements[0].path
        if file_path.lower().endswith('.pdf'):
            file_content = extract_text_from_pdf(file_path)
            message_content = file_content
            
        elif file_path.lower().endswith('.docx'):
            file_content = extract_text_from_doc(file_path)
            message_content = file_content
        else:
            await cl.Message(content="Unsupported file type. Please attach a .pdf or .docx file.").send()
            return
    else:
        message_content = message.content

    message_history.append({"role": "user", "content": message_content})
    
    msg = cl.Message(content="", author="Tommy")
    response = ""
    async for chunk in stream_gemini_response(message_content):
        await msg.stream_token(chunk)
        response += chunk
    await msg.send()
    

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
    
    pdf = MarkdownPdf()
    pdf.add_section(Section(response, toc=False))
    pdf.save('output2.pdf')
    
    
    if "ROADMAP" in response:
        await cl.Message(content="Download pdf", elements=[cl.File(name="Road_Map.pdf", path="output2.pdf")], author="Tommy").send()
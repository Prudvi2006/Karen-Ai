
# from langchain_core.outputs import chat_result
# from langchain_core.outputs import chat_result
# from fastapi import APIRouter, UploadFile, File, Depends
# # pyrefly: ignore [missing-import]
# from auth.dependencies import get_current_user
# # pyrefly: ignore [missing-import]
# from rag.vectordb import get_vector_store
# # pyrefly: ignore [missing-import]
# from rag.loader import extract_text_from_pdf
# # pyrefly: ignore [missing-import]
# from rag.splitter import split_text
# import os
# import shutil
# from database import chats_collection
# from bson import ObjectId
# # pyrefly: ignore [missing-import]
# import cloudinary
# import cloudinary.uploader
# # import cloudinary_config
# CURRENT_IMAGE = None

# router = APIRouter()

# UPLOAD_FOLDER = "uploads"

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# @router.post("/upload")

# async def upload_pdf(
#     chat_id: str,
#     file: UploadFile = File(...),
#     user_id: str = Depends(get_current_user)
#         ):
#     print("=== upload endpoint entered ===")
#     # Upload PDF to Cloudinary
#     result = cloudinary.uploader.upload(
#         file.file,
#         resource_type="raw",
#         folder="chat-pdfs"
#     )
#     print("File uploaded into cloud at upload",result["secure_url"])
#     pdf_url = result["secure_url"]
#     public_id = result["public_id"]

#     # Reset file pointer so we can read it again
#     file.file.seek(0)

#     # Save temporarily for text extraction
#     os.makedirs("temp", exist_ok=True)
#     temp_path = os.path.join("temp", file.filename)

#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Save Cloudinary information in MongoDB
#     chats_collection.update_one(
#         {"_id": ObjectId(chat_id)},
#         {
#             "$set": {
#                 "pdf_url": pdf_url,
#                 "pdf_public_id": public_id
#             }
#         }
#     )

#     # Extract text for RAG
#     text = extract_text_from_pdf(temp_path)
#     print(text)

#     chunks = split_text(text)

#     get_vector_store().add_texts(
#         texts=chunks,
#         metadatas=[
#             {
#                 "chat_id": chat_id,
#                 "user_id": user_id,
#                 "source": file.filename
#             }
#             for _ in chunks
#         ]
#     )

#     print("Saved to Chroma")

#     # Delete temporary file
#     os.remove(temp_path)

#     return {
#         "message": "File uploaded successfully",
#         "filename": file.filename,
#         "pdf_url": pdf_url
#     }



# @router.post("/upload-image")
# async def upload_image(
#     chat_id: str,
#     file: UploadFile = File(...)
# ):

#     result = cloudinary.uploader.upload(
#         file.file,
#         folder="chat-images"
#     )
    

#     image_url = result["secure_url"]
#     public_id = result["public_id"]

#     result_db = chats_collection.update_one(
#         {"_id": ObjectId(chat_id)},
#         {
#             "$set": {
#                 "image_url": image_url,
#                 "image_public_id": public_id
#             }
#         }
#     )

#     print("Matched:", result_db.matched_count)
#     print("Modified:", result_db.modified_count)

#     return {
#         "message": "Image uploaded successfully",
#         "image_url": image_url
#     }


from Backend.routes import chat
from langchain_core.outputs import chat_result
from langchain_core.outputs import chat_result
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
# pyrefly: ignore [missing-import]
from auth.dependencies import get_current_user
# pyrefly: ignore [missing-import]
from rag.vectordb import get_vector_store
# pyrefly: ignore [missing-import]
from rag.loader import extract_text_from_pdf
# pyrefly: ignore [missing-import]
from rag.splitter import split_text
import os
import shutil
from database import chats_collection
from bson import ObjectId
# pyrefly: ignore [missing-import]
import cloudinary
import cloudinary.uploader
# import cloudinary_config
CURRENT_IMAGE = None

router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def process_pdf_in_background(temp_path: str, chat_id: str, user_id: str, filename: str):
    """Background task to extract text, chunk it, and save to Chroma without blocking response."""
    try:
        # Extract text for RAG
        text = extract_text_from_pdf(temp_path)
        print(text)

        chunks = split_text(text)

        get_vector_store().add_texts(
            texts=chunks,
            metadatas=[
                {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "source": filename
                }
                for _ in chunks
            ]
        )
        print("Saved to Chroma")

        # ✅ Mark the PDF as ready for RAG
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {
                "$set": {
                    "rag_ready": True
                }
            }
        )


        print("RAG indexing completed")
    except Exception as e:
        print(f"Error processing PDF in background: {e}")
    finally:
        # Delete temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/upload")
def upload_pdf(
    chat_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    print("=== upload endpoint entered ===")
    # Upload PDF to Cloudinary
    result = cloudinary.uploader.upload(
        file.file,
        resource_type="raw",
        folder="chat-pdfs"
    )
    print("File uploaded into cloud at upload", result["secure_url"])
    pdf_url = result["secure_url"]
    public_id = result["public_id"]

    # Reset file pointer so we can read it again
    file.file.seek(0)

    # Save temporarily for text extraction
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", file.filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save Cloudinary information in MongoDB
    result_db=chats_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {
            "$set": {
                "pdf_url": pdf_url,
                "pdf_public_id": public_id,
                "rag_ready": False
            }
        }
    )
    print("Matched:", result_db.matched_count)
    print("Modified:", result_db.modified_count)

    chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
    print(chat)
    # Offload PDF extraction and vector embedding to background tasks
    background_tasks.add_task(
        process_pdf_in_background,
        temp_path,
        chat_id,
        user_id,
        file.filename
    )

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "pdf_url": pdf_url
    }


@router.post("/upload-image")
async def upload_image(
    chat_id: str,
    file: UploadFile = File(...)
):

    result = cloudinary.uploader.upload(
        file.file,
        folder="chat-images"
    )
    
    image_url = result["secure_url"]
    public_id = result["public_id"]

    result_db = chats_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {
            "$set": {
                "image_url": image_url,
                "image_public_id": public_id
            }
        }
    )

    print("Matched:", result_db.matched_count)
    print("Modified:", result_db.modified_count)

    return {
        "message": "Image uploaded successfully",
        "image_url": image_url
    }
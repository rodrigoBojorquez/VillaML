from fastapi import APIRouter, Depends, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.application.assistant.chatbot_service import ChatbotService
from app.application.assistant.speech_service import SpeechService
from app.domain.common.system_messages import SystemMessages
from container import Container
from dependency_injector.wiring import inject, Provide
from typing import Annotated


router = APIRouter(prefix="/assistant", tags=["Asistente"])

"""
    Requests de los endpoints
"""
class ChatRequest(BaseModel):
    user_id: str
    message: str

class SentimentAnalysisRequest(BaseModel):
    user_id: str
    message: str


@router.get("/chat/{user_id}")
@inject
async def get_chat_session(
    user_id: str,
    service: Annotated[ChatbotService, Depends(Provide[Container.chatbot_service])],
):
    """
    Endpoint para obtener información de una sesión.
    """
    session_info = await service.get_chat_checkpoint(user_id)

    # return ChatResponse.parse_messages(session_info["messages"])
    return {"messages": session_info}


@router.post("/chat")
@inject
async def chat(
    request: ChatRequest,
    service: Annotated[ChatbotService, Depends(Provide[Container.chatbot_service])],
):
    """
    Endpoint para manejar conversaciones con el chatbot.
    """
    response = await service.chat(request.user_id, request.message)
    return {"response": response}


@router.post("/speech")
@inject
async def chat_speech(
    speech_service: Annotated[
        SpeechService, Depends(Provide[Container.speech_service])
    ],
    file: UploadFile,
):
    """
    Endpoint para manejar conversaciones con el chatbot a través de audio.
    """
    file_bytes = await file.read()
    text = speech_service.to_text(file_bytes)
    return {"text": text}


@router.post("/chat/stream")
@inject
async def chat_stream(
    request: ChatRequest,
    service: Annotated[ChatbotService, Depends(Provide[Container.chatbot_service])],
):
    """
    Endpoint para manejar conversaciones con el chatbot en formato streaming.
    """
    stream = service.chat_stream(request.user_id, request.message)

    # Enviar el stream como respuesta
    return StreamingResponse(
        stream,
        media_type="text/plain",
    )


@router.delete("/chat/{user_id}")
@inject
async def delete_chat(
    user_id: str,
    service: Annotated[ChatbotService, Depends(Provide[Container.chatbot_service])],
):
    """
    Endpoint para eliminar una conversación.
    """
    await service.delete_session(user_id)
    return Response(status_code=200)

@router.post("/sentiment-analysis")
@inject
async def sentiment_analysis(
    request: SentimentAnalysisRequest,
    service: Annotated[ChatbotService, Depends(Provide[Container.chatbot_service])],
):
    """
    Endpoint para realizar análisis de sentimientos.
    """
    response = await service.prompt(request.message, SystemMessages.ANALYZE_SENTIMENT_SYSTEM_MESSAGE)
    return {"response": response}

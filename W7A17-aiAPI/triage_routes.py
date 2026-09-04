from fastapi import APIRouter, Depends, Request

from errors import BAD_REQUEST, UNPROCESSABLE
from llm.schema import STUB_RESULT, Source, TriageRequest, TriageResponse
from llm.service import TriageService

router = APIRouter()


def get_triage(request: Request) -> TriageService:
    return request.app.state.triage


@router.post(
    "/tasks/triage",
    tags=["triage"],
    response_model=TriageResponse,
    summary="Triage a task description",
    description="Classifies a free-text task description into a category and an urgency. One request in, one structured answer out.",
    responses={400: BAD_REQUEST, 422: UNPROCESSABLE},
)
def triage_task(body: TriageRequest, service: TriageService = Depends(get_triage)):
    if service.stub_mode:
        return TriageResponse(**STUB_RESULT.model_dump(), source=Source.STUB)
    result, source = service.triage(body.text)
    return TriageResponse(**result.model_dump(), source=source)

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os

from src.models.database import (
    Project,
    Upload,
    Analysis,
    FeatureProposal,
    DevelopmentTask,
    ProcessingStatus,
    get_db,
)
from src.storage.file_manager import file_manager
from src.core.data_processor import DataProcessor
from src.core.feature_proposer import FeatureProposer
from src.utils.helpers import is_allowed_file

router = APIRouter(prefix="/api", tags=["api"])

data_processor = DataProcessor(file_manager)
feature_proposer = FeatureProposer()


@router.post("/projects")
async def create_project(
    name: str, description: str = "", db: Session = Depends(get_db)
):
    """Create a new project."""
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "name": project.name, "description": project.description}


@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "created_at": p.created_at,
        }
        for p in projects
    ]


@router.post("/projects/{project_id}/uploads")
async def upload_file(
    project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload a file to a project."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate file type
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Save file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    file_path = file_manager.save_upload(temp_path, file.filename, project_id)
    file_type = os.path.splitext(file.filename)[1].lstrip(".")

    # Create upload record
    upload = Upload(
        project_id=project_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    # Clean up temp file
    os.remove(temp_path)

    return {"id": upload.id, "filename": upload.filename, "status": upload.status}


@router.get("/projects/{project_id}/uploads")
async def list_uploads(project_id: int, db: Session = Depends(get_db)):
    """List all uploads for a project."""
    uploads = db.query(Upload).filter(Upload.project_id == project_id).all()
    return [
        {
            "id": u.id,
            "filename": u.filename,
            "file_type": u.file_type,
            "status": u.status,
        }
        for u in uploads
    ]


@router.post("/projects/{project_id}/analyze")
async def analyze_project(
    project_id: int,
    query: str = "What should we build next?",
    db: Session = Depends(get_db),
):
    """Analyze project data and generate feature recommendations."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create analysis record
    analysis = Analysis(project_id=project_id, query=query)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        # Process all project files
        context_text = data_processor.process_project_files(project_id)

        if not context_text.strip():
            analysis.summary = "No data available for analysis"
            analysis.status = ProcessingStatus.COMPLETED
            db.commit()
            return {"analysis_id": analysis.id, "message": "No data to analyze"}

        # Generate feature proposal
        proposal = feature_proposer.generate_proposal(context_text, query)

        if "error" in proposal:
            analysis.status = ProcessingStatus.FAILED
            db.commit()
            raise HTTPException(status_code=500, detail=proposal["error"])

        # Save feature proposal
        feature = FeatureProposal(
            analysis_id=analysis.id,
            title=proposal["title"],
            description=proposal["description"],
            justification=proposal.get("justification", ""),
            ui_changes=proposal.get("ui_changes", ""),
            data_model_changes=proposal.get("data_model_changes", ""),
            workflow_changes=proposal.get("workflow_changes", ""),
            priority=proposal.get("priority", "medium"),
        )
        db.add(feature)
        db.commit()
        db.refresh(feature)

        # Save development tasks
        for task_data in proposal.get("tasks", []):
            task = DevelopmentTask(
                feature_id=feature.id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                task_type=task_data.get("task_type", ""),
                estimated_hours=task_data.get("estimated_hours"),
            )
            db.add(task)

        analysis.summary = (
            f"Generated {len(proposal.get('tasks', []))} development tasks"
        )
        analysis.status = ProcessingStatus.COMPLETED
        db.commit()

        return {
            "analysis_id": analysis.id,
            "feature": {
                "id": feature.id,
                "title": feature.title,
                "description": feature.description,
                "justification": feature.justification,
                "ui_changes": feature.ui_changes,
                "data_model_changes": feature.data_model_changes,
                "workflow_changes": feature.workflow_changes,
                "priority": feature.priority,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "task_type": t.task_type,
                        "estimated_hours": t.estimated_hours,
                    }
                    for t in feature.tasks
                ],
            },
        }

    except Exception as e:
        analysis.status = ProcessingStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/analyses")
async def list_analyses(project_id: int, db: Session = Depends(get_db)):
    """List all analyses for a project."""
    analyses = db.query(Analysis).filter(Analysis.project_id == project_id).all()
    result = []
    for a in analyses:
        result.append(
            {
                "id": a.id,
                "query": a.query,
                "summary": a.summary,
                "status": a.status,
                "created_at": a.created_at,
            }
        )
    return result

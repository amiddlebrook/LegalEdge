"""Survey system for collecting user feedback and feature requests."""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class SurveyType(Enum):
    """Types of surveys."""
    NPS = "nps"  # Net Promoter Score
    CSAT = "csat"  # Customer Satisfaction
    CES = "ces"  # Customer Effort Score
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL_FEEDBACK = "general_feedback"
    ONBOARDING = "onboarding"
    EXIT_INTENT = "exit_intent"


class SurveyStatus(Enum):
    """Survey status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class QuestionType(Enum):
    """Question types."""
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    RATING = "rating"  # 1-5, 1-10 scale
    TEXT = "text"
    TEXTAREA = "textarea"
    NPS = "nps"  # 0-10 scale
    YES_NO = "yes_no"


@dataclass
class SurveyQuestion:
    """Survey question data structure."""
    id: str
    question_text: str
    question_type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None  # For multiple choice questions
    scale_min: Optional[int] = None  # For rating questions
    scale_max: Optional[int] = None  # For rating questions
    order: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary."""
        return {
            "id": self.id,
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "required": self.required,
            "options": self.options,
            "scale_min": self.scale_min,
            "scale_max": self.scale_max,
            "order": self.order,
            "metadata": self.metadata
        }


@dataclass
class SurveyResponse:
    """Survey response data structure."""
    id: str
    survey_id: str
    user_id: Optional[str]
    session_id: str
    responses: Dict[str, Any]  # question_id -> answer
    submitted_at: datetime
    user_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "id": self.id,
            "survey_id": self.survey_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "responses": self.responses,
            "submitted_at": self.submitted_at.isoformat(),
            "user_metadata": self.user_metadata
        }


@dataclass
class Survey:
    """Survey data structure."""
    id: str
    title: str
    description: str
    survey_type: SurveyType
    status: SurveyStatus
    questions: List[SurveyQuestion]
    target_audience: Optional[Dict[str, Any]] = None  # Targeting criteria
    display_conditions: Optional[Dict[str, Any]] = None  # When to show survey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert survey to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "survey_type": self.survey_type.value,
            "status": self.status.value,
            "questions": [q.to_dict() for q in self.questions],
            "target_audience": self.target_audience,
            "display_conditions": self.display_conditions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }


class SurveyManager:
    """Manages survey creation, distribution, and analysis."""

    def __init__(self):
        self.active_surveys: Dict[str, Survey] = {}
        self.survey_responses: Dict[str, List[SurveyResponse]] = {}

    async def create_survey(self, survey_data: Dict[str, Any], created_by: str) -> Survey:
        """Create a new survey."""
        survey_id = str(uuid.uuid4())

        questions = []
        for i, q_data in enumerate(survey_data.get("questions", [])):
            question = SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text=q_data["question_text"],
                question_type=QuestionType(q_data["question_type"]),
                required=q_data.get("required", True),
                options=q_data.get("options"),
                scale_min=q_data.get("scale_min"),
                scale_max=q_data.get("scale_max"),
                order=i,
                metadata=q_data.get("metadata")
            )
            questions.append(question)

        survey = Survey(
            id=survey_id,
            title=survey_data["title"],
            description=survey_data["description"],
            survey_type=SurveyType(survey_data["survey_type"]),
            status=SurveyStatus.DRAFT,
            questions=questions,
            target_audience=survey_data.get("target_audience"),
            display_conditions=survey_data.get("display_conditions"),
            created_at=datetime.now(),
            created_by=created_by
        )

        self.active_surveys[survey_id] = survey
        await self._save_survey(survey)
        return survey

    async def publish_survey(self, survey_id: str) -> bool:
        """Publish a survey to make it active."""
        if survey_id in self.active_surveys:
            self.active_surveys[survey_id].status = SurveyStatus.ACTIVE
            self.active_surveys[survey_id].updated_at = datetime.now()
            await self._update_survey(self.active_surveys[survey_id])
            return True
        return False

    async def get_survey_for_user(self, user_id: Optional[str], session_id: str) -> Optional[Survey]:
        """Get appropriate survey for a user."""
        # Check display conditions and targeting
        for survey in self.active_surveys.values():
            if survey.status != SurveyStatus.ACTIVE:
                continue

            # Check if user should see this survey
            if await self._should_show_survey(survey, user_id, session_id):
                return survey

        return None

    async def submit_response(self, survey_id: str, user_id: Optional[str],
                            session_id: str, responses: Dict[str, Any],
                            user_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Submit survey response."""
        if survey_id not in self.active_surveys:
            return False

        response = SurveyResponse(
            id=str(uuid.uuid4()),
            survey_id=survey_id,
            user_id=user_id,
            session_id=session_id,
            responses=responses,
            submitted_at=datetime.now(),
            user_metadata=user_metadata
        )

        if survey_id not in self.survey_responses:
            self.survey_responses[survey_id] = []

        self.survey_responses[survey_id].append(response)
        await self._save_response(response)
        return True

    async def get_survey_analytics(self, survey_id: str) -> Dict[str, Any]:
        """Get analytics for a survey."""
        if survey_id not in self.survey_responses:
            return {"response_count": 0, "completion_rate": 0}

        responses = self.survey_responses[survey_id]
        survey = self.active_surveys.get(survey_id)

        if not survey:
            return {"error": "Survey not found"}

        # Calculate analytics
        total_responses = len(responses)

        # Response rate by question
        question_responses = {}
        for question in survey.questions:
            question_id = question.id
            answers = [r.responses.get(question_id) for r in responses if question_id in r.responses]
            question_responses[question_id] = {
                "question_text": question.question_text,
                "response_count": len(answers),
                "answers": answers
            }

        # Calculate NPS if this is an NPS survey
        nps_score = None
        if survey.survey_type == SurveyType.NPS:
            nps_responses = []
            for response in responses:
                for question_id, answer in response.responses.items():
                    if survey.questions and survey.questions[0].id == question_id:
                        try:
                            nps_responses.append(int(answer))
                        except (ValueError, TypeError):
                            continue

            if nps_responses:
                promoters = sum(1 for x in nps_responses if x >= 9)
                detractors = sum(1 for x in nps_responses if x <= 6)
                nps_score = (promoters - detractors) / len(nps_responses) * 100

        return {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "total_responses": total_responses,
            "response_rate": total_responses / max(1, total_responses),  # Mock calculation
            "question_analytics": question_responses,
            "nps_score": nps_score,
            "average_completion_time": 120,  # Mock data
            "responses_over_time": await self._get_responses_over_time(responses)
        }

    async def _should_show_survey(self, survey: Survey, user_id: Optional[str], session_id: str) -> bool:
        """Determine if survey should be shown to user."""
        # Check targeting criteria
        if survey.target_audience:
            # Check user segments, usage patterns, etc.
            pass

        # Check display conditions
        if survey.display_conditions:
            # Check page views, time on site, etc.
            pass

        # Simple logic: show NPS survey to 10% of users
        if survey.survey_type == SurveyType.NPS:
            import hashlib
            user_hash = hashlib.md5((user_id or session_id).encode()).hexdigest()
            return int(user_hash[-2:], 16) % 100 < 10  # 10% of users

        return True

    async def _save_survey(self, survey: Survey):
        """Save survey to storage."""
        # In production, save to database
        survey_data = survey.to_dict()
        filepath = Path("surveys") / f"{survey.id}.json"
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(survey_data, f, indent=2)

    async def _update_survey(self, survey: Survey):
        """Update survey in storage."""
        await self._save_survey(survey)

    async def _save_response(self, response: SurveyResponse):
        """Save response to storage."""
        # In production, save to database
        response_data = response.to_dict()
        filepath = Path("surveys") / "responses" / f"{response.survey_id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Load existing responses
        existing_responses = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_responses = json.load(f)

        existing_responses.append(response_data)

        with open(filepath, 'w') as f:
            json.dump(existing_responses, f, indent=2)

    async def _get_responses_over_time(self, responses: List[SurveyResponse]) -> List[Dict[str, Any]]:
        """Get response count over time."""
        # Group responses by date
        from collections import defaultdict
        responses_by_date = defaultdict(int)

        for response in responses:
            date_str = response.submitted_at.date().isoformat()
            responses_by_date[date_str] += 1

        # Convert to list of dicts
        return [{"date": date, "count": count} for date, count in responses_by_date.items()]


# Global survey manager instance
survey_manager = SurveyManager()


class SurveyService:
    """Service for managing surveys and feedback collection."""

    @staticmethod
    async def create_nps_survey(created_by: str) -> Survey:
        """Create a Net Promoter Score survey."""
        nps_question = SurveyQuestion(
            id=str(uuid.uuid4()),
            question_text="How likely are you to recommend LegalEdge to a friend or colleague?",
            question_type=QuestionType.NPS,
            required=True,
            scale_min=0,
            scale_max=10,
            order=1
        )

        follow_up_question = SurveyQuestion(
            id=str(uuid.uuid4()),
            question_text="What is the primary reason for your score?",
            question_type=QuestionType.TEXTAREA,
            required=False,
            order=2
        )

        survey_data = {
            "title": "Net Promoter Score Survey",
            "description": "Help us understand how we can improve LegalEdge",
            "survey_type": SurveyType.NPS.value,
            "questions": [nps_question.to_dict(), follow_up_question.to_dict()]
        }

        return await survey_manager.create_survey(survey_data, created_by)

    @staticmethod
    async def create_feature_request_survey(created_by: str) -> Survey:
        """Create a feature request survey."""
        questions = [
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="What feature would you like to see added to LegalEdge?",
                question_type=QuestionType.TEXTAREA,
                required=True,
                order=1
            ),
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="How would this feature benefit your workflow?",
                question_type=QuestionType.TEXTAREA,
                required=False,
                order=2
            ),
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="How important is this feature to you?",
                question_type=QuestionType.RATING,
                required=True,
                scale_min=1,
                scale_max=5,
                order=3
            )
        ]

        survey_data = {
            "title": "Feature Request Survey",
            "description": "Share your ideas for improving LegalEdge",
            "survey_type": SurveyType.FEATURE_REQUEST.value,
            "questions": [q.to_dict() for q in questions]
        }

        return await survey_manager.create_survey(survey_data, created_by)

    @staticmethod
    async def create_onboarding_survey(created_by: str) -> Survey:
        """Create an onboarding feedback survey."""
        questions = [
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="How easy was it to get started with LegalEdge?",
                question_type=QuestionType.RATING,
                required=True,
                scale_min=1,
                scale_max=5,
                order=1
            ),
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="Which features do you find most valuable?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                required=False,
                options=["Portfolio Analysis", "Legislative Tracking", "Alerts", "Reports", "API Access"],
                order=2
            ),
            SurveyQuestion(
                id=str(uuid.uuid4()),
                question_text="What challenges did you encounter during setup?",
                question_type=QuestionType.TEXTAREA,
                required=False,
                order=3
            )
        ]

        survey_data = {
            "title": "Onboarding Experience Survey",
            "description": "Help us improve the onboarding experience",
            "survey_type": SurveyType.ONBOARDING.value,
            "questions": [q.to_dict() for q in questions],
            "target_audience": {"new_users": True, "days_since_signup": {"max": 30}}
        }

        return await survey_manager.create_survey(survey_data, created_by)

    @staticmethod
    async def get_available_surveys(user_id: Optional[str], session_id: str) -> List[Survey]:
        """Get surveys available for a user."""
        available_surveys = []

        for survey in survey_manager.active_surveys.values():
            if survey.status == SurveyStatus.ACTIVE:
                if await survey_manager._should_show_survey(survey, user_id, session_id):
                    available_surveys.append(survey)

        return available_surveys

    @staticmethod
    async def submit_survey_response(survey_id: str, user_id: Optional[str],
                                   session_id: str, responses: Dict[str, Any],
                                   user_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Submit a survey response."""
        return await survey_manager.submit_response(
            survey_id, user_id, session_id, responses, user_metadata
        )

    @staticmethod
    async def get_survey_results(survey_id: str) -> Dict[str, Any]:
        """Get survey results and analytics."""
        return await survey_manager.get_survey_analytics(survey_id)

    @staticmethod
    async def get_all_surveys() -> List[Survey]:
        """Get all surveys."""
        return list(survey_manager.active_surveys.values())


# Background task for survey processing
async def survey_processor():
    """Background task to process survey responses and trigger follow-ups."""
    while True:
        try:
            # Process NPS responses and identify detractors
            for survey in survey_manager.active_surveys.values():
                if survey.survey_type == SurveyType.NPS:
                    analytics = await survey_manager.get_survey_analytics(survey.id)
                    nps_score = analytics.get("nps_score")

                    if nps_score is not None and nps_score < 0:
                        # Trigger follow-up for detractors
                        await SurveyService._trigger_detractor_followup(survey.id)

            await asyncio.sleep(3600)  # Process hourly

        except Exception as e:
            logger.error(f"Error in survey processor: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retry

    @staticmethod
    async def _trigger_detractor_followup(survey_id: str):
        """Trigger follow-up actions for NPS detractors."""
        # In production, this would:
        # 1. Send email to support team
        # 2. Schedule follow-up call
        # 3. Create support ticket
        # 4. Trigger outreach sequence
        pass

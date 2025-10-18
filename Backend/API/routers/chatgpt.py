"""
ChatGPT API Router

Endpoints for AI-powered recommendations and analysis.
Provides access to ChatGPT service for fantasy football insights.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from services.chatgpt_service import chatgpt_service


router = APIRouter()


# --- Request/Response Models ---
class LineupRecommendationRequest(BaseModel):
    team_roster: List[Dict[str, Any]]
    opponent_data: Dict[str, Any]
    league_settings: Dict[str, Any]


class DraftSuggestionRequest(BaseModel):
    available_players: List[Dict[str, Any]]
    current_roster: List[Dict[str, Any]]
    draft_position: int
    league_settings: Dict[str, Any]


class PlayerAnalysisRequest(BaseModel):
    player_id: str
    historical_stats: Dict[str, Any]
    upcoming_matchup: Dict[str, Any]


class TradeEvaluationRequest(BaseModel):
    giving_players: List[Dict[str, Any]]
    receiving_players: List[Dict[str, Any]]
    team_context: Dict[str, Any]


class MatchupPredictionRequest(BaseModel):
    team_a: Dict[str, Any]
    team_b: Dict[str, Any]
    week_context: Dict[str, Any]


class SeasonStrategyRequest(BaseModel):
    current_team: Dict[str, Any]
    league_standings: List[Dict[str, Any]]
    weeks_remaining: int


# --- Endpoints ---
@router.post("/lineup/recommendations")
async def get_lineup_recommendations(request: LineupRecommendationRequest) -> Dict[str, Any]:
    """
    Get AI-powered lineup recommendations based on roster and matchup data.
    """
    try:
        return chatgpt_service.get_lineup_recommendations(
            team_roster=request.team_roster,
            opponent_data=request.opponent_data,
            league_settings=request.league_settings
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lineup recommendations: {str(e)}"
        )


@router.post("/draft/suggestions")
async def get_draft_suggestions(request: DraftSuggestionRequest) -> Dict[str, Any]:
    """
    Get AI-powered draft pick suggestions based on available players and strategy.
    """
    try:
        return chatgpt_service.suggest_draft_picks(
            available_players=request.available_players,
            current_roster=request.current_roster,
            draft_position=request.draft_position,
            league_settings=request.league_settings
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating draft suggestions: {str(e)}"
        )


@router.post("/player/{player_id}/analysis")
async def analyze_player_performance(player_id: str, request: PlayerAnalysisRequest) -> Dict[str, Any]:
    """
    Generate comprehensive AI analysis of player performance and outlook.
    """
    try:
        return chatgpt_service.analyze_player_performance(
            player_id=player_id,
            historical_stats=request.historical_stats,
            upcoming_matchup=request.upcoming_matchup
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing player performance: {str(e)}"
        )


@router.post("/trade/evaluation")
async def evaluate_trade_proposal(request: TradeEvaluationRequest) -> Dict[str, Any]:
    """
    Evaluate trade proposals using AI analysis of player values and team fit.
    """
    try:
        return chatgpt_service.evaluate_trade_proposal(
            giving_players=request.giving_players,
            receiving_players=request.receiving_players,
            team_context=request.team_context
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating trade proposal: {str(e)}"
        )


@router.post("/matchup/prediction")
async def predict_matchup_outcome(request: MatchupPredictionRequest) -> Dict[str, Any]:
    """
    Predict head-to-head matchup outcomes with AI analysis.
    """
    try:
        return chatgpt_service.predict_matchup_outcome(
            team_a=request.team_a,
            team_b=request.team_b,
            week_context=request.week_context
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting matchup outcome: {str(e)}"
        )


@router.post("/strategy/season")
async def generate_season_strategy(request: SeasonStrategyRequest) -> Dict[str, Any]:
    """
    Generate comprehensive season strategy recommendations.
    """
    try:
        return chatgpt_service.generate_season_strategy(
            current_team=request.current_team,
            league_standings=request.league_standings,
            weeks_remaining=request.weeks_remaining
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating season strategy: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check ChatGPT service health and connectivity."""
    return {
        "status": "healthy",
        "service": "ChatGPT API Integration",
        "version": "1.0.0"
    }
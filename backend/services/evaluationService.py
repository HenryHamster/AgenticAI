"""
Evaluation Service for Game User Responses

This service retrieves game data from the database and evaluates user responses
using the evaluation system.
"""

from typing import Dict, List, Optional, Any
from schema.gameModel import GameModel
from schema.turnModel import TurnModel
from services.database.gameService import load_game_from_database
from services.database.turnService import get_turns_by_game_id
from eval import quick_evaluate, EvalWrapper


class GameEvaluationService:
    """Service for evaluating user responses in games"""
    
    def __init__(self, evaluation_service_type: str = "mock"):
        """
        Initialize the evaluation service
        
        Args:
            evaluation_service_type: Type of evaluation service ("mock", "custom")
        """
        self.evaluation_service_type = evaluation_service_type
    
    def evaluate_game_responses(self, game_id: str) -> Dict[str, Any]:
        """
        Evaluate all user responses for a specific game
        
        Args:
            game_id: The game ID to evaluate
            
        Returns:
            Dictionary containing evaluation results for all turns and players
        """
        try:
            # Load game data
            game = load_game_from_database(game_id)
            if not game:
                return {"error": f"Game {game_id} not found"}
            
            # Get all turns for the game
            turns = get_turns_by_game_id(game_id)
            if not turns:
                return {"error": f"No turns found for game {game_id}"}
            
            # Evaluate responses for each turn
            evaluation_results = {
                "game_id": game_id,
                "game_name": game.name,
                "total_turns": len(turns),
                "evaluations": []
            }
            
            for turn in turns:
                turn_evaluation = self._evaluate_turn_responses(turn)
                evaluation_results["evaluations"].append(turn_evaluation)
            
            # Calculate overall statistics
            evaluation_results["overall_stats"] = self._calculate_overall_stats(
                evaluation_results["evaluations"]
            )
            
            return evaluation_results
            
        except Exception as e:
            return {"error": f"Failed to evaluate game: {str(e)}"}
    
    def evaluate_single_turn(self, game_id: str, turn_number: int) -> Dict[str, Any]:
        """
        Evaluate user responses for a specific turn
        
        Args:
            game_id: The game ID
            turn_number: The turn number to evaluate
            
        Returns:
            Dictionary containing evaluation results for the specific turn
        """
        try:
            turns = get_turns_by_game_id(game_id)
            target_turn = None
            
            for turn in turns:
                if turn.turn_number == turn_number:
                    target_turn = turn
                    break
            
            if not target_turn:
                return {"error": f"Turn {turn_number} not found for game {game_id}"}
            
            return self._evaluate_turn_responses(target_turn)
            
        except Exception as e:
            return {"error": f"Failed to evaluate turn: {str(e)}"}
    
    def evaluate_player_responses(self, game_id: str, player_uid: str) -> Dict[str, Any]:
        """
        Evaluate all responses from a specific player
        
        Args:
            game_id: The game ID
            player_uid: The player UID to evaluate
            
        Returns:
            Dictionary containing evaluation results for the specific player
        """
        try:
            turns = get_turns_by_game_id(game_id)
            player_evaluations = []
            
            for turn in turns:
                if player_uid in turn.game_state.player_responses:
                    response = turn.game_state.player_responses[player_uid]
                    environment = self._get_environment_context(turn)
                    
                    evaluation = quick_evaluate(
                        environment_text=environment,
                        user_response_text=response,
                        service_type=self.evaluation_service_type
                    )
                    
                    player_evaluations.append({
                        "turn_number": turn.turn_number,
                        "response": response,
                        "evaluation": evaluation
                    })
            
            return {
                "game_id": game_id,
                "player_uid": player_uid,
                "total_responses": len(player_evaluations),
                "evaluations": player_evaluations,
                "player_stats": self._calculate_player_stats(player_evaluations)
            }
            
        except Exception as e:
            return {"error": f"Failed to evaluate player responses: {str(e)}"}
    
    def _evaluate_turn_responses(self, turn: TurnModel) -> Dict[str, Any]:
        """Evaluate all responses in a single turn"""
        turn_evaluation = {
            "turn_number": turn.turn_number,
            "player_evaluations": {},
            "turn_stats": {}
        }
        
        # Get environment context for this turn
        environment = self._get_environment_context(turn)
        
        # Evaluate each player's response
        for player_uid, response in turn.game_state.player_responses.items():
            evaluation = quick_evaluate(
                environment_text=environment,
                user_response_text=response,
                service_type=self.evaluation_service_type,
                ai_model="gpt-4.1-nano",
            )
            
            turn_evaluation["player_evaluations"][player_uid] = {
                "response": response,
                "evaluation": evaluation
            }
        
        # Calculate turn statistics
        turn_evaluation["turn_stats"] = self._calculate_turn_stats(
            turn_evaluation["player_evaluations"]
        )
        
        return turn_evaluation
    
    def _get_environment_context(self, turn: TurnModel) -> str:
        """Extract environment context from turn data"""
        context_parts = []
        
        # Add dungeon master verdict if available
        if turn.game_state.dungeon_master_verdict:
            context_parts.append(f"Dungeon Master: {turn.game_state.dungeon_master_verdict}")
        
        # Add narrative result if available
        if turn.game_state.narrative_result:
            context_parts.append(f"Narrative: {turn.game_state.narrative_result}")
        
        # Add world state if available
        if turn.game_state.world_state_change:
            world_state = turn.game_state.world_state_change
            context_parts.append(f"World State: {world_state}")
        
        # Add character states if available
        if turn.game_state.character_state_change:
            for char_state in turn.game_state.character_state_change:
                context_parts.append(f"Character State: {char_state}")
        
        return " | ".join(context_parts) if context_parts else "Game environment context"
    
    def _calculate_turn_stats(self, player_evaluations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for a single turn"""
        if not player_evaluations:
            return {"average_score": 0.0, "total_players": 0}
        
        scores = []
        for player_data in player_evaluations.values():
            evaluation = player_data["evaluation"]
            if "score" in evaluation:
                scores.append(evaluation["score"])
        
        return {
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "total_players": len(player_evaluations),
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0
        }
    
    def _calculate_player_stats(self, player_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a specific player"""
        if not player_evaluations:
            return {"average_score": 0.0, "total_responses": 0}
        
        scores = []
        for eval_data in player_evaluations:
            evaluation = eval_data["evaluation"]
            if "score" in evaluation:
                scores.append(evaluation["score"])
        
        return {
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "total_responses": len(player_evaluations),
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "score_trend": scores  # For trend analysis
        }
    
    def _calculate_overall_stats(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall statistics for the entire game"""
        all_scores = []
        total_responses = 0
        
        for turn_eval in evaluations:
            turn_stats = turn_eval.get("turn_stats", {})
            if "average_score" in turn_stats:
                all_scores.append(turn_stats["average_score"])
            total_responses += turn_stats.get("total_players", 0)
        
        return {
            "overall_average_score": sum(all_scores) / len(all_scores) if all_scores else 0.0,
            "total_responses_evaluated": total_responses,
            "total_turns": len(evaluations),
            "score_trend": all_scores
        }


# Convenience functions for quick access
def evaluate_game_responses(game_id: str, service_type: str = "mock") -> Dict[str, Any]:
    """Quick function to evaluate all responses in a game"""
    service = GameEvaluationService(service_type)
    return service.evaluate_game_responses(game_id)


def evaluate_turn_responses(game_id: str, turn_number: int, service_type: str = "mock") -> Dict[str, Any]:
    """Quick function to evaluate responses in a specific turn"""
    service = GameEvaluationService(service_type)
    return service.evaluate_single_turn(game_id, turn_number)


def evaluate_player_responses(game_id: str, player_uid: str, service_type: str = "mock") -> Dict[str, Any]:
    """Quick function to evaluate responses from a specific player"""
    service = GameEvaluationService(service_type)
    return service.evaluate_player_responses(game_id, player_uid)

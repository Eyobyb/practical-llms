from typing import Tuple

from sherpa_ai.events import EventType
from sherpa_ai.memory import Belief
from sherpa_ai.output_parsers.base import BaseOutputProcessor
from sherpa_ai.output_parsers.validation_result import ValidationResult
from sherpa_ai.utils import TextSimilarityState, check_entities_match


class EntityValidation(BaseOutputProcessor):
    """
     Process and validate the presence of entities in the generated text.

    This class inherits from the BaseOutputProcessor and provides a method to process
    the generated text and validate the presence of entities based on a specified source.

    Methods:
    - process_output(text: str, belief: Belief) -> ValidationResult:
        Process the generated text and validate the presence of entities.

    - get_failure_message() -> str:
        Returns a failure message to be displayed when the validation fails.

    """

    def process_output(
        self, text: str, belief: Belief, iteration_count: int = 1
    ) -> ValidationResult:
        """
        Verifies that entities within `text` exist in the `belief` source text.
        Args:
            text: The text to be processed
            belief: The belief object of the agent that generated the output
            iteration_count (int, optional): The iteration count for validation processing. Defaults to 1.
        Returns:
            ValidationResult: The result of the validation. If any entity in the
            text to be processed doesn't exist in the source text,
            validation is invalid and contains a feedback string.
            Otherwise, validation is valid.
        """
        source = belief.get_histories_excluding_types(
            exclude_types=[EventType.feedback, EventType.result],
        )
        entity_exist_in_source, error_message = check_entities_match(
            text, source, self.similarity_picker(iteration_count)
        )
        if entity_exist_in_source:
            return ValidationResult(
                is_valid=True,
                result=text,
                feedback="",
            )
        else:
            return ValidationResult(
                is_valid=False,
                result=text,
                feedback=error_message,
            )

    def similarity_picker(self, value: int):
        """
        Picks a text similarity state based on the provided iteration count value.

        Args:
            value (int): The iteration count value used to determine the text similarity state.
                        - 0: Use BASIC text similarity.
                        - 1: Use text similarity BY_METRICS.
                        - Default: Use text similarity BY_LLM.

        Returns:
            TextSimilarityState: The selected text similarity state.
        """
        switch_dict = {0: TextSimilarityState.BASIC, 1: TextSimilarityState.BY_METRICS}
        return switch_dict.get(value, TextSimilarityState.BY_LLM)

    def get_failure_message(self) -> str:
        return "Some enitities from the source might not be mentioned."

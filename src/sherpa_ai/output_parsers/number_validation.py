from typing import Tuple

from sherpa_ai.memory import Belief
from sherpa_ai.output_parsers.base import BaseOutputProcessor


class CitationValidation(BaseOutputProcessor):
    def __init__(
        self,
        agent_belief: Belief,
    ):
        # threshold
        self.agent_belief = agent_belief

    def process_output(self, text: str) -> Tuple[bool, str]:
        # TODO: Implement the number validation, return True and the text
        # if the text is valid. Return false and the message if the text is invalid.
        pass

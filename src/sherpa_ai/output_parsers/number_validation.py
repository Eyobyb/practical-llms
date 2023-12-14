from typing import Tuple

from sherpa_ai.memory import Belief
from sherpa_ai.output_parsers.base import BaseOutputProcessor
from sherpa_ai.utils import check_if_number_exist


class NumberValidation(BaseOutputProcessor):
    def __init__(
        self,
        agent_belief: Belief,
    ):
        # threshold

        self.agent_belief = agent_belief
        self.source_text = ""
    def process_output(self, text: str) -> Tuple[bool, str]:
        # TODO: Implement the number validation, return True and the text
        # if the text is valid. Return false and the message if the text is invalid.
        check_validation = check_if_number_exist( text ,self.source_text)
        if check_validation['number_exists']==True:
            return True, text
        else:
            return False , check_validation['messages']

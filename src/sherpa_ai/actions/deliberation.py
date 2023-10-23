from langchain.base_language import BaseLanguageModel

from sherpa_ai.actions.base import BaseAction

DELIBERATION_DESCRIPTION = """Role Description: {role_description}
Task Description: {task}

Please deliberate on the task and generate a solution that is:

Highly Detailed: Break down components and elements clearly.
Quality-Oriented: Ensure top-notch performance and longevity.
Precision-Focused: Specific measures, materials, or methods to be used.

Keep the result concise and short. No more than one paragraph.

"""  # noqa: E501


class Deliberation(BaseAction):
    def __init__(
        self,
        role_description: str,
        llm: BaseLanguageModel,
        description: str = DELIBERATION_DESCRIPTION,
    ):
        self.name = "Deliberation"
        self.role_description = role_description
        self.description = description
        self.llm = llm

    def execute(self, task: str) -> str:
        prompt = self.description.format(
            task=task, role_description=self.role_description
        )

        result = self.llm.predict(prompt)

        return result

    def __str__(self):
        return self.name + ": task(string)"

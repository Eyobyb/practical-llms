from langchain.chat_models.base import BaseChatModel

from sherpa_ai.agents.agent_pool import AgentPool
from sherpa_ai.agents.base import BaseAgent

DESCRIPTION_PROMPT = """
You are a Critic agent that receive a plan from the planner to execuate a task from user.
Your goal is to output the 10 most necessary feedback given the corrent plan to solve the task.
"""
IMPORTANCE_PROMPT = """The plan you should be necessary and important to complete the task.
Evaluate if the content of plan and selected actions/ tools are important and necessary.
Output format:
Score: <Integer score from 1 - 10>
Evaluation: <evaluation in text>
Do not include other text in your resonse.
Output:
"""
DETAIL_PROMPT = """The plan you should be detailed enough to complete the task.
Evaluate if the content of plan and selected actions/ tools contains all the details the task needed.
Output format:
Score: <Integer score from 1 - 10>
Evaluation: <evaluation in text>
Do not include other text in your resonse.
Output:
"""
INSIGHT_PROMPT = """
What are the top 5 high-level insights you can infer from the all the memory you have?
Only output insights with high confidence.
Insight: 
"""
FEEDBACK_PROMPT = """
What are the 10 most important feedback for the plan received from the planner, using the\
insight you have from current observation, evaluation using the importance matrices and detail matrices.
Feedback: 
"""


class Critic(BaseAgent):
    """
    The critic agent receives a plan from the planner and evaluate the plan based on
    some pre-defined metrics. At the same time, it gives the feedback to the planner.
    """

    def __init__(
        self,
        name: str,
        llm: BaseChatModel,
        description=DESCRIPTION_PROMPT,
        shared_memory=None,
        belief=None,
        action_selector=None,
        num_runs=1,
        ratio: float = 1.0,
    ):
        self.llm = llm
        self.description = description
        self.shared_memory = shared_memory
        self.belief = belief
        self.ratio = ratio

    def get_importance_evaluation(self, task: str, plan: str):
        # return score in int and evaluation in string for importance matrix
        prompt = "Task: " + task + "\nPlan: " + plan + IMPORTANCE_PROMPT
        output = self.llm.predict(prompt)
        score = int(output.split("Score:")[1].split("Evaluation")[0])
        evaluation = output.split("Evaluation: ")[1]
        return score, evaluation

    def get_detail_evaluation(self, task: str, plan: str):
        # return score in int and evaluation in string for detail matrix
        prompt = "Task: " + task + "\nPlan: " + plan + DETAIL_PROMPT
        output = self.llm.predict(prompt)
        score = int(output.split("Score:")[1].split("Evaluation")[0])
        evaluation = output.split("Evaluation: ")[1]
        return score, evaluation

    def get_insight(self):
        # return a list of string: top 5 important insight given the belief and memory (observation)
        observation = self.observe(self.belief)
        prompt = "Observation: " + observation + "\n" + INSIGHT_PROMPT
        result = self.llm.predict(prompt)
        insights = [i for i in result.split("\n") if len(i.strip()) > 0][:5]
        return insights

    def post_process(self, feedback: str):
        return [i for i in feedback.split("\n") if i]

    def get_feedback(self, task: str, plan: str):
        # take plan, result of evaluation (importance, detail), insight, belief, observation, and generate top 10 feedback
        # observation = self.observe(self.belief)
        i_score, i_evaluation = self.get_importance_evaluation(task, plan)
        d_score, d_evaluation = self.get_detail_evaluation(task, plan)
        # approve or not, check score/ ratio
        # insights = self.get_insight()
        if i_score <= 10 * self.ratio or d_score <= 10 * self.ratio:
            prompt = (
                # f"\nCurrent observation you have is: {observation}"
                # f"Insight you have from current observation: {insights}"
                f"Evaluation in the importance matrices: {i_evaluation}"
                f"Evaluation in the detail matrices: {d_evaluation}" + FEEDBACK_PROMPT
            )
            feedback = self.llm.predict(self.description + FEEDBACK_PROMPT + prompt)
            return self.post_process(feedback)
        else:
            return ""
